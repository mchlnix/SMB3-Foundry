"""Inspection windows for parsed levels, PRG usage, and byte ownership.

This module packages the level-inspection tooling that sits beside the editor
proper. It lets maintainers and advanced users move from parsed level records
to PRG-bank occupancy, byte-range ownership, and thumbnail-oriented browsing
without stepping outside Foundry's live ROM context.

See Also
--------
foundry.gui.windows.ObjectViewer
    Inspects individual object encodings and decoded block output.
foundry.game.level.Level
    Supplies the ROM-backed level data that these viewers summarize.
"""

import math
from dataclasses import dataclass
from random import randint, seed

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import (
    QBrush,
    QColor,
    QColorConstants,
    QMouseEvent,
    QPainter,
    QPaintEvent,
)
from PySide6.QtWidgets import (
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from foundry import get_level_thumbnail, pixmap_to_base64
from foundry.game.File import ROM
from foundry.gui.localization import tr, tr_data_name
from foundry.gui.windows.CustomChildWindow import CustomChildWindow
from smb3parse.constants import (
    BASE_OFFSET,
    ENEMY_ITEM_OBJECT_SET,
    OBJECT_SET_NAMES,
    PLAINS_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    Constants,
)
from smb3parse.data_points import WorldMapData
from smb3parse.levels import WORLD_COUNT
from smb3parse.util.parser import FoundLevel
from smb3parse.util.rom import PRG_BANK_SIZE


def _gen_level_name(level_address: int, level: FoundLevel) -> str:
    """Generate a readable name for a found level.

    This gives byte-view and tree-view entries a stable label derived from ROM address, world-map
    metadata, and parser-discovered level information. The label is localized
    display text only; the viewer still opens levels from the original ROM
    address and parser metadata.

    Parameters
    ----------
    level_address : int
        ROM address of the level layout data.
    level : FoundLevel
        Level model or level reference used by the operation.

    Returns
    -------
    str
        Generated level name.
    """
    world_data = WorldMapData(ROM(), level.world_number - 1)

    if world_data.big_q_block_level_address == level_address:
        return tr("LevelViewer", "big_question_mark_block_level", "Big Question Mark Block Level")

    if world_data.airship_level_address == level_address:
        return tr("LevelViewer", "airship_level", "Airship Level")

    if world_data.coin_ship_level_address == level_address:
        return tr("LevelViewer", "coin_ship_level", "Coin Ship Level")

    if world_data.generic_exit_level_address == level_address:
        return tr("LevelViewer", "generic_exit_level", "Generic Exit Level")

    if world_data.toad_warp_level_address == level_address:
        return tr("LevelViewer", "toad_warp_level", "Toad Warp Level")

    return tr("LevelViewer", "object_set_level", "{object_set} Level").format(
        object_set=tr_data_name("ObjectSet", OBJECT_SET_NAMES[level.object_set_number])
    )


class LevelViewer(CustomChildWindow):
    """Inspect how parsed levels occupy ROM banks and world-map structure.

    The viewer exposes two complementary perspectives over parsed level data:
    a tree grouped by world and jump relationships, and PRG-bank tabs that show
    where level data sits inside each bank. It is a debugging and reverse-
    engineering aid rather than part of the main editing workflow.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    addresses_by_object_set : dict[int, set[int]]
        Level addresses grouped by object set.
    levels_by_address : dict[int, FoundLevel]
        Found levels keyed by ROM address.

    Attributes
    ----------
    _tab_widget : QTabWidget
        Tab widget containing the world tree and per-bank block views.
    addresses_by_object_set : dict[int, set[int]]
        Level addresses grouped by object set from the parser.
    levels_by_address : dict[int, FoundLevel]
        Parsed levels keyed by layout address.

    See Also
    --------
    LevelBlockView
        Draws the bank-occupancy view used on each PRG tab.
    """

    def __init__(
        self,
        parent,
        addresses_by_object_set: dict[int, set[int]],
        levels_by_address: dict[int, FoundLevel],
    ):
        """Build the tree and bank tabs for parsed level inspection.

        The constructor turns one parser result into both inspection surfaces
        used by the window. After caching the address maps on the instance, it
        reads the ROM's object-set-to-PRG-bank table, allocates one empty
        ``LevelBlockView`` tab for each referenced bank, appends each parsed
        level range into the tab that owns that level's object set, and then
        inserts a tree tab that groups the same ``FoundLevel`` records by world
        and jump reachability. The rest of the window relies on that staged
        setup: bank tabs inspect ROM occupancy while the tree tab preserves the
        parser's world-map traversal relationships, and both views stay in sync
        because they consume the same cached level data.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        addresses_by_object_set : dict[int, set[int]]
            Level addresses grouped by object set.
        levels_by_address : dict[int, FoundLevel]
            Found levels keyed by ROM address.
        """
        super(LevelViewer, self).__init__(parent, tr("LevelViewer", "level_viewer", "Level Viewer"))

        self.addresses_by_object_set = addresses_by_object_set
        self.levels_by_address = levels_by_address
        self._prg_bank_numbers: list[int] = []

        self._tab_widget = QTabWidget(self)

        self.setCentralWidget(self._tab_widget)

        # get prg numbers for object sets and sort them
        prg_banks_by_object_set = ROM().read(Constants.OFFSET_BY_OBJECT_SET_A000, 16)
        sorted_prg_bank_numbers = list(set(prg_banks_by_object_set[PLAINS_OBJECT_SET:SPADE_BONUS_OBJECT_SET]))
        sorted_prg_bank_numbers.sort()
        self._prg_bank_numbers = sorted_prg_bank_numbers

        # create tab widgets with PRG numbers in their titles
        for prg_number in sorted_prg_bank_numbers:
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(LevelBlockView([]))

            self._tab_widget.addTab(
                scroll_area,
                tr("LevelViewer", "prg_prg_number", "PRG #{prg_number}").format(prg_number=prg_number),
            )

        # got through all levels and assign them to their respective prg tab widget, based on their object set
        for address in sorted(levels_by_address.keys()):
            level = levels_by_address[address]
            tab_index_from_object_set = sorted_prg_bank_numbers.index(prg_banks_by_object_set[level.object_set_number])

            byte_view = self._tab_widget.widget(tab_index_from_object_set).widget()
            byte_view.levels_in_order.append((level.object_set_number, address, level.object_data_length))

        # insert tree view with all levels at the start of the tabs
        self._tab_widget.insertTab(0, self._gen_tree_view(levels_by_address), tr("LevelViewer", "levels", "Levels"))
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh level-viewer labels without rebuilding byte views.

        The window title, levels tab, and PRG-bank tab captions are rebuilt from
        the active catalog. Existing tab widgets, loaded level-byte rows, and
        object-set/address payloads remain stable so localization does not
        change the inspected ROM data.
        """
        self.setWindowTitle(tr("LevelViewer", "level_viewer", "Level Viewer"))

        if self._tab_widget.count():
            self._tab_widget.setTabText(0, tr("LevelViewer", "levels", "Levels"))

        for tab_index, prg_number in enumerate(self._prg_bank_numbers, start=1):
            if tab_index < self._tab_widget.count():
                self._tab_widget.setTabText(
                    tab_index,
                    tr("LevelViewer", "prg_prg_number", "PRG #{prg_number}").format(prg_number=prg_number),
                )

    @staticmethod
    def _gen_tree_view(levels_by_address: dict[int, FoundLevel]) -> QTreeWidget:
        """Build the world and jump-relationship tree for parsed levels.

        Top-level entries are grouped by world, then jump-discovered levels are
        attached beneath the levels that reference them so users can inspect
        reachable level structure instead of a flat address list. The method
        stages that tree in three passes: create world roots, attach levels
        that are directly reachable from world or world-specific map entries,
        then revisit jump destinations until every discovered parent item
        exists. That preserves the same traversal relationships the parser
        found in ROM data when the inspection UI renders them.

        Parameters
        ----------
        levels_by_address : dict[int, FoundLevel]
            Found levels keyed by ROM address.

        Returns
        -------
        QTreeWidget
            Tree widget populated with parsed level relationships.
        """
        tree_widget = QTreeWidget()

        world_tree_items = []
        level_item_by_address: dict[int, QTreeWidgetItem] = {}

        def _get_level_item(address_: int, level_: FoundLevel, parent_: QTreeWidgetItem):
            """Return the tree item for a level address.

            It presents editor data in a dedicated inspection or utility window. The return value exposes the inspected data or widget calculation needed by the utility window.

            Parameters
            ----------
            address_ : int
                Level address used to look up an existing tree item.
            level_ : FoundLevel
                Found level used to populate a new tree item when needed.
            parent_ : QTreeWidgetItem
                Parent tree item that receives newly created level items.

            Returns
            -------
            QTreeWidgetItem
                Existing or newly created tree item for the level address.
            """
            if address_ in level_item_by_address:
                return level_item_by_address[address_]

            if any(position_ not in levels_by_address for position_ in level_.level_offset_positions):
                print(f"{address_:#x}", "accessible from world map")

            print(
                hex(address_),
                level_.object_set_number,
                f"From World: {level_.found_in_world}, Jump: {level_.found_as_jump}, "
                f"World Specific: {level_.is_world_specific}",
            )

            level_item = QTreeWidgetItem()
            level_item.setText(
                0,
                _gen_level_name(address_, level_) + f" @ 0x{address_:x} / 0x{level.enemy_offset:x}",
            )
            parent_.addChild(level_item)

            level_item_by_address[address_] = level_item

            return level_item

        # Step 1: Make world tree items
        for world_num in range(WORLD_COUNT - 1):
            world_item = QTreeWidgetItem(tree_widget)
            world_item.setText(
                0,
                tr("LevelViewer", "world_world_number", "World {world_number}").format(world_number=world_num + 1),
            )

            world_tree_items.append(world_item)

        # Step 2.1: Make Top Level Tree Items
        for address, level in levels_by_address.items():
            if level.found_in_world:
                parent = world_tree_items[level.world_number - 1]
                _get_level_item(address, level, parent)

        # Step 2.2: Make Generic Level Tree Items
        for address, level in levels_by_address.items():
            if level.is_world_specific:
                parent = world_tree_items[level.world_number - 1]
                _get_level_item(address, level, parent)

        # Step 3: Make Jump Level Tree Widgets
        jump_destinations = [(address, level) for address, level in levels_by_address.items() if level.found_as_jump]

        # it is not always a given, that jumped to levels come after jumped from levels, so we might need to go through
        # them multiple times
        while jump_destinations:
            address, level = jump_destinations.pop(0)

            if not all(
                position in level_item_by_address
                for position in level.level_offset_positions
                if position in levels_by_address
            ):
                # not all levels, that jump to this one have widgets yet, so put it back at the end of the list
                jump_destinations.append((address, level))
                continue

            for position in level.level_offset_positions:
                if position in levels_by_address:
                    assert position in level_item_by_address, (
                        hex(address),
                        level,
                        levels_by_address[position],
                        hex(position),
                    )
                    _get_level_item(address, level, level_item_by_address[position])

        tree_widget.expandAll()

        return tree_widget


class ByteView(QWidget):
    """Paint contiguous level data as colored byte regions inside one PRG bank.

    Each entry in ``levels_in_order`` contributes a colored run sized by the
    parsed level length. This gives maintainers a quick occupancy view for one
    bank before the higher-level block view groups those runs into named
    segments. ``LevelViewer`` feeds parsed level ranges into this widget, which
    then becomes the low-level source for both occupancy painting and the more
    human-readable block view layered on top of the same data. The range list
    enters once through the constructor, then each paint pass turns those
    ranges into a bank-relative byte heatmap. Nothing here understands level
    relationships; it is purely the "address ranges to pixels" stage of the
    viewer pipeline, and other classes build richer behavior on top of that
    rendered occupancy data.

    Notes
    -----
    This widget intentionally stops at occupancy. The broader level viewer adds
    grouped regions and hover previews later, but they all start from the same
    "bank ranges become painted bytes" transformation performed here. Its data
    flow is simple and explicit: parsed level ranges enter once, paint events
    read that stored state, and the widget emits a bank-occupancy picture that
    richer viewer layers can build on.

    Parameters
    ----------
    levels_in_order : list[tuple[int, int, int]]
        Ordered list of ``(object_set, level_address, level_length)`` tuples.

    Attributes
    ----------
    _random_colors : list[QColor]
        Stable per-object-set colors used while drawing byte ranges.
    levels_in_order : list[tuple[int, int, int]]
        Tuples describing the bank layout currently being displayed.

    See Also
    --------
    LevelBlockView
        Groups the same ranges into larger labeled regions.
    """

    def __init__(self, levels_in_order: list[tuple[int, int, int]]):
        """Store level ranges and create stable colors for the bank view.

        Parameters
        ----------
        levels_in_order : list[tuple[int, int, int]]
            Levels ordered for display in the byte view.
        """
        super(ByteView, self).__init__()

        self.levels_in_order = levels_in_order
        seed(0)
        self._random_colors = [
            QColor(randint(0, 255), randint(0, 255), randint(0, 255)) for _ in range(ENEMY_ITEM_OBJECT_SET)
        ]

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.setMouseTracking(True)

    def sizeHint(self):
        """Level-viewer bank size for one PRG occupancy surface.

        Width is fixed to the viewer's expected ROM-bank layout, while the
        height follows ``heightForWidth`` so subclasses can present either byte
        cells or grouped regions from the same parsed level ranges.
        That shared sizing contract is what lets the byte-level and grouped
        region views swap into the same scroll area and keep bank-navigation
        workflow stable.

        Returns
        -------
        QSize
            Recommended size for the parent width being laid out.
        """
        return QSize(1000, self.heightForWidth(self.parentWidget().width()))

    @property
    def first_level_start(self):
        """First level address used as this bank view's origin.

        Both byte and grouped-region views measure their layout relative to
        this bank-local origin instead of absolute ROM address zero.
        That keeps one PRG bank visually compact even when the original ROM
        addresses are large, and it keeps bank-level free-space accounting
        consistent across both viewers during the same inspection workflow.

        Returns
        -------
        int
            Absolute ROM address used as the byte-view origin.
        """
        if not self.levels_in_order:
            return PRG_BANK_SIZE

        return self.levels_in_order[0][1]

    def paintEvent(self, event: QPaintEvent):
        """Render one PRG bank as colored byte occupancy cells.

        Each level range is drawn in a stable object-set color, then the rest
        of the bank is filled red to make unused space visually obvious.
        This turns raw ROM bank occupancy into the byte-level free-space view
        that the grouped region view later summarizes and annotates, so data
        flows from raw ranges to grouped region inspection without changing
        banks. The paint pass consumes ``levels_in_order`` exactly as
        ``LevelViewer`` populated it, translates those absolute ROM addresses
        into bank-relative byte positions, and then overlays the unused tail of
        the bank so maintainers can see both occupied and free regions in the
        same coordinate system.

        Parameters
        ----------
        event : QPaintEvent
            Qt event delivered to the widget.
        """
        if not self.levels_in_order:
            return

        painter = QPainter(self)

        byte_side_length = 8

        width = self.width() // byte_side_length
        height = self.height() // byte_side_length

        level_start = level_length = 0

        # draw all level data from 0
        for object_set, level_start, level_length in self.levels_in_order:
            color = self._random_colors[object_set]
            level_start -= self.first_level_start

            for level_byte in range(level_length):
                cur_pos = level_start + level_byte
                x = (cur_pos % width) * byte_side_length
                y = (cur_pos // width) * byte_side_length

                painter.fillRect(x, y, byte_side_length, byte_side_length, color)

        # draw the rest of the memory left in the ROM bank in red
        last_drawn_index = level_start + level_length + 1
        end_of_bank = PRG_BANK_SIZE - ((self.first_level_start - BASE_OFFSET) % PRG_BANK_SIZE)

        print(f"Drawing rest of the bank from {last_drawn_index} to {end_of_bank}")

        for level_byte in range(end_of_bank - last_drawn_index):
            cur_pos = last_drawn_index + level_byte
            x = (cur_pos % width) * byte_side_length
            y = (cur_pos // width) * byte_side_length

            painter.fillRect(x, y, byte_side_length, byte_side_length, QColorConstants.Red)

        # draw the grid over everything
        painter.setPen(QColorConstants.Black)

        for x in range(1, width):
            x *= byte_side_length

            painter.drawLine(x, 0, x, self.height())

        for y in range(1, height):
            y *= byte_side_length

            painter.drawLine(0, y, self.width(), y)


@dataclass
class _Block:
    """Describe one labeled region in the PRG-bank block view.

    ``LevelBlockView`` builds these transient records before each paint pass so
    layout, tooltip lookup, and drawing all refer to the same parsed bank
    regions. They are not persistent model objects; they are short-lived view
    records produced from the byte ranges currently visible in the bank view.
    One parsed ``_Block`` can later supply its label to painting and its level
    tuple to tooltip thumbnail generation. They are the intermediate structure
    that lets ``LevelBlockView`` share one parsed result across layout,
    painting, and hover handling, instead of recomputing separate structures for
    each of those tasks.

    Notes
    -----
    The dataclass keeps the block view's three concerns in sync: parsing,
    labeling, and hover lookup all consume the same transient region record.
    Its workflow value is shared state: once one region is parsed, painting and
    hover handling can both consume that same record without rebuilding it.

    Attributes
    ----------
    color : QColor
        Fill color used for the region.
    level : tuple[int, int, int] | None
        Associated ``(object_set, address, length)`` tuple when the region
        represents a level.
    name : str
        Label shown inside the region.
    size : int
        Region size in bytes.

    See Also
    --------
    LevelBlockView
        Creates and draws these region descriptors.
    """

    color: QColor
    name: str
    size: int
    level: tuple[int, int, int] | None = None


class LevelBlockView(ByteView):
    """Group bank bytes into named regions for level and free-space inspection.

    Unlike ``ByteView``, which paints every byte position, this widget merges
    contiguous runs into readable blocks such as code/unknown areas, level data,
    and unused space. The class turns the raw range list into three maintainer-
    facing behaviors at once: region layout, region painting, and hover-time
    thumbnail lookup for level-backed regions. ``ByteView`` supplies the raw
    ranges, ``_parse_levels_for_blocks`` groups them, and the rest of the class
    reuses that parsed list for hit-testing and painting. This is the "grouped
    regions and metadata affordances" stage of the same viewer
    pipeline, sitting directly between parsed bank ranges and the user's visual
    inspection of free space, level placement, and hover previews.

    Notes
    -----
    The class exists because byte-level occupancy was not enough for people
    trying to understand bank usage. Its job is to turn those same ranges into
    named regions that can be scanned quickly and then inspected further
    through tooltips and thumbnails. The data flow is raw ranges ->
    ``_parse_levels_for_blocks`` -> transient ``_Block`` records -> painting
    and hover inspection.

    Parameters
    ----------
    levels_in_order : list[tuple[int, int, int]]
        Ordered list of ``(object_set, level_address, level_length)`` tuples.

    Attributes
    ----------
    block_height : int
        Height in pixels for one rendered region block.
    block_width : int
        Width in pixels for one rendered region block.

    See Also
    --------
    ByteView
        Lower-level byte occupancy renderer for the same bank data.
    """

    def __init__(self, levels_in_order: list[tuple[int, int, int]]):
        """Initialize region sizing for the bank block view.

        Parameters
        ----------
        levels_in_order : list[tuple[int, int, int]]
            Ordered list of ``(object_set, level_address, level_length)`` tuples.
        """
        super().__init__(levels_in_order)

        self.block_height = 100  # px
        self.block_width = 170  # px

    def heightForWidth(self, width):
        """Height needed for the parsed PRG-bank regions at one width.

        Region count depends on the bank parsing step, so this layout helper
        asks ``_parse_levels_for_blocks`` for the parsed grouping before
        sizing the widget.
        The widget height therefore tracks the human-readable region model that
        painting and hover handling will use, not just the raw byte list.

        Parameters
        ----------
        width : int
            Available widget width in pixels.

        Returns
        -------
        int
            Height required to lay out all parsed blocks.
        """
        if not self.levels_in_order:
            return 600

        block_count = len(self._parse_levels_for_blocks())

        blocks_per_line = max(1, width // self.block_width)

        lines = math.ceil(block_count / blocks_per_line)

        return lines * self.block_height

    def _parse_levels_for_blocks(self):
        """Parse PRG-bank byte ranges into labeled inspection regions.

        Gaps between known levels become explicit unused-space blocks, while the
        prefix before the first level is labeled as code or unknown ROM data.
        The resulting transient records are then reused for layout, painting,
        and tooltip lookup so all three behaviors agree on the same bank
        parsing. The method walks the ordered ROM ranges once, tracks the next
        unassigned byte position inside the bank, emits explicit gap records
        before every level-backed block, and then appends one final unused
        region if the bank does not end on a level boundary.
        This is the parsing step that turns raw level ranges into the named
        PRG-bank regions shown by the grouped inspection view.

        Returns
        -------
        list[_Block]
            Parsed regions in display order.
        """
        potential_blocks: list[_Block] = []

        current_pos = self.first_level_start

        prg_start = (self.first_level_start // PRG_BANK_SIZE) * PRG_BANK_SIZE

        if self.first_level_start != prg_start:
            potential_blocks.append(
                _Block(
                    QColorConstants.Gray,
                    tr("LevelViewer", "address_code_unknown", "{address}: Code/Unknown").format(
                        address=f"0x{prg_start:x}"
                    ),
                    current_pos % PRG_BANK_SIZE,
                )
            )

        for object_set, abs_level_start, level_length in self.levels_in_order:
            if current_pos != abs_level_start:
                potential_blocks.append(
                    _Block(
                        QColorConstants.Red,
                        tr("LevelViewer", "address_unused_space", "{address}: Unused Space").format(
                            address=f"0x{current_pos:x}"
                        ),
                        abs_level_start - current_pos,
                    )
                )
                current_pos = abs_level_start

            potential_blocks.append(
                _Block(
                    self._random_colors[object_set],
                    tr("LevelViewer", "address_object_set", "{address}: {object_set}").format(
                        address=f"0x{abs_level_start:x}",
                        object_set=tr_data_name("ObjectSet", OBJECT_SET_NAMES[object_set]),
                    ),
                    level_length,
                    (object_set, abs_level_start, level_length),
                )
            )
            current_pos += level_length + 1

        if current_pos % PRG_BANK_SIZE != 0:
            rest = PRG_BANK_SIZE - current_pos % PRG_BANK_SIZE

            potential_blocks.append(
                _Block(QColorConstants.Red, tr("LevelViewer", "unused_space", "Unused Space"), rest)
            )

        return potential_blocks

    def _starting_point_by_index(self, index: int):
        """Map one parsed region index onto the grouped bank-view grid.

        The helper converts the parsed region index into the fixed-size tile
        grid used by the grouped bank view.
        That keeps hit testing, tooltips, and painting on the same coordinate
        system used by the visual region layout.

        Parameters
        ----------
        index : int
            Zero-based index of the item to access.

        Returns
        -------
        QPoint
            Top-left pixel position for the indexed region.
        """
        view_width = self.width() // self.block_width * self.block_width

        if view_width < self.block_width:
            x = 0
            y = index

        else:
            blocks_per_line = view_width // self.block_width
            assert blocks_per_line >= 1

            x = index % blocks_per_line
            y = index // blocks_per_line

        return QPoint(x * self.block_width, y * self.block_height)

    def _get_block_at(self, x: int, y: int) -> _Block | None:
        """Resolve widget coordinates to one parsed PRG-bank region.

        Hover handling uses this instead of reparsing tooltip state separately.
        The method is the hit-test bridge between widget coordinates and the
        parsed PRG-bank region metadata that drives labels and thumbnails for
        one ROM bank.
        Hover lookup uses this hit test instead of building a separate tooltip
        model, so the same parsed region record drives both painting and hover
        state. It converts the pointer position into the grouped-view grid,
        rejects coordinates that fall outside the parsed bank layout, and then
        looks up the `_Block` record that painting used for that same screen
        cell.

        Parameters
        ----------
        x : int
            Horizontal coordinate in widget space.
        y : int
            Vertical coordinate in widget space.

        Returns
        -------
        _Block | None
            Region at the queried position, if any.
        """
        blocks_per_line = max(1, self.width() // self.block_width)

        if blocks_per_line * self.block_width < x:
            return None

        blocks = self._parse_levels_for_blocks()
        lines = math.ceil(len(blocks) / blocks_per_line)

        if lines * self.block_height < y:
            return None

        x_offset = x // self.block_width
        y_offset = y // self.block_height

        index = y_offset * blocks_per_line + x_offset

        if index >= len(blocks):
            return None

        return blocks[index]

    def mouseMoveEvent(self, event: QMouseEvent):
        """Refresh the hover thumbnail for the region under the cursor.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        self._set_thumbnail(event.x(), event.y())

        super().mouseMoveEvent(event)

    def _set_thumbnail(self, x: int, y: int):
        """Update the tooltip preview for the region under the cursor.

        Only level-backed regions show thumbnails; code and unused-space blocks
        clear the tooltip instead.

        Parameters
        ----------
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.
        """
        block = self._get_block_at(x, y)

        if block is None or block.level is None:
            self.setToolTip(None)
            return

        image_data = get_level_thumbnail(
            block.level[0],
            block.level[1],
            0x0,
        )

        self.setToolTip(
            f"<b>{block.name}</b><br/>"
            f"<u>{tr('LevelViewer', 'type', 'Type')}:</u> {tr_data_name('ObjectSet', OBJECT_SET_NAMES[block.level[0]])} "
            f"<u>{tr('LevelViewer', 'objects', 'Objects')}:</u> {block.level[1]:#x} "
            f"<img src='data:image/png;base64,{pixmap_to_base64(image_data)}'>"
        )

    def _paint_block(self, painter: QPainter, pos: QPoint, block: _Block):
        """Draw one parsed PRG-bank region into the grouped view.

        The region label and byte count come from the parsed ``_Block`` record
        so painting stays aligned with tooltip lookup and block layout.
        Each rectangle is therefore a direct visual projection of one parsed
        bank region, not a separate view-specific computation.

        The draw step consumes the same parsed region record used by layout and
        hover lookup, keeping the grouped bank workflow on one shared set of
        metadata.

        Parameters
        ----------
        painter : QPainter
            Painter that renders the region.
        pos : QPoint
            Top-left widget position for the region.
        block : _Block
            Parsed region descriptor being drawn.
        """
        rect = QRect(pos, QSize(self.block_width, self.block_height))

        painter.fillRect(rect, QBrush(block.color))

        painter.setPen(QColorConstants.Black)
        painter.drawRect(rect)

        name_pos = pos + QPoint(5, self.block_height // 3)
        size_pos = pos + QPoint(5, 2 * self.block_height // 3)

        painter.drawText(name_pos, block.name)
        painter.drawText(
            size_pos,
            tr("LevelViewer", "size_size_bytes_percent", "Size: {size} Bytes ({percent} %)").format(
                size=block.size,
                percent=round(100 / PRG_BANK_SIZE * block.size, 1),
            ),
        )

    def paintEvent(self, event: QPaintEvent):
        """Paint the parsed PRG-bank regions as labeled blocks.

        Parameters
        ----------
        event : QPaintEvent
            Qt event delivered to the widget.
        """
        p = QPainter(self)

        for index, block in enumerate(self._parse_levels_for_blocks()):
            self._paint_block(p, self._starting_point_by_index(index), block)
