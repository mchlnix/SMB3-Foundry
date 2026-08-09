import time

from PySide6.QtWidgets import QApplication

from foundry.game.File import ROM
from smb3parse.constants import PLAINS_OBJECT_SET
from smb3parse.util.parser import gen_levels_in_rom
from smb3parse.util.parser.examples.canvas import Canvas

if __name__ == "__main__":
    start = time.time()
    rom = ROM("roms/SMB3.nes")

    ##########################
    use_rust = False
    ##########################

    if use_rust:  # rust version
        from r6502 import load_from_address, ParsedLevel
    else:
        from smb3parse.util.parser.cpu import load_from_address
        from smb3parse.util.parser.level import ParsedLevel

    parsed_level: ParsedLevel = load_from_address(rom._data, 32, PLAINS_OBJECT_SET, 0x1FB92, 0xC537, 1_000_000)

    list(gen_levels_in_rom(rom, use_rust))

    print(time.time() - start)

    exit(0)
    app = QApplication()

    canvas = Canvas(parsed_level)

    print(parsed_level.parsed_objects)
    print(parsed_level.parsed_enemies)

    app.exec()
