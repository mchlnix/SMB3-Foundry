from typing import Optional


# nn - actual number to be used
# ll - short for 00ll, 2 byte address in the zero page, basically RAM
# hhll - full address, 2 bytes high, 2 bytes low
RTS = 0x60
NOP = 0xEA
LDY_CONST = 0xA0  # LDY #$nn
LDA_CONST = 0xA9  # LDA #$nn
STA_OFFSET = 0x8D  # STA $hhll
STY_RAM = 0x84  # STY $ll


def little_endian(two_bytes: bytearray) -> int:
    """
    Takes a byte array of length 2 and returns the integer it represents in little endian.
    """

    first, second = two_bytes

    return (second << 8) + first


def compare_bytearrays(bytearray_1, bytearray_2, chunk_size=32):
    assert len(bytearray_1) == len(bytearray_2)

    for start_address in range(0, len(bytearray_1), chunk_size):
        old_chunk = bytearray_1[start_address : start_address + chunk_size]
        new_chunk = bytearray_2[start_address : start_address + chunk_size]

        if (
            bytearray_1[start_address : start_address + chunk_size]
            != bytearray_2[start_address : start_address + chunk_size]
        ):
            print()
            print(start_address, hex(start_address))
            print([hex(bit) for bit in old_chunk])
            print([hex(bit) for bit in new_chunk])
            assert False


def lrange(a1: int, a2: Optional[int] = None, a3: Optional[int] = None, /):
    if a2 is None:
        return list(range(a1))

    if a3 is None:
        return list(range(a1, a2))

    return list(range(a1, a2, a3))
