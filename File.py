class ROM:
    data = bytearray()

    def __init__(self, path="SMB3.nes"):
        if not ROM.data:
            ROM.load_from_file(path)

        self.position = 0

    @staticmethod
    def load_from_file(path):
        with open(path, "rb") as rom:
            ROM.data = list(rom.read())

    @staticmethod
    def save_to_file(path):
        with open(path, "wb") as f:
            f.write(bytearray(ROM.data))

    def seek(self, position):
        if position > len(ROM.data) or position < 0:
            return -1

        self.position = position

        return 0

    def get_byte(self, position=-1):
        if position >= 0:
            k = self.seek(position) >= 0
        else:
            k = self.position < len(ROM.data)

        if k:
            return_byte = ROM.data[self.position]
        else:
            return_byte = 0

        self.position += 1

        return return_byte

    def peek_byte(self, position=-1):
        old_position = self.position

        byte = self.get_byte(position)

        self.position = old_position

        return byte

    def bulk_read(self, count, position=-1):
        if position >= 0:
            self.seek(position)
        else:
            position = self.position

        self.position += count

        return ROM.data[position:position+count]

    def bulk_write(self, data, position=-1):
        if position >= 0:
            self.seek(position)
        else:
            position = self.position

        self.position += len(data)

        ROM.data[position:position + len(data)] = data
