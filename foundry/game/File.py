from os.path import basename
from pathlib import Path
from typing import Optional

from smb3parse.util.rom import INESHeader, Rom, PRG_BANK_SIZE


class ROM(Rom):
    MARKER_VALUE = bytes("SMB3FOUNDRY", "ascii")
    PRG030_INDEX = -2
    """The index passed to search_bank to search the vanilla prg030 bank, regardless of expanded ROM"""
    PRG031_INDEX = -1
    """The index passed to search_bank to search the vanilla prg031 bank, regardless of expanded ROM"""

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

    def search_bank(self, needle: bytes, bank: int) -> int:
        """Search a specific bank given a zero-based bank index.
        If negative values are used, -1 is the last bank, -2 is the second-to-last bank, etc.
        """
        num_prg_banks = ROM().prg_banks
        # Mod here for negative banks (negative indices index from the end)
        bank = bank % num_prg_banks

        if bank not in range(num_prg_banks):
            return -1

        start = bank * PRG_BANK_SIZE
        return self.find(needle, start, start + PRG_BANK_SIZE)
