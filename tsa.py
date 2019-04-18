from Data import tsa_offsets

tsa_data = bytearray(1024)


def load_tsa_data(rom, object_set_number):
    global tsa_data

    rom.seek(tsa_offsets[object_set_number])

    tsa_data = rom.bulk_read(1024)

    return tsa_data.copy()
