# import pathlib
import sys
import time

from PySide6.QtWidgets import QApplication

from foundry.game.File import ROM
from smb3parse.constants import PLAINS_OBJECT_SET
from smb3parse.util.parser import gen_levels_in_rom
from smb3parse.util.parser.cpu import NesCPU
from smb3parse.util.parser.examples.canvas import Canvas
from r6502 import load_from_address, ParsedLevel

if __name__ == "__main__":
    start = time.time()
    rom = ROM("roms/SMB3.nes")

    # mpu = NesCPU(rom_data, False)
    # parsed_level = r6502.load_from_address(PLAINS_OBJECT_SET, 0x1FB92, 0xC537, 100000)

    # parse 1-1
    parsed_level: ParsedLevel = load_from_address(rom._data, 32, PLAINS_OBJECT_SET, 0x1FB92, 0xC537)

    print("\n".join(map(str, parsed_level.parsed_objects)))

    # pathlib.Path("/tmp/memory.bin").write_bytes(bytes(mpu.memory[0x6000:0x7950]))

    list(gen_levels_in_rom(rom))
    print(time.time() - start)
    exit(0)
    app = QApplication()

    canvas = Canvas(parsed_level)

    print(parsed_level.parsed_objects)
    print(parsed_level.parsed_enemies)

    app.exec()
