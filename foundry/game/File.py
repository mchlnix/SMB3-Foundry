from os.path import basename
from pathlib import Path
from typing import Optional

from smb3parse.util.rom import INESHeader, Rom


class ROM(Rom):
    MARKER_VALUE = bytes("SMB3FOUNDRY", "ascii")

    rom_data = bytearray()
    header: Optional[INESHeader] = None

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
        """Returns bytes, instead of bytearray, because bytes is hashable. FIXME?"""
        rom = ROM()

        return bytes(rom.tsa_data_for_object_set(object_set))

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
        Path(path).open("wb").write(bytearray(ROM.rom_data))

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
