from os.path import basename
from typing import List, Optional

from smb3parse.util.rom import Rom


_ROM: "ROM" = None


WORLD_COUNT = 9  # includes warp zone

TSA_OS_LIST = 0x3C3F9
TSA_TABLE_SIZE = 0x400
TSA_TABLE_INTERVAL = TSA_TABLE_SIZE + 0x1C00

TSA_BASE_OS = 0x00010


def to_word(byte_1: int, byte_2: int):
    """Converts two bytes into a word"""
    return (byte_2 << 8) + byte_1


def get_bank_offset(bank: int):
    """Helper function for getting the bank offset quickly"""
    return bank * 0x2000 + 0x10


class BankHandler:
    """Handles multiple banks and allow them to work in sync"""
    def __init__(self, banks):
        self.amount_of_banks = banks
        self.banks = [Bank() for _ in range(banks)]

    def add_data(self, data: list):
        """Adds a list of data to the bank"""
        for idx, bank in enumerate(self.banks):
            offset = bank.add_data(data)
            if offset is not None:
                return idx, offset
        else:
            return None

    def save_to_rom(self, bank_idx):
        """Saves each bank to ROM"""
        for idx, bank in enumerate(self.banks):
            bank.save_to_rom(bank_idx + idx)


class Bank:
    """Handles the bank element of the game.  Very useful for converting data for NES ready data"""
    def __init__(self):
        self.data = []

    def add_data(self, data: List[int]):
        """Adds a string of data to the bank"""
        len = len(self.data)
        if len + len(data) < 0x2000:
            self.data.extend(list(bytearray(data)))
            return len
        return None

    def save_to_rom(self, bank_idx: int, offset: int=0):
        """Saves the data inside the bank to ROM"""
        ROM().bulk_write(bytearray(self.data), get_bank_offset(bank_idx) + offset)


def load_from_file(pathname: str) -> None:
    """Loads a new ROM"""
    if _ROM is None:
        ROM(pathname)
    else:
        _ROM.load_from_file(pathname)


class ROM(Rom):
    MARKER_VALUE = bytes("SMB3FOUNDRY", "ascii")

    def __new__(cls, *args, **kwargs):
        global _ROM
        if _ROM is None:
            _ROM = super().__new__(cls)
        return _ROM

    def __init__(self, pathname: Optional[str] = None):
        if _ROM is None or not hasattr(_ROM, "path"):
            if pathname is None:
                raise ValueError("Rom has not been loaded")
            self.path = pathname
            self.name = basename(pathname)
            self.rom_data = bytearray()
            self.additional_data = bytearray()
            self.load_from_file(pathname)
            Rom.__init__(self, self.rom_data)
            self._position = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"

    @property
    def chr_offset(self) -> int:
        """Provides the offset for the chr data"""
        return self.get_byte(5) * 0x2000 + 0x10

    @property
    def position(self) -> int:
        """The current index in ROM"""
        return self._position

    @position.setter
    def position(self, position: int) -> None:
        if position is None or position < 0:
            return  # Do not want to change the position
        if position > len(self.rom_data):
            raise IndexError(f"Invalid position: {position} inside rom of length: {len(self.rom_data)}")
        self._position = position

    def load_from_file(self, pathname: str):
        """Loads a file from memory"""
        if pathname is None:
            raise ValueError("INVALID PATH")
        with open(pathname, "rb") as rom:
            data = bytearray(rom.read())

        additional_data_start = data.find(ROM.MARKER_VALUE)

        if additional_data_start == -1:
            self.rom_data = data
            self.additional_data = ""
        else:
            self.rom_data = data[:additional_data_start]
            additional_data_start += len(ROM.MARKER_VALUE)
            self.additional_data = data[additional_data_start:].decode("utf-8")

    @staticmethod
    def tsa_offset(object_set: int) -> int:
        rom = ROM()

        tsa_index = rom.int(TSA_OS_LIST + object_set)

        if object_set == 0:
            # todo why is the tsa index in the wrong (seemingly) false?
            tsa_index += 1

        tsa_index = rom.int(TSA_OS_LIST + object_set)

        if object_set == 0:
            # todo why is the tsa index in the wrong (seemingly) false?
            tsa_index += 1

        return TSA_BASE_OS + tsa_index * TSA_TABLE_INTERVAL

    @staticmethod
    def get_tsa_data(object_set: int) -> bytearray:
        rom = ROM()

        tsa_start = ROM.tsa_offset(object_set)

        return rom.read(tsa_start, TSA_TABLE_SIZE)

    @staticmethod
    def save_to_file(path: str):
        with open(path, "wb") as f:
            f.write(bytearray(_ROM.rom_data))

        if _ROM.additional_data:
            with open(path, "ab") as f:
                f.write(_ROM.MARKER_VALUE)
                f.write(_ROM.additional_data.encode("utf-8"))

        _ROM.path = path
        _ROM.name = basename(path)

    @staticmethod
    def set_additional_data(additional_data):
        _ROM.additional_data = additional_data

    def get_word(self, position: Optional[int] = None) -> int:
        """Reads a word of data"""
        self.position = position
        low_byte = self.rom_data[self.position]
        self.position += 1
        high_byte = self.rom_data[self.position]
        self.position += 1
        return low_byte + (high_byte << 8)

    def get_byte(self, position: Optional[int] = None) -> int:
        """Reads a byte from rom"""
        self.position = position
        return self.rom_data[self.position]

    def peek_byte(self, position: Optional[int] = None) -> int:
        """Gets a byte without saving the position"""
        _position = self.position
        byte = self.get_byte(position)
        self.position = _position
        return byte

    def bulk_read(self, count: int, position: Optional[int] = None) -> bytearray:
        """Reads multiple bytes"""
        self.position = position
        position = self.position
        self.position += count
        return self.rom_data[position: self.position]

    def bulk_write(self, data: bytearray, position: Optional[int] = None) -> None:
        """Writes multiple bytes"""
        self.position = position
        position = self.position
        self.position += len(data)
        try:
            self.rom_data[position: position + len(data)] = data
        except IndexError:
            raise IndexError(f"Unable to save rom data {data} to {position}")
