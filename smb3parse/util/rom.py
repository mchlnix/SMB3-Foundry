from smb3parse.util import little_endian


class Rom:
    def __init__(self, rom_data: bytearray):
        self._data = rom_data

    def little_endian(self, offset: int) -> int:
        return little_endian(self._data[offset : offset + 2])

    def write_little_endian(self, offset: int, integer: int):
        right_byte = (integer & 0xFF00) >> 8
        left_byte = integer & 0x00FF

        self.write(offset, bytes([left_byte, right_byte]))

    def read(self, offset: int, length: int) -> bytearray:
        return self._data[offset : offset + length]

    def write(self, offset: int, data: bytes):
        self._data[offset : offset + len(data)] = data

    def find(self, byte: bytes, offset: int = 0) -> int:
        return self._data.find(byte, offset)

    def int(self, offset: int) -> int:
        read_bytes = self.read(offset, 1)

        return read_bytes[0]

    def save_to(self, path: str):
        with open(path, "wb") as file:
            file.write(self._data)
