"""Coordinate the Scribe tool-window tabs for world-map editing.

This module defines :class:`ToolWindow`, the small auxiliary window that
collects the world-map editing tools used by Scribe. The window owns the tab
container for tile picking, level-pointer editing, sprite selection, and lock
editing, then re-emits each tool's selection signal for the rest of the GUI.

The tool window sits between the shared :class:`~foundry.game.level.LevelRef`
state and the per-tool widgets in :mod:`scribe.gui.tool_window`. Maintainers
usually read this file first when tracing how world-map tool selections are
assembled into one Qt window, then continue into
``scribe.gui.tool_window.block_picker`` or the table-based list widgets for the
tool-specific workflows.

See Also
--------
scribe.gui.tool_window.block_picker
    Tile-picking workflow and zoom handling for world-map tiles.
scribe.gui.tool_window.level_pointer_list
    Editable list of world-map level pointers shown in the tool window.
scribe.gui.tool_window.sprite_list
    Editable list of world-map sprites shown in the tool window.
scribe.gui.tool_window.locks_list
    Editable list of lock and bridge objects shown in the tool window.
"""

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.localization import tr
from scribe.gui.tool_window.block_picker import BlockPicker
from scribe.gui.tool_window.level_pointer_list import LevelPointerList
from scribe.gui.tool_window.locks_list import LocksList
from scribe.gui.tool_window.sprite_list import SpriteList

TR_KEY_CONTEXT = "scribe.tool_window"


