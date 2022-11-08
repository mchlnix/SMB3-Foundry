from collections import defaultdict

from PySide6.QtWidgets import QApplication, QProgressDialog

from foundry.game.File import ROM
from smb3parse.levels import WORLD_COUNT
from smb3parse.util.parser import gen_levels_in_rom
from smb3parse.util.parser.level import ParsedLevel


class LevelParseProgressDialog(QProgressDialog):
    def __init__(self):
        super(LevelParseProgressDialog, self).__init__(
            "Parsing World Maps to find Levels.", "Cancel", 0, WORLD_COUNT - 1
        )

        self.levels_per_object_set: dict[int, set[int]] = defaultdict(set)
        self.levels_by_address: dict[int, ParsedLevel] = {}

        self.setWindowTitle("Parsing World Maps to find Levels")
        self.forceShow()

        QApplication.processEvents()

        self._get_all_levels()

    def _get_all_levels(self):
        level_gen = gen_levels_in_rom(ROM())

        try:
            world_number, levels_in_world = next(level_gen)
            while True:
                self.setLabelText(f"Parsing World {world_number}. Found Levels: {levels_in_world}")
                self.setValue(world_number - 1)

                QApplication.processEvents()
                world_number, levels_in_world = level_gen.send(self.wasCanceled())

        except StopIteration as si:
            self.levels_per_object_set, self.levels_by_address = si.value
