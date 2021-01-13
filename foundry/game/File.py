from ctypes import Structure, sizeof, addressof, memmove, c_char, c_ubyte
from os.path import basename
from typing import List, Optional

from smb3parse.constants import BASE_OFFSET, PAGE_A000_ByTileset
from smb3parse.util.rom import Rom

WORLD_COUNT = 9  # includes warp zone

# W = WORLD_MAP
# OS = OFFSET

OS_SIZE = 2  # byte

TSA_OS_LIST = PAGE_A000_ByTileset
TSA_TABLE_SIZE = 0x400
TSA_TABLE_INTERVAL = TSA_TABLE_SIZE + 0x1C00


class _INESHdr(Structure):
    _fields_ = [
        ("magic", c_char * 4),
        ("prg_units", c_ubyte),
        ("chr_units", c_ubyte),
        ("flags6", c_char),
        ("unused_flags", c_char * 4),
        ("unused_pad", c_char * 5)
    ]
    PRG_UNIT_SIZE = 0x4000
    CHR_UNIT_SIZE = 0x2000

    def __init__(self, data):
        self.raw_data = data[0:sizeof(self)]
        memmove(addressof(self), data, sizeof(self))

    @property
    def prg_size(self):
        return self.prg_units * _INESHdr.PRG_UNIT_SIZE

    @property
    def chr_size(self):
        return self.chr_units * _INESHdr.CHR_UNIT_SIZE


class ROM(Rom):
    MARKER_VALUE = bytes("SMB3FOUNDRY", "ascii")

    VANILLA_PRG_SIZE = 0x40000

    rom_data = bytearray()
    header = None

    additional_data = ""

    path: str = ""
    name: str = ""

    W_INIT_OS_LIST: List[int] = []

    def __init__(self, path: Optional[str] = None):
        if not ROM.rom_data:
            if path is None:
                raise ValueError("Rom was not loaded!")

            ROM.load_from_file(path)

        super(ROM, self).__init__(ROM.rom_data)

        self.position = 0

    @staticmethod
    def prg_normalize(offset: int) -> int:
        """ Takes a vanilla ROM PRG offset and returns a
        new offset that is correct for the current ROM's
        PRG size
        """
        # Only prg030 and prg031 are modified in an expanded ROM,
        # so offsets to other banks should stay the same.
        if offset < (BASE_OFFSET + (30 * 0x2000)):
            return offset
        # Otherwise, we need to normalize this bank 30 or 31
        # offset to the last two banks based on PRG size
        return ROM.header.prg_size - (ROM.VANILLA_PRG_SIZE - offset)

    @staticmethod
    def get_tsa_data(object_set: int) -> bytes:
        rom = ROM()

        # TSA_OS_LIST offset value assumes vanilla ROM size, so normalize it
        tsa_index = rom.int(ROM.prg_normalize(TSA_OS_LIST) + object_set)

        if object_set == 0:
            # Note that for the World Map, PAGE_A000 is set to bank 11, but
            # the actual drawing of the map and the map tiles are defined
            # in bank 12. prg030.asm handles swapping hard-coded to bank 12
            # and drawing the initial map via Map_Reload_with_Completions.
            # Therefore, the PAGE_A000_ByTileset doesn't have the TSA data for
            # the map tiles.
            tsa_index = 12

        # INES header size + (bank with tsa data * sizeof(bank))
        tsa_start = BASE_OFFSET + tsa_index * TSA_TABLE_INTERVAL

        return bytes(rom.read(tsa_start, TSA_TABLE_SIZE))

    @staticmethod
    def load_from_file(path: str):
        with open(path, "rb") as rom:
            data = bytearray(rom.read())

        ROM.header = _INESHdr(bytes(data))
        ROM.path = path
        ROM.name = basename(path)

        additional_data_start = data.find(ROM.MARKER_VALUE)

        if additional_data_start == -1:
            ROM.rom_data = data
            ROM.additional_data = ""
        else:
            ROM.rom_data = data[:additional_data_start]

            additional_data_start += len(ROM.MARKER_VALUE)

            ROM.additional_data = data[additional_data_start:].decode("utf-8")

    @staticmethod
    def save_to_file(path: str, set_new_path=True):
        with open(path, "wb") as f:
            f.write(bytearray(ROM.rom_data))

        if ROM.additional_data:
            with open(path, "ab") as f:
                f.write(ROM.MARKER_VALUE)
                f.write(ROM.additional_data.encode("utf-8"))

        if set_new_path:
            ROM.path = path
            ROM.name = basename(path)

    @staticmethod
    def set_additional_data(additional_data):
        ROM.additional_data = additional_data

    @staticmethod
    def is_loaded() -> bool:
        return bool(ROM.path)

    def seek(self, position: int) -> int:
        if position > len(ROM.rom_data) or position < 0:
            return -1

        self.position = position

        return 0

    def get_byte(self, position: int = -1) -> int:
        if position >= 0:
            k = self.seek(position) >= 0
        else:
            k = self.position < len(ROM.rom_data)

        if k:
            return_byte = ROM.rom_data[self.position]
        else:
            return_byte = 0

        self.position += 1

        return return_byte

    def peek_byte(self, position: int = -1) -> int:
        old_position = self.position

        byte = self.get_byte(position)

        self.position = old_position

        return byte

    def bulk_read(self, count: int, position: int = -1) -> bytearray:
        if position >= 0:
            self.seek(position)
        else:
            position = self.position

        self.position += count

        return ROM.rom_data[position : position + count]

    def bulk_write(self, data: bytearray, position: int = -1):
        if position >= 0:
            self.seek(position)
        else:
            position = self.position

        self.position += len(data)

        ROM.rom_data[position : position + len(data)] = data
