from util import little_endian


class Rom:
    def __init__(self, rom_data: bytearray):
        self._data = rom_data

    def little_endian(self, offset: int) -> int:
        return little_endian(self._data[offset : offset + 2])

    def read(self, offset: int, length: int) -> bytearray:
        return self._data[offset : offset + length]

    def find(self, byte: bytes, offset: int = 0) -> int:
        return self._data.find(byte, offset)
