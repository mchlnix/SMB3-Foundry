def little_endian(two_bytes: bytearray) -> int:
    """
    Takes a byte array of length 2 and returns the integer it represents in little endian.
    """

    first, second = two_bytes

    return (second << 8) + first
