from functools import lru_cache as lru_cache
from typing import List


@lru_cache
def get_byte_bits(b: int, reverse: bool = False, false_value: int = 0, true_value: int = 1) -> List[int]:
    """
    Converts a byte to a row 1 bit per pixel row of image data
    :param b: The byte to be converted
    :param reverse: To start from the left or right respectively
    :param false_value: The value of the bit if False
    :param true_value: The value of the bit if True
    :return: A list representation of a bit
    """
    if reverse:
        return [true_value if b & (0x80 >> i) else false_value for i in range(8)]
    else:
        return [true_value if b & (0b1 << i) else false_value for i in range(8)]