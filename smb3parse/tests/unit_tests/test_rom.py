from smb3parse.util.rom import INESHeader, Rom


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


def test_header(rom):
    assert rom._header.magic == b"NES\x1A"
    assert rom._header.prg_units == 0x10
    assert rom._header.chr_units == 0x10
    assert rom._header.flags6 == b"\x40"

    assert rom._header.prg_size == 0x40000
    assert rom._header.chr_size == 0x20000


def test_header_expanded(rom, expanded_rom):
    assert rom.prg_normalize(0x30010) == 0x30010
    assert rom.prg_normalize(0x40010) == 0x40010
    assert expanded_rom.prg_normalize(0x30010) == 0x30010
    assert expanded_rom.prg_normalize(0x40010) == 0x40010 + INESHeader.PRG_UNIT_SIZE


def test_expanded_rom_reads_same_as_normal(rom, expanded_rom):
    assert len(rom._data) < len(expanded_rom._data)

    for offset in range(0, rom._header.prg_size + rom._header.chr_size, INESHeader.PRG_UNIT_SIZE // 4):
        if offset == 0:
            # skip the INES Header, since it will be different in an expanded rom
            continue

        assert rom.read(offset, 0x10) == expanded_rom.read(offset, 0x10)
