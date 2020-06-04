from dataclasses import dataclass


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








