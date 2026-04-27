"""List stock SMB3 level addresses as one source inside the level selector.

This module owns the fallback selection source that exposes the vanilla stock
level tables by world. It is the simplest level-selector source: world and
level list widgets feed staged object-set and ROM-address data into the parent
dialog without relying on found-level metadata or world-map pointer browsing.

See Also
--------
foundry.gui.dialogs.level_selector.LevelSelector
    Parent dialog that stages selected stock addresses for acceptance.
foundry.gui.dialogs.level_selector.found_level_list
    Alternative source that stages levels discovered from the active ROM.
"""

from PySide6.QtWidgets import QGridLayout, QLabel, QListWidget, QWidget

from foundry.game.File import ROM
from foundry.game.level.Level import Level
from foundry.gui import WORLD_ITEMS
from smb3parse.levels import HEADER_LENGTH

LOST_LEVELS_INDEX = 8
OVERWORLD_MAPS_INDEX = 9


class StockLevelWidget(QWidget):
    """List stock SMB3 level addresses by world.

    This widget exposes the vanilla US address table as a fallback selection
    source. These addresses can become stale after automatic level management or
    other ROM edits, so the selector warns when found-level metadata exists.

    Attributes
    ----------
    level_list : QListWidget
        Levels available for the selected world row.
    world_list : QListWidget
        World, lost-level, and overworld-map categories.
    """

    def __init__(self):
        """Create the stock world and level lists.

        The first world is selected immediately, but the parent level selector
        decides when to consume the selection.
        """
        super().__init__()

        self.world_list = QListWidget(parent=self)
        self.world_list.addItems(WORLD_ITEMS)

        self.world_list.itemSelectionChanged.connect(self._on_world_click)

        self.level_list = QListWidget(parent=self)

        stock_level_layout = QGridLayout(self)

        description_label = QLabel()
        description_label.setWordWrap(True)
        description_label.setText(
            "These are the Level and Enemy addresses of the US version of SMB3. If Levels are moved (e.g. by the "
            "automatic Level management) or overwritten by other Levels, then loading these might result in an error "
            "or broken Level."
        )

        if ROM.additional_data.found_levels:
            description_label.setStyleSheet("QLabel { color : red; }")

        stock_level_layout.addWidget(QLabel("World"), 0, 0)
        stock_level_layout.addWidget(QLabel("Level"), 0, 1)

        stock_level_layout.addWidget(self.world_list, 1, 0)
        stock_level_layout.addWidget(self.level_list, 1, 1)

        stock_level_layout.addWidget(description_label, 2, 0, 1, 2)

        # doing it here, when the level selector is not connected to our signals yet, will not populate the spinner
        # widgets
        # that is OK, though, because, otherwise a potentially out-of-date stock level would populate the spinners,
        # while the level selector opens to the world map by default
        self.world_list.setCurrentRow(0)

    def _on_world_click(self):
        """Populate levels for the selected stock world category.

        The special overworld-map row maps to world number 0 because those
        entries use world-map layout data instead of normal level data.
        """
        index = self.world_list.currentRow()

        if index < 0:
            index = 0

        if index == OVERWORLD_MAPS_INDEX:
            world_number = 0  # world maps
        else:
            world_number = index + 1

        self.level_list.clear()

        # skip the first meaningless item
        for level in Level.offsets[1:]:
            if level.game_world == world_number and level.name:
                self.level_list.addItem(level.name)

        if self.level_list.count():
            self.level_list.setCurrentRow(0)

    @property
    def _level_index(self):
        """Resolve the selection into an index in ``Level.offsets``.

        Lost levels and regular worlds use different base offsets in
        ``Level.world_indexes``.

        Returns
        -------
        int
            Offset-table index for the selected stock level.
        """
        level_array_offset = self.level_list.currentRow() + 1

        if self.level_is_lost:
            level_array_offset += Level.world_indexes[9]

        elif not self.level_is_overworld:
            level_array_offset += Level.world_indexes[self.world_number]

        return level_array_offset

    @property
    def _level_def(self):
        """Resolve the selection into the stock level-definition record.

        Downstream properties all read from this definition so stock-address
        lookups, display names, and object-set decisions stay consistent for one
        selected row.

        Returns
        -------
        object
            Entry from ``Level.offsets``.
        """
        return Level.offsets[self._level_index]

    @property
    def level_address(self):
        """Resolve the selection into a stock layout/header address.

        Normal level table entries point after the header, so ``HEADER_LENGTH``
        is subtracted for those levels. Overworld maps already use the layout
        address directly.

        Returns
        -------
        int
            ROM address for the selected level data.
        """
        level_address = self._level_def.rom_level_offset

        if not self.level_is_overworld:
            level_address -= HEADER_LENGTH

        return level_address

    @property
    def enemy_address(self):
        """Resolve the selection into a stock enemy-data address.

        Workshop-style stock enemy entries are one byte past the actual stream
        start, so nonzero values are adjusted back by one before the level
        selector stages the address into its shared enemy-data spinner and
        later accept-time payload. This property is therefore the handoff point
        between the stock lookup tables and the common staged-address workflow
        that the parent selector shares with found-level and world-map sources.

        Returns
        -------
        int
            ROM address for enemy/item data, or ``0`` for overworld maps.
        """
        if not self.level_is_overworld:
            enemy_address = self._level_def.enemy_offset
        else:
            enemy_address = 0

        if enemy_address:
            # data in look up table is off by one, since workshop ignores the first byte
            enemy_address -= 1

        return enemy_address

    @property
    def object_set_number(self):
        """Resolve the selection into a stock object set number.

        This object set is what the level selector stages into its common parse
        controls before preview or accept logic runs.

        Returns
        -------
        int
            Object set used to parse and render the selected level.
        """
        return self._level_def.real_obj_set

    @property
    def world_number(self):
        """Resolve the selection into a one-based world number.

        Lost levels are treated as world 1 for downstream naming and loading.
        The parent level selector uses this normalized world number when it
        labels the staged selection and when it decides which world tab to show
        after other workflows bounce back into the stock list.

        Returns
        -------
        int
            One-based world number for the selection.
        """
        if self.level_is_lost:
            world_number = 1
        else:
            world_number = self.world_list.currentRow() + 1

        return world_number

    @world_number.setter
    def world_number(self, value):
        """Select a world row by one-based world number.

        Parameters
        ----------
        value : int
            One-based world number to select.
        """
        self.world_list.setCurrentRow(value - 1)

    @property
    def level_name(self):
        """Resolve the selection into a stock-level display name.

        The selector combines world context and the stock level name so the
        staged selection can be shown consistently across stock, found, and
        world-map sources before the dialog commits one source's addresses.

        Returns
        -------
        str
            Human-readable selection label.
        """
        if self.level_is_overworld:
            level_name = ""
        elif self.level_is_lost:
            level_name = "Lost World, "
        else:
            level_name = f"World {self.world_number}, "

        level_name += str(self._level_def.name)

        return level_name

    @property
    def level_is_overworld(self):
        """Report whether the selected category is overworld maps.

        The property is used by selector staging to disable unsupported accept
        paths and to decide whether enemy data should be shown at all.

        Returns
        -------
        bool
            ``True`` when the overworld-map category is selected.
        """
        return self.world_list.currentRow() == OVERWORLD_MAPS_INDEX

    @property
    def level_is_lost(self):
        """Report whether the selected category is lost levels.

        Lost levels reuse stock tables but are labeled separately so callers can
        present the selection as a special-case fallback rather than a normal
        world row.

        Returns
        -------
        bool
            ``True`` when the lost-level category is selected.
        """
        return self.world_list.currentRow() == LOST_LEVELS_INDEX

    def showEvent(self, event):
        """Focus the world list when the stock selector is shown.


        Parameters
        ----------
        event : object
            Qt event delivered to the widget.
        """
        self.world_list.setFocus()
