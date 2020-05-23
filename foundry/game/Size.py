from dataclasses import dataclass


@dataclass
class Size:
    """Defines a 2d shape"""
    width: int = 0
    height: int = 0

    @classmethod
    def from_dict(cls, dic: dict, default_width: int = 1, default_height: int = 1):
        """Makes a 2d size from a dictionary of values"""
        width = dic["width"] if "width" in dic else default_width
        height = dic["height"] if "height" in dic else default_height
        return cls(width, height)
