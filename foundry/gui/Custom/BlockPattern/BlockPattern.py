

from dataclasses import dataclass


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
        return cls(*[tsa_data[(idx * 0xFF) + index] for idx in range(4)])

    def __getitem__(self, item: int) -> int:
        if item == 0:
            return self.top_left
        elif item == 1:
            return self.bottom_left
        elif item == 2:
            return self.top_right
        elif item == 3:
            return self.bottom_right
        else:
            raise NotImplementedError

    def __setitem__(self, key: int, value: int):
        if key == 0:
            self.top_left = value
        elif key == 1:
            self.bottom_left = value
        elif key == 2:
            self.top_right = value
        elif key == 3:
            self.bottom_right = value
        else:
            raise NotImplementedError
