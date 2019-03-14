from Data import tsa_offsets

tsa_data = bytearray(1024)
object_number = bytearray(4)

OBJECT_SET_SIZE = 0xC0


# holds a table that has nes graphics
class MetaTable:
    def __init__(self, rom, tile_amount, offset):
        tile_offset = 0
        self.metaTable = bytearray(tile_amount * 64)
        self.tile_amount = tile_amount

        rom.seek(offset)

        tile_buffer = bytearray(0x1000 + 1)

        for i in range(len(tile_buffer)):
            tile_buffer[i] = rom.get_byte()

        for i in range(tile_amount):
            base_offset = i * 16

            # one tile is 8*2 bytes long
            for j in range(8):
                right_byte = tile_buffer[base_offset + j]
                left_byte = tile_buffer[base_offset + j + 8]

                # 8 pixel are encoded in 2 consecutive bytes
                for k in range(8):
                    mask = 2**k
                    self.metaTable[tile_offset + k] = (right_byte & mask) // mask | \
                                                      (((left_byte & mask) // mask) << 1)

                tile_offset += 8


def load_tsa_data(rom, object_set_number):
    rom.seek(tsa_offsets[object_set_number])

    print(f"Getting tsa data for object set {object_set_number}")

    for i in range(1024):
        tsa_data[i] = rom.get_byte()

    # for i in range(256):
    #     print(f"{tsa_data[i]} {tsa_data[256 + i]} {tsa_data[512 + i]} {tsa_data[768 + i]}")

    return tsa_data.copy()