class ToolWindow(QMainWindow):
    """Host the tabbed tool widgets used by Scribe's world-map editor.

    ``ToolWindow`` is the composition point for the tool-side widgets that
    operate on one world-map session. It wires each tab to the same
    :class:`LevelRef`, exposes a small set of selection signals for the rest of
    the GUI, and keeps the tool window visually focused on one editing mode at
    a time.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns the floating tool window.
    level_ref : LevelRef
        Shared level reference that supplies world-map data and change signals
        to every tab in the window for the open map session.

    Attributes
    ----------
    level_ref : LevelRef
        Shared level model passed through to each tool tab.
    tabbed_widget : QTabWidget
        Central tab container that presents the available world-map tools.
    tile_picker : BlockPicker
        Tile-selection tab for choosing map blocks and adjusting block zoom.
    level_pointer_list : LevelPointerList
        Tabular editor for level pointers on the active world map.
    sprite_list : SpriteList
        Tabular editor for world-map sprite entries.
    locks_list : LocksList
        Tabular editor for lock and bridge entries.
    tile_selected : SignalInstance
        Re-emitted when the tile picker chooses a tile ID.
    sprite_selection_changed : SignalInstance
        Re-emitted when the sprite list changes its selected row.
    level_pointer_selection_changed : SignalInstance
        Re-emitted when the level-pointer list changes its selected row.
    locks_selection_changed : SignalInstance
        Re-emitted when the locks list changes its selected row.

    Notes
    -----
    The window clears list selections whenever the selected tab changes. That
    keeps only the active tool's selection highlighted, which matches the
    world-map workflow where pointer, sprite, and lock selections share the
    same editing surface.
    """

    tile_selected: SignalInstance = Signal(int)
    """Is fired, when a tile has been selected through the tile picker. int-argument is the tile id."""

    sprite_selection_changed: SignalInstance = Signal(int)
    level_pointer_selection_changed: SignalInstance = Signal(int)
    locks_selection_changed: SignalInstance = Signal(int)

    def __init__(self, parent: QWidget | None, level_ref: LevelRef):
        """Initialize the tabbed tool window for one shared level reference.

        The constructor configures the window chrome, creates each tool tab
        against the shared level reference, re-emits their selection signals,
        and installs the tab widget as the window's central content. The setup
        happens in three phases: configure the floating tool-window flags,
        create and connect the individual tabs, then register tab-change hooks
        that clear inactive list selections. Those hooks keep the rest of the
        editor synchronized with one visible world-map selection mode.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this floating tool window.
        level_ref : LevelRef
            Shared level reference consumed by every tab to read and mutate the
            active world-map state.

        Notes
        -----
        Initialization follows one fixed sequence: configure the floating
        window flags, build each per-tool widget against ``level_ref``, bridge
        each widget's selection signal back onto the tool-window signals, then
        register tab-change hooks that clear selections from inactive list
        tabs. That sequencing matters because the rest of the editor treats the
        tool window as one coordinated selection surface rather than four
        independent widgets with competing highlighted rows.
        """
        super(ToolWindow, self).__init__(parent)

        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)

        self.setWindowTitle(tr(TR_KEY_CONTEXT, "window.title"))

        self.level_ref = level_ref

        self.tabbed_widget = QTabWidget()

        self.tile_picker = BlockPicker(self, level_ref)
        self.tile_picker.tile_selected.connect(self.tile_selected.emit)

        self.level_pointer_list = LevelPointerList(self, level_ref)
        self.level_pointer_list.selection_changed.connect(self.level_pointer_selection_changed.emit)

        self.sprite_list = SpriteList(self, level_ref)
        self.sprite_list.selection_changed.connect(self.sprite_selection_changed.emit)

        self.locks_list = LocksList(self, level_ref)
        self.locks_list.selection_changed.connect(self.locks_selection_changed.emit)

        self.tabbed_widget.addTab(self.tile_picker, tr(TR_KEY_CONTEXT, "tab.tiles"))
        self.tabbed_widget.addTab(self.level_pointer_list, tr(TR_KEY_CONTEXT, "tab.level_pointers"))
        self.tabbed_widget.addTab(self.sprite_list, tr(TR_KEY_CONTEXT, "tab.sprites"))
        self.tabbed_widget.addTab(self.locks_list, tr(TR_KEY_CONTEXT, "tab.locks_bridges"))

        # clear selection if you change the tab
        self.tabbed_widget.currentChanged.connect(lambda _: self.level_pointer_list.clearSelection())
        self.tabbed_widget.currentChanged.connect(lambda _: self.sprite_list.clearSelection())
        self.tabbed_widget.currentChanged.connect(lambda _: self.locks_list.clearSelection())

        self.setCentralWidget(self.tabbed_widget)

    def retranslate_ui(self) -> None:
        """Refresh tool-window labels after a language change.

        The tool window owns the live-translation workflow for tab titles and
        delegates detailed refreshes to the table-based child widgets.
        Selection signals, tab ordering, and the shared ``LevelRef`` remain
        unchanged, so label updates stay at the display boundary without
        disturbing selected rows, undo state, or the active editing mode.
        """
        self.setWindowTitle(tr(TR_KEY_CONTEXT, "window.title"))
        self.tabbed_widget.setTabText(0, tr(TR_KEY_CONTEXT, "tab.tiles"))
        self.tabbed_widget.setTabText(1, tr(TR_KEY_CONTEXT, "tab.level_pointers"))
        self.tabbed_widget.setTabText(2, tr(TR_KEY_CONTEXT, "tab.sprites"))
        self.tabbed_widget.setTabText(3, tr(TR_KEY_CONTEXT, "tab.locks_bridges"))
        self.level_pointer_list.retranslate_ui()
        self.sprite_list.retranslate_ui()
        self.locks_list.retranslate_ui()

    def set_zoom(self, zoom_level: int = 2) -> None:
        """Forward a new block-picker zoom level to the tile tab.

        Parameters
        ----------
        zoom_level : int, default: 2
            Zoom factor applied to the block bank shown by the tile picker.
            Other tabs ignore this value because only the tile workflow renders
            block graphics at a scalable size.

        Notes
        -----
        Zoom is display state owned by the tile picker. Forwarding it here
        keeps the main window from reaching into the picker internals and does
        not affect undo, ROM persistence, or selected tool payloads.
        """
        self.tile_picker.set_zoom(zoom_level)
