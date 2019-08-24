from os.path import basename
from typing import List, Optional

WORLD_COUNT = 9  # includes warp zone

# W = WORLD_MAP
# OS = OFFSET

OS_SIZE = 2  # byte

W_BASE_OS = 0xE010
W_LAYOUT_LIST_OS = W_BASE_OS + 0xA598
W_INIT_LIST_OS = W_BASE_OS + 0xB3CA
W_LEVEL_Y_POS_LIST_OS = W_BASE_OS + 0xB3DC
W_LEVEL_X_POS_LIST_OS = W_BASE_OS + 0xB3EE
W_LEVEL_ENEMY_LIST_OS = W_BASE_OS + 0xB400
W_LEVEL_LAYOUT_LIST_OS = W_BASE_OS + 0xB412

TSA_OS_LIST = 0x3C3F9
TSA_TABLE_SIZE = 0x400
TSA_TABLE_INTERVAL = TSA_TABLE_SIZE + 0x1C00

TSA_BASE_OS = 0x00010


# little endian
def le(two_bytes: bytearray) -> int:
    first, second = two_bytes

    return (second << 8) + first


class ROM:
    MARKER_VALUE = bytes("SMB3FOUNDRY", "ascii")

    rom_data = bytearray()

    additional_data = ""

    path: str = ""
    name: str = ""

    W_LAYOUT_OS_LIST: List[int] = []
    W_INIT_OS_LIST: List[int] = []

    def __init__(self, path: Optional[str] = None):
        if not ROM.rom_data:
            if path is None:
                raise ValueError("Rom was not loaded!")

            ROM.load_from_file(path)

        self.position = 0

    @staticmethod
    def _parse_rom():
        ROM._setup_map_addresses()
        ROM._setup_level_addresses()

    @staticmethod
    def _setup_map_addresses():
        offsets = ROM().bulk_read(WORLD_COUNT * OS_SIZE, W_LAYOUT_LIST_OS)

        ROM.W_LAYOUT_OS_LIST.clear()

        for world in range(WORLD_COUNT):
            index = world * 2

            world_map_offset = (offsets[index + 1] << 8) + offsets[index]

            ROM.W_LAYOUT_OS_LIST.append(W_BASE_OS + world_map_offset)

    @staticmethod
    def _setup_level_addresses():
        pass

    @staticmethod
    def get_tsa_data(object_set: int) -> bytearray:
        rom = ROM()

        rom.seek(TSA_OS_LIST + object_set)

        tsa_index = rom.get_byte()

        if object_set == 0:
            # todo why is the tsa index in the wrong (seemingly) false?
            tsa_index += 1

        rom.seek(TSA_BASE_OS + tsa_index * TSA_TABLE_INTERVAL)

        return rom.bulk_read(TSA_TABLE_SIZE)

    @staticmethod
    def load_from_file(path: str):
        with open(path, "rb") as rom:
            data = bytearray(rom.read())

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

        ROM._parse_rom()

    @staticmethod
    def save_to_file(path: str):
        with open(path, "wb") as f:
            f.write(bytearray(ROM.rom_data))

        if ROM.additional_data:
            with open(path, "ab") as f:
                f.write(ROM.MARKER_VALUE)
                f.write(ROM.additional_data.encode("utf-8"))

    @staticmethod
    def set_additional_data(additional_data):
        ROM.additional_data = additional_data

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
