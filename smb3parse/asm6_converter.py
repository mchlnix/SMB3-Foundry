from dataclasses import dataclass
import yaml
from yaml import CLoader as Loader

from foundry import data_dir

with open(data_dir.joinpath("smb3_variables.yaml")) as f:
    variables = yaml.load(f, Loader=Loader)


def handle_partitioning(s):
    """Handles if we have a | diving the characters"""
    if ' | ' in s:
        result = 0
        for ele in [to_int(st) for st in s.split(' | ')]:
            result |= ele
        return result
    elif ' & ' in s:
        result = 0
        for ele in [to_int(st) for st in s.split(' & ')]:
            result &= ele
        return result
    else:
        return s


def convert_str_to_int_white_space(s: str) -> int:
    """Removes whitespace"""
    return to_int(s.strip())


def convert_str_to_int(s: str) -> int:
    """Assumes that we have already determined this is a value to be converted"""
    if s.startswith('$'):
        return int(s[1:], 16)
    try:
        return variables[s]
    except KeyError:
        return int(s)


def to_int(s: str) -> int:
    """Converts value to an int"""
    s = handle_partitioning(s)
    if isinstance(s, int):
        return s
    if s.startswith('$'):
        return convert_str_to_int(s[1:])
    else:
        return int(s)


def to_label(s: str):
    s = s.replace(' ', '_')
    s = s.replace('(', "_")
    s = s.replace(')', "_")
    s = s.replace('/', "_")
    s = s.replace('#', '_')
    return s


def to_hex(i: int):
    if i <= 0xFF:
        return f"${format(i, '02X')}"
    elif i <= 0xFFFF:
        return f"${format(i, '04X')}"
    return f"${hex(i)[:2]}"


@dataclass
class Pointer:
    _address: int
    _bank: int = 0xC000

    @property
    def address(self) -> int:
        return self._address

    @address.setter
    def address(self, address: int):
        self._address = address % 0x2000

    @property
    def bank(self) -> int:
        return self._bank

    @bank.setter
    def bank(self, bank: int):
        if bank < 0xFF:
            self._bank = bank
        elif bank < 0xFFFF:
            self._bank = (bank & 0xF000) >> 12
        else:
            raise NotImplementedError

    @property
    def bank_offset(self):
        return self.bank << 12

    @property
    def relative_address(self):
        return self.address + self.bank_offset

    @classmethod
    def from_absolute_address(cls, address, bank=0xC):
        return cls(address % 0x2000, bank)








