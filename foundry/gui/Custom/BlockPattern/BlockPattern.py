

from dataclasses import dataclass

from smb3parse.asm6_converter import to_hex


@dataclass
class BlockPattern:
    """A pattern for a block in terms of tsa data"""

    top_left: int
    top_right: int
    bottom_left: int
    bottom_right: int

    @classmethod
    def from_tsa_data(cls, index: int, tsa_data: bytearray):
        """Forms a block pattern from tsa data"""
        return cls(*[tsa_data[(idx * 256) + index] for idx in range(4)])

    def __str__(self) -> str:
        return f"{to_hex(self[0])}, {to_hex(self[1])}, {to_hex(self[2])}, {to_hex(self[3])}"

    def __getitem__(self, item: int) -> int:
        if item == 0:
            return self.top_left
        elif item == 1:
            return self.top_right
        elif item == 2:
            return self.bottom_left
        elif item == 3:
            return self.bottom_right
        else:
            raise NotImplementedError

    def __setitem__(self, key: int, value: int):
        if key == 0:
            self.top_left = value
        elif key == 1:
            self.top_right = value
        elif key == 2:
            self.bottom_left = value
        elif key == 3:
            self.bottom_right = value
        else:
            raise NotImplementedError
