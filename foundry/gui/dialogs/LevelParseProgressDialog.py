"""Show progress while SMB3 world maps are scanned for level metadata.

This module owns :class:`LevelParseProgressDialog`, the transient dialog that
bridges ROM parsing work into a Qt progress surface. The dialog consumes the
shared ROM handle exposed through :mod:`foundry.game.File` together with the
incremental world-by-world state yielded by :func:`smb3parse.util.parser.gen_levels_in_rom`.
It produces a modal ``QProgressDialog`` that stays responsive while parsing and
retains the discovered ``FoundLevel`` collections for later editor workflows.

See Also
--------
foundry.game.File
    Provides the ROM object consumed by the parser workflow.
smb3parse.util.parser
    Defines the generator and ``FoundLevel`` records accumulated by this
    dialog.
"""

from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QProgressDialog

from foundry.game.File import ROM
from smb3parse.levels import WORLD_COUNT
from smb3parse.util.parser import FoundLevel, gen_levels_in_rom


class LevelParseProgressDialog(QProgressDialog):
    """Display and coordinate the level parse progress dialog.

    It supports a focused editor dialog while keeping UI state synchronized with the model. Callers use it to edit one focused slice of model or settings state.

    Attributes
    ----------
    levels_by_address : dict[int, FoundLevel]
        Collection of levels by address maintained for dialog UI state.
    levels_per_object_set : dict[int, set[int]]
        Levels per object set used for dialog UI state.
    """

    def __init__(self):
        """Initialize the object and its runtime state.

        It supports a focused editor dialog while keeping UI state synchronized with the model. Initialization establishes the state later methods rely on instead of re-reading ROM data.
        """
        super(LevelParseProgressDialog, self).__init__(
            "Parsing World Maps to find Levels.", "Cancel", 0, WORLD_COUNT - 1
        )

        self.levels_per_object_set: dict[int, set[int]] = defaultdict(set)
        self.levels_by_address: dict[int, FoundLevel] = {}

        self.setWindowTitle("Parsing World Maps to find Levels")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.forceShow()

        QApplication.processEvents()

        self._get_all_levels()

    def _get_all_levels(self):
        """Parse the ROM world maps and store discovered levels.

        It supports a focused editor dialog while keeping UI state synchronized with the model. The method delegates lower-level work while keeping the public workflow focused.
        """
        level_gen = gen_levels_in_rom(ROM())

        try:
            world_number, levels_in_world = next(level_gen)
            while True:
                self.setLabelText(f"Parsing World {world_number}. Found Levels: {levels_in_world}")
                self.setValue(world_number - 1)

                QApplication.processEvents()
                world_number, levels_in_world = level_gen.send(self.wasCanceled())

        except StopIteration as si:
            # TODO: Check for wasCancelled()
            self.levels_per_object_set, self.levels_by_address = si.value
