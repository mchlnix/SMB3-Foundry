from os.path import basename
from typing import Optional

from smb3parse.constants import BASE_OFFSET, PAGE_A000_ByTileset, WORLD_MAP_TSA_INDEX
from smb3parse.util.rom import INESHeader, Rom

# W = WORLD_MAP
# OS = OFFSET

OS_SIZE = 2  # byte

TSA_OS_LIST = PAGE_A000_ByTileset
TSA_TABLE_SIZE = 0x400
TSA_TABLE_INTERVAL = TSA_TABLE_SIZE + 0x1C00


class ROM(Rom):
    MARKER_VALUE = bytes("SMB3FOUNDRY", "ascii")

    rom_data = bytearray()
    header = None

    additional_data = ""

    path: str = ""
    name: str = ""

    W_INIT_OS_LIST: list[int] = []

    def __init__(self, path: Optional[str] = None):
        if not ROM.rom_data:
            if path is None:
                raise ValueError("Rom was not loaded!")

            ROM.load_from_file(path)

        super(ROM, self).__init__(ROM.rom_data, ROM.header)

    @staticmethod
    def get_tsa_data(object_set: int) -> bytes:
        rom = ROM()

        # TSA_OS_LIST offset value assumes vanilla ROM size, so normalize it
        tsa_index = rom.int(TSA_OS_LIST + object_set)

        if object_set == 0:
            # Note that for the World Map, PAGE_A000 is set to bank 11, but
            # the actual drawing of the map and the map tiles are defined
            # in bank 12. prg030.asm handles swapping hard-coded to bank 12
            # and drawing the initial map via Map_Reload_with_Completions.
            # Therefore, the PAGE_A000_ByTileset doesn't have the TSA data for
            # the map tiles.
            tsa_index = WORLD_MAP_TSA_INDEX

        # INES header size + (bank with tsa data * sizeof(bank))
        tsa_start = BASE_OFFSET + tsa_index * TSA_TABLE_INTERVAL

        return bytes(rom.read(tsa_start, TSA_TABLE_SIZE))

    @staticmethod
    def load_from_file(path: str):
        with open(path, "rb") as rom:
            data = bytearray(rom.read())

        ROM.header = INESHeader.from_buffer_copy(data)
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
    def reload_from_file():
        if ROM.path:
            ROM.load_from_file(ROM.path)

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

    def get_byte(self, position: int) -> int:
        position = self.prg_normalize(position)

        if position < len(ROM.rom_data):
            return ROM.rom_data[position]

        raise IndexError(
            f"Attempted to read from offset 0x{position:X} when ROM is only of size 0x{len(ROM.rom_data):X}"
        )

    def bulk_read(self, count: int, position: int) -> bytearray:
        position = self.prg_normalize(position)
        return ROM.rom_data[position : position + count]

    def bulk_write(self, data: bytearray, position: int):
        position = self.prg_normalize(position)
        ROM.rom_data[position : position + len(data)] = data
