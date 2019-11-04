def little_endian(two_bytes: bytearray) -> int:
    first, second = two_bytes

    return (second << 8) + first
