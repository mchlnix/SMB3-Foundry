import pathlib
from ctypes import Structure, c_char, c_ubyte
from os import PathLike
from pathlib import Path
from typing import Optional, Union, cast

from smb3parse.constants import BASE_OFFSET, PAGE_A000_ByTileset, WORLD_MAP_TSA_INDEX
from smb3parse.util import little_endian

TSA_OS_LIST = PAGE_A000_ByTileset
TSA_TABLE_SIZE = 0x400

PRG_BANK_SIZE = 0x2000


class NormalizedAddress(int):
    """Type class used to inform Rom.prg_normalize that an address is already normalized."""

    def __new__(cls, val: int):
        result = super(NormalizedAddress, cls).__new__(cls, val)
        return cast(NormalizedAddress, result)


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

    def prg_normalize(self, offset: int) -> NormalizedAddress:
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

    def little_endian(self, offset: int) -> int:
        offset = self.prg_normalize(offset)
        return little_endian(self._data[offset : offset + 2])

    def write_little_endian(self, offset: int, integer: int):
        offset = self.prg_normalize(offset)
        right_byte = (integer & 0xFF00) >> 8
        left_byte = integer & 0x00FF

        self.write(offset, bytes([left_byte, right_byte]))

    def read(self, offset: int, length: int) -> bytearray:
        offset = self.prg_normalize(offset)
        return self._data[offset : offset + length]

    def read_until(self, offset, delimiter):
        end = self.find(delimiter, offset)

        return self.read(offset, end - offset)

    def write(self, offset: int, data: Union[bytes, int]):
        if isinstance(data, int):
            data = bytes([data])

        offset = self.prg_normalize(offset)
        self._data[offset : offset + len(data)] = data

    def find(self, byte: bytes, offset: int = 0) -> int:
        return self._data.find(byte, offset)

    def nibbles(self, offset: int) -> tuple[int, int]:
        byte = self.int(offset)

        high_nibble = byte >> 4
        low_nibble = byte & 0x0F

        return high_nibble, low_nibble

    def write_nibbles(self, offset: int, high_nibble: int, low_nibble: int = 0):
        if any(nibble > 0x0F for nibble in [high_nibble, low_nibble]):
            raise ValueError(f"{high_nibble=} or {low_nibble=} was larger than 0x0F.")

        byte = (high_nibble << 4) + low_nibble

        self.write(offset, byte)

    @staticmethod
    def from_file(path: PathLike):
        return Rom(bytearray(pathlib.Path(path).read_bytes()))

    def save_to(self, path: PathLike):
        Path(path).open("wb").write(self._data)

    def int(self, offset: int) -> int:
        read_bytes = self.read(offset, 1)

        return read_bytes[0]
