from dataclasses import dataclass


@dataclass
class Range:
    """Determine range of numbers python"""
    start: int = 0
    end: int = 0

    @property
    def size(self):
        """The end - start"""
        return abs(self.start - self.end)

    def is_inside(self, idx: int) -> bool:
        """Determines if an idx is inside the range"""
        try:
            return self.start <= idx <= self.end
        except TypeError:
            return False

    @classmethod
    def from_offset(cls, start, offset):
        return cls(start, start + offset)

    @classmethod
    def from_dict(cls, dic: dict, default_start: int = 0, default_end: int = 0):
        """Makes a dictionary from dictionary values"""
        start = dic["start"] if "start" in dic else default_start
        int(start[1:], 16) if isinstance(start, str) and start.startswith("$") else int(start)
        end = dic["end"] if "end" in dic else default_end
        int(end[1:], 16) if isinstance(end, str) and end.startswith("$") else int(end)
        return cls(start, end)
