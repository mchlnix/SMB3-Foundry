from os.path import basename


class ROM:
    MARKER_VALUE = bytes("SMB3FOUNDRY", "ascii")

    rom_data = bytearray()

    additional_data = ""

    name = ""

    def __init__(self, path=None):
        if not ROM.rom_data:
            if path is None:
                raise ValueError("Rom was not loaded!")

            ROM.load_from_file(path)

        self.position = 0

    @staticmethod
    def load_from_file(path):
        with open(path, "rb") as rom:
            data = bytearray(rom.read())

        ROM.name = basename(path)

        additional_data_start = data.find(ROM.MARKER_VALUE)

        if additional_data_start == -1:
            ROM.rom_data = data
            ROM.additional_data = ""
            return

        ROM.rom_data = data[:additional_data_start]

        additional_data_start += len(ROM.MARKER_VALUE)

        ROM.additional_data = data[additional_data_start:].decode("utf-8")

    @staticmethod
    def save_to_file(path):
        with open(path, "wb") as f:
            f.write(bytearray(ROM.rom_data))

        if ROM.additional_data is not None:
            with open(path, "ab") as f:
                f.write(ROM.MARKER_VALUE)
                f.write(ROM.additional_data.encode("utf-8"))

    @staticmethod
    def set_additional_data(additional_data):
        ROM.additional_data = additional_data

    def seek(self, position):
        if position > len(ROM.rom_data) or position < 0:
            return -1

        self.position = position

        return 0

    def get_byte(self, position=-1):
        if position >= 0:
            k = self.seek(position) >= 0
        else:
            k = self.position < len(ROM.rom_data)

        if k:
            return_byte = ROM.rom_data[self.position]
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

        return ROM.rom_data[position:position + count]

    def bulk_write(self, data, position=-1):
        if position >= 0:
            self.seek(position)
        else:
            position = self.position

        self.position += len(data)

        ROM.rom_data[position:position + len(data)] = data
