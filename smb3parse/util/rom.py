from ctypes import Structure, c_char, c_ubyte
from smb3parse.util import little_endian
from smb3parse.constants import BASE_OFFSET


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

    @property
    def prg_size(self):
        return self.prg_units * INESHeader.PRG_UNIT_SIZE

    @property
    def chr_size(self):
        return self.chr_units * INESHeader.CHR_UNIT_SIZE


class Rom:
    VANILLA_PRG_SIZE = 0x40000

    def __init__(self, rom_data: bytearray, header: INESHeader):
        self._data = rom_data
        self._header = header

    def prg_normalize(self, offset: int) -> int:
        """Takes a vanilla ROM PRG offset and returns a
        new offset that is correct for the current ROM's
        PRG size

        IMPORTANT: This method is not idempotent! You cannot
        call this multiple times giving it resulting offsets
        from previous calls to it.
        """
        # data in expanded Roms is inserted between PRG29 and PRG30
        # (0-indexed); so any offset, that goes beyond PRG29 needs
        # to be adjusted by adding however much data was inserted
        if offset < (BASE_OFFSET + (30 * 0x2000)):
            return offset

        # we need to normalize this bank 30 or 31 or CHR
        # offset to the correct bank based on PRG size
        no_bytes_added_to_rom = self._header.prg_size - Rom.VANILLA_PRG_SIZE
        return offset + no_bytes_added_to_rom

    def little_endian(self, offset: int) -> int:
        offset = self.prg_normalize(offset)
        return little_endian(self._data[offset : offset + 2])

    def write_little_endian(self, offset: int, integer: int):
        offset = self.prg_normalize(offset)
        right_byte = (integer & 0xFF00) >> 8
        left_byte = integer & 0x00FF

        self.write(offset, bytes([left_byte, right_byte]))

    def read(self, offset: int, length: int) -> bytes:
        offset = self.prg_normalize(offset)
        return self._data[offset : offset + length]

    def write(self, offset: int, data: bytes):
        offset = self.prg_normalize(offset)
        self._data[offset : offset + len(data)] = data

    def find(self, byte: bytes, offset: int = 0) -> int:
        return self._data.find(byte, offset)

    def int(self, offset: int) -> int:
        read_bytes = self.read(offset, 1)

        return read_bytes[0]

    def save_to(self, path: str):
        with open(path, "wb") as file:
            file.write(self._data)
