import pathlib
from ctypes import Structure, c_char, c_ubyte
from os import PathLike
from pathlib import Path
from typing import Optional, Union

from typing_extensions import TypeAlias

from smb3parse.constants import BASE_OFFSET, PAGE_A000_ByTileset, WORLD_MAP_TSA_INDEX
from smb3parse.util import little_endian

TSA_OS_LIST = PAGE_A000_ByTileset
TSA_TABLE_SIZE = 0x400

PRG_BANK_SIZE = 0x2000


RawAddress: TypeAlias = int


class NormalizedAddress(RawAddress):
    """
    Roms can be expanded to hold more data than the original SMB3 game. This data is added between PRG_029 and PRG_030.

    This makes it necessary to reroute any address, that would've gone to the old PRG_030 and PRG_031 to the new PRG_030
    and PRG_031.

    Since this cannot happen twice, without exceeding the size of the Rom, we have to keep track of which addresses have
    already been normalized.

    This is done using these types and a type checker, as well as only having 3 methods in the Rom class dealing with
    raw Rom data. _read, _write and _find. Any other method using these must normalize their addresses and not give them
    out.
    """

    pass


AnyAddress: TypeAlias = Union[RawAddress, NormalizedAddress]


class INESHeader(Structure):
    _fields_ = [
        ("magic", c_char * 4),
        ("prg_units", c_ubyte),
        ("chr_units", c_ubyte),
        ("flags6", c_char),
        ("unused_flags", c_char * 4),
        ("unused_pad", c_char * 5),
    ]
    PRG_UNIT_SIZE = 0x4000
    CHR_UNIT_SIZE = 0x2000
    LENGTH = 0x10

    @property
    def prg_size(self):
        return self.prg_units * INESHeader.PRG_UNIT_SIZE

    @property
    def chr_size(self):
        return self.chr_units * INESHeader.CHR_UNIT_SIZE


class Rom:
    VANILLA_PRG_SIZE = 0x40000

    def __init__(self, rom_data: bytearray, header: Optional[INESHeader] = None):
        self._data = rom_data

        if header is None:
            header = INESHeader.from_buffer_copy(bytes(rom_data))

        self._header = header

    @property
    def prg_units(self):
        return self._header.prg_units

    @property
    def prg_banks(self):
        return self.prg_units * 2

    def prg_normalize(self, offset: AnyAddress) -> NormalizedAddress:
        """Takes a vanilla ROM PRG offset and returns a
        new offset that is correct for the current ROM's
        PRG size

        IMPORTANT: This method is not idempotent! You cannot
        call this multiple times giving it resulting offsets
        from previous calls to it.
        """
        if isinstance(offset, NormalizedAddress):
            return offset

        # data in expanded Roms is inserted between PRG29 and PRG30
        # (0-indexed); so any offset, that goes beyond PRG29 needs
        # to be adjusted by adding however much data was inserted
        if offset < (BASE_OFFSET + (30 * PRG_BANK_SIZE)):
            return NormalizedAddress(offset)

        # we need to normalize this bank 30 or 31 or CHR
        # offset to the correct bank based on PRG size
        no_bytes_added_to_rom = self._header.prg_size - Rom.VANILLA_PRG_SIZE

        return NormalizedAddress(offset + no_bytes_added_to_rom)

    def tsa_data_for_object_set(self, object_set: int) -> bytearray:
        # TSA_OS_LIST offset value assumes vanilla ROM size, so normalize it

        tsa_index = self.int(TSA_OS_LIST + object_set)

        if object_set == 0:
            # Note that for the World Map, PAGE_A000 is set to bank 11, but
            # the actual drawing of the map and the map tiles are defined
            # in bank 12. prg030.asm handles swapping hard-coded to bank 12
            # and drawing the initial map via Map_Reload_with_Completions.
            # Therefore, the PAGE_A000_ByTileset doesn't have the TSA data for
            # the map tiles.
            tsa_index = WORLD_MAP_TSA_INDEX

        # INES header size + (bank with tsa data * sizeof(bank))
        tsa_start = BASE_OFFSET + tsa_index * PRG_BANK_SIZE

        return self.read(tsa_start, TSA_TABLE_SIZE)

    def little_endian(self, offset: AnyAddress) -> int:
        return little_endian(self.read(offset, 2))

    def write_little_endian(self, offset: AnyAddress, integer: int):
        right_byte = (integer & 0xFF00) >> 8
        left_byte = integer & 0x00FF

        self.write(offset, bytes([left_byte, right_byte]))

    def read(self, offset: AnyAddress, length: int) -> bytearray:
        offset = self.prg_normalize(offset)

        return self._read(offset, length)

    def _read(self, offset: NormalizedAddress, length: int) -> bytearray:
        return self._data[offset : offset + length]

    def read_until(self, offset: AnyAddress, delimiter: Union[bytes, int]):
        if isinstance(delimiter, int):
            delimiter = bytes([delimiter])

        end = self.find(delimiter, offset)

        return self.read(offset, end - offset)

    def write(self, offset: AnyAddress, data: Union[bytes, int]):
        if isinstance(data, int):
            data = bytes([data])

        offset = self.prg_normalize(offset)

        return self._write(offset, data)

    def _write(self, offset: NormalizedAddress, data: bytes):
        self._data[offset : offset + len(data)] = data

    def find(self, needle: Union[bytes, int], start: AnyAddress = 0, end: AnyAddress = -1) -> NormalizedAddress:
        if isinstance(needle, int):
            needle = bytes([needle])

        start = self.prg_normalize(start)

        if end == -1:
            end = len(self._data)

        end = self.prg_normalize(end)

        return self._find(needle, start, end)

    def _find(self, needle: bytes, start: NormalizedAddress, end: NormalizedAddress) -> NormalizedAddress:
        return NormalizedAddress(self._data.find(needle, start, end))

    def nibbles(self, offset: AnyAddress) -> tuple[int, int]:
        byte = self.int(offset)

        high_nibble = byte >> 4
        low_nibble = byte & 0x0F

        return high_nibble, low_nibble

    def write_nibbles(self, offset: AnyAddress, high_nibble: int, low_nibble: int = 0):
        if any(nibble > 0x0F for nibble in [high_nibble, low_nibble]):
            raise ValueError(f"{high_nibble=} or {low_nibble=} was larger than 0x0F.")

        byte = (high_nibble << 4) + low_nibble

        self.write(offset, byte)

    @staticmethod
    def from_file(path: PathLike):
        return Rom(bytearray(pathlib.Path(path).read_bytes()))

    def save_to(self, path: PathLike):
        Path(path).open("wb").write(self._data)

    def int(self, offset: AnyAddress) -> int:
        read_bytes = self.read(offset, 1)

        return read_bytes[0]
