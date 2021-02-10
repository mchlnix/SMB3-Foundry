from smb3parse.util.rom import Rom, INESHeader


def test_find():
    rom_bytes = bytearray(b"\x00\x01\x02\x03\x04\x05\x06\x00\xff\xff\xff\xff\xff\xff\xff\xff")
    header = INESHeader.from_buffer_copy(rom_bytes)

    rom = Rom(rom_bytes, header)

    assert rom.find(b"\x00") == 0
    assert rom.find(b"\x00", 1) == 7
    assert rom.find(b"\x07") == -1


def test_little_endian():
    rom_bytes = bytearray(b"\x00\x01\x02\x03\x04\x05\x06\x00\xff\xff\xff\xff\xff\xff\xff\xff")
    header = INESHeader.from_buffer_copy(rom_bytes)

    rom = Rom(rom_bytes, header)

    assert rom.little_endian(0) == (0x01 << 8) + 0x00
    assert rom.little_endian(6) == (0x00 << 8) + 0x06


def test_int():
    rom_bytes = bytearray(b"\x00\x01\x02\x03\x04\x1f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff")
    header = INESHeader.from_buffer_copy(rom_bytes)
    numbers = [0, 1, 2, 3, 4, 0x1F]

    rom = Rom(rom_bytes, header)

    for offset, number in enumerate(numbers):
        assert rom.int(offset) == number
