import pathlib

from PySide6.QtWidgets import QApplication

from foundry.game.File import ROM
from smb3parse.data_points import Position
from smb3parse.util.parser.cpu import NesCPU
from smb3parse.util.parser.examples.canvas import Canvas

if __name__ == "__main__":
    rom = ROM("SMB3.nes")

    mpu = NesCPU(rom)

    # parse 1-1
    parsed_level = mpu.load_from_world_map(0, Position(4, 2, 0))

    print("\n".join(map(str, parsed_level.parsed_objects)))

    pathlib.Path("/tmp/memory.bin").write_bytes(bytes(mpu.memory[0x6000:0x7950]))

    app = QApplication()

    canvas = Canvas(parsed_level)

    app.exec()
