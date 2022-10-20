from typing import Callable

from smb3parse.constants import BASE_OFFSET
from smb3parse.util.parser import MEM_Screen_Start_AddressH, MEM_Screen_Start_AddressL
from smb3parse.util.rom import PRG_BANK_SIZE, Rom


class NESMemory(list):
    def __init__(self, backing_list: list, rom: Rom):
        super(NESMemory, self).__init__(backing_list)

        self.rom = rom

        self._read_observers: dict[list[int, Callable]] = {}
        self._write_observers: dict[list[int, Callable]] = {}

        # load PRG 30
        self._load_bank(30, 0x8000)

        # load PRG 31
        self._load_bank(31, 0xE000)

    def load_a000_page(self, prg_index: int):
        self._load_bank(prg_index, 0xA000)

    def load_c000_page(self, prg_index: int):
        self._load_bank(prg_index, 0xC000)

    def _load_bank(self, prg_index: int, offset: int):
        prg_bank_position = BASE_OFFSET + prg_index * PRG_BANK_SIZE

        self[offset : offset + PRG_BANK_SIZE] = self.rom.read(prg_bank_position, PRG_BANK_SIZE)

    def add_read_observer(self, address_list: list[int], callback: Callable):
        self._read_observers[address_list] = callback

    def add_write_observer(self, address_list: list[int], callback: Callable):
        self._write_observers[tuple(address_list)] = callback

    def __getitem__(self, address: int):
        if address == 0x10:
            return_value = 0b1000_0000
        else:
            return_value = super(NESMemory, self).__getitem__(address)

        for address_range, callback in self._read_observers.items():
            if address in address_range:
                callback(address, return_value)

        return return_value

    def __setitem__(self, address, value):
        for address_range, callback in self._write_observers.items():
            if address in address_range:
                callback(address, value)

        if address in [MEM_Screen_Start_AddressL, MEM_Screen_Start_AddressH]:
            # ignore these addresses, since they seem to access the Mapper, but actually overwrite a pointer to the
            # screen memory
            return

        return super(NESMemory, self).__setitem__(address, value)
