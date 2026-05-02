"""Select a level from stock, discovered, or world-map sources.

This module owns Foundry's broadest level-picking workflow. It combines the
stock address tables, found-level metadata, world-map pointer browsing, and
optional thumbnail previews into one staged selection surface that ultimately
returns an object set plus ROM layout and enemy addresses.

See Also
--------
foundry.gui.dialogs.level_selector.found_level_list
    Found-level source that stages metadata discovered from the active ROM.
foundry.gui.dialogs.level_selector.overworld_selection_map
    World-map source that stages pointer-backed selections from a rendered map.
foundry.gui.dialogs.level_selector.stock_level_list
    Stock-address source used when ROM-managed metadata is unavailable.
"""

from PySide6.QtGui import QCloseEvent, QKeyEvent, QKeySequence, QShortcut, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
)

from foundry import Settings, get_level_thumbnail, icon
from foundry.game.File import ROM
from foundry.gui import OBJECT_SET_ITEM_KEYS, OBJECT_SET_ITEMS
from foundry.gui.localization import tr
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import (
    MUSHROOM_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)
from smb3parse.data_points import LevelPointerData
from smb3parse.levels import HEADER_LENGTH, WORLD_COUNT
from smb3parse.levels.level_header import LevelHeader

from ...settings import LevelPreviewType
from .found_level_list import FoundLevelWidget
from .overworld_selection_map import WorldMapLevelSelect
from .stock_level_list import StockLevelWidget


def _retranslate_object_set_dropdown(dropdown: QComboBox) -> None:
    """Refresh object-set labels without changing the selected encoded index.

    Parameters
    ----------
    dropdown : QComboBox
        Object-set selector whose row indexes are stable SMB3 object-set ids.
        Only visible labels are rewritten during live language switching.
    """
    current_index = dropdown.currentIndex()
    signals_were_blocked = dropdown.blockSignals(True)

    for index, (object_set_item, object_set_key) in enumerate(zip(OBJECT_SET_ITEMS, OBJECT_SET_ITEM_KEYS)):
        if index < dropdown.count():
            dropdown.setItemText(index, tr("Common", object_set_key, object_set_item))

    dropdown.setCurrentIndex(current_index)
    dropdown.blockSignals(signals_were_blocked)


def _should_use_vertical_preview(level_address: int) -> bool:
    """Classify preview orientation from the staged level header.

    The preview orientation is read from the level header stored at
    ``level_address``. Levels with fewer than one screen are also treated as
    vertical so the thumbnail widget uses the narrow preview area.
    This check affects only preview layout. The state flow stays one-way from
    the staged ROM address into the thumbnail widget; the address itself
    remains the selection payload returned by the dialog.

    Parameters
    ----------
    level_address : int
        ROM address of the level layout data.

    Returns
    -------
    bool
        ``True`` when the level header marks the level vertical or has no
        horizontal screens.
    """
    level_header_bytes = ROM().read(level_address, HEADER_LENGTH)

    level_header = LevelHeader(ROM(), level_header_bytes)

    return level_header.is_vertical or level_header.screens < 1


class _LevelPreviewWidget(QScrollArea):
    """Scroll-area wrapper for rendered level thumbnails.

    The selector keeps separate horizontal and vertical preview widgets so each
    can reserve scrollbar space around the generated thumbnail without resizing
    the entire dialog unpredictably. It is a small layout-control wrapper as
    much as a preview surface: level thumbnails can change size drastically as
    the staged addresses or object set change, and this class absorbs those
    size shifts so the selector can show previews without destabilizing the
    rest of the dialog.

    Parameters
    ----------
    vertical : bool, optional
        Whether this preview is laid out beside the selector for vertical
        levels.

    Attributes
    ----------
    _is_vertical : bool
        Whether this widget reserves width for a vertical preview layout.
    _preview_label : QLabel
        Label that owns the rendered thumbnail pixmap.

    Notes
    -----
    The scrollbar push-out logic exists to preserve framing around generated
    thumbnails. Without it, Qt overlays scrollbars on the preview and creates a
    feedback loop where one scrollbar causes the other to become necessary.
    """

    def __init__(self, vertical=False):
        """Create an empty thumbnail preview.

        The widget starts with only its label and scrollbar sizing policy in
        place; actual pixmap content arrives later when the surrounding level
        selector stages a candidate object set plus layout and enemy addresses
        and asks for a preview refresh. The early scrollbar-size adjustment is
        part of that contract because preview widgets need the real scrollbar
        dimensions before they can reserve room for large thumbnails without
        obscuring them. The constructor therefore prepares the stable preview
        frame that later selection changes will reuse, records whether this
        instance participates in the horizontal or vertical branch of the
        selector layout, and binds the shared preview label that later
        thumbnail refreshes mutate. All ROM decoding and thumbnail generation
        stay outside this class; its job is to own the scroll-area state that
        later ``set_level_preview`` calls update after the selector's staged
        addresses change.

        Parameters
        ----------
        vertical : bool, optional
            Whether this preview is laid out beside the selector for vertical
            levels.
        """
        super().__init__()

        self._is_vertical = vertical

        self._preview_label = QLabel()

        self.setWidget(self._preview_label)
        self.setWidgetResizable(True)

        # the scrollbars start with a default size of 100, 100, so adjust the size to get the real size here
        # see _push_out_scrollbars()
        self.verticalScrollBar().adjustSize()
        self.horizontalScrollBar().adjustSize()

    def set_level_preview(self, object_set_number: int, level_address: int, enemy_address: int):
        """Render and display a level thumbnail.

        This is the preview widget's one staging entry point. ``LevelSelector``
        calls it after a stock list, found-level table, or world-map click has
        already collapsed into one staged object set plus layout and enemy
        addresses. The widget then turns that staged triple into a thumbnail,
        resizes the embedded label to the decoded pixmap, and finally expands
        its scroll-area frame so the preview can stay readable without
        destabilizing the rest of the selector layout.

        Parameters
        ----------
        object_set_number : int
            Object set number that selects graphics and object definitions.
        level_address : int
            ROM address of the level layout data.
        enemy_address : int
            ROM address of the level enemy/item data.
        """
        level_preview_pixmap = get_level_thumbnail(object_set_number, level_address, enemy_address)

        self._preview_label.setPixmap(level_preview_pixmap)
        self._preview_label.setFixedSize(level_preview_pixmap.size())

        self._push_out_scrollbars()

    def _push_out_scrollbars(self):
        """When the widget of a scroll area becomes to large, scrollbars are shown. Those are shown over the widget,
        however, without increasing the size of the scroll area. So if one scrollbar becomes necessary, its existence
        makes the other scrollbar also necessary. We forego that by extending the size of the widget by as many pixels
        as are needed for both the frame of the scroll area (linewidth) and the size of the scrollbar.

        This keeps the preview scrollbars offset so level thumbnails stay visually framed.
        """
        if self._is_vertical:
            self._push_out_vertical_scrollbar()

        if not self._is_vertical:
            self._push_out_horizontal_scrollbar()

    def _push_out_horizontal_scrollbar(self):
        """Reserve height for the horizontal preview scrollbar."""
        new_height = self._preview_label.height() + self.lineWidth() * 2

        if self._preview_label.width() > self.width():
            new_height += self.horizontalScrollBar().height()

        self.setFixedHeight(new_height)

    def _push_out_vertical_scrollbar(self):
        """Reserve width for the vertical preview scrollbar."""
        new_width = self._preview_label.width() + self.lineWidth() * 2

        if self._preview_label.height() > self.height():
            new_width += self.verticalScrollBar().width()

        self.setFixedWidth(new_width)


class LevelSelector(QDialog):
    """Select an editable level from stock, discovered, or map sources.

    The dialog stages object set, layout address, enemy address, world index,
    and display name until the user accepts. Unsupported world-map, mushroom
    house, and spade bonus selections are blocked before the caller receives
    the staged addresses.

    Parameters
    ----------
    parent : QWidget
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _found_level_widget : FoundLevelWidget
        Optional table of levels discovered from Foundry ROM metadata.
    _horizontal_level_preview : _LevelPreviewWidget
        Preview area used for horizontal level thumbnails.
    _stock_level_widget : StockLevelWidget
        Stock SMB3 level list and world list tab.
    _vertical_level_preview : _LevelPreviewWidget
        Preview area used for vertical level thumbnails.
    button_cancel : QPushButton
        Button that rejects the dialog.
    button_ok : QPushButton
        Button that accepts a supported level selection.
    clicked_level_pointer : LevelPointerData | None
        Last world-map pointer clicked, used to accept a repeated click.
    enemy_data_label : QLabel
        Label for the enemy data address spinner.
    enemy_data_offset : int
        Enemy data address committed when the dialog is accepted.
    enemy_data_spinner : Spinner
        Editable staged enemy data address.
    level_name : str
        Display name for the staged selection.
    object_data_label : QLabel
        Label for the layout data address spinner.
    object_data_offset : int
        Layout/header address committed when the dialog is accepted.
    object_data_spinner : Spinner
        Editable staged layout/header address.
    object_set : int
        Object set committed when the dialog is accepted.
    object_set_dropdown : QComboBox
        Object set selector used to parse and preview the staged addresses.
    object_set_label : QLabel
        Label for the object set selector.
    source_selector : QTabWidget
        Tab widget containing stock, discovered, and world-map sources.
    world_index : int
        One-based world number for the staged selection.
    """

    def __init__(self, parent):
        """Create the level selection dialog.

        Construction happens in six phases. It first initializes the staged
        selection fields, then builds the shared address and object-set
        controls, then adds the stock, found-level, and world-map source tabs,
        then creates the horizontal and vertical preview widgets, then lays out
        the dialog and keyboard shortcuts, and finally seeds the first visible
        selection before connecting the preview-refresh signals. That ordering
        matters because all sources feed the same staged object-set and address
        controls, while preview generation is intentionally connected only after
        the initial auto-selection so the dialog does not render redundant
        thumbnails during startup. Once construction is complete, every source
        widget funnels through ``fill_in_data`` into one shared staged triple
        of object set, layout address, and enemy address, and the accept path
        reads only that staged triple back out. That means the constructor is
        doing more than laying out widgets: it establishes the routing between
        heterogeneous ROM-backed sources, the shared staged state they mutate,
        and the preview widgets that reflect that staged state before the
        caller commits to opening a level. Future changes need to preserve that
        order so startup stays deterministic and selection changes always flow
        through one path before ``_on_ok`` commits the result.

        Parameters
        ----------
        parent : QWidget
            Parent Qt widget that owns this object.
        """
        super(LevelSelector, self).__init__(parent)

        self.setWindowTitle(tr("LevelSelector", "level_selector", "Level Selector"))
        self.setModal(True)

        self.level_name = ""

        self.object_set = 0
        self.world_index = 0
        self.object_data_offset = 0x0
        self.enemy_data_offset = 0x0

        self.clicked_level_pointer: LevelPointerData | None = None

        self.enemy_data_label = QLabel(parent=self, text=tr("LevelSelector", "enemy_data", "Enemy Data"))
        self.enemy_data_spinner = Spinner(parent=self)

        self.object_data_label = QLabel(parent=self, text=tr("LevelSelector", "object_data", "Object Data"))
        self.object_data_spinner = Spinner(self)

        self.object_set_label = QLabel(parent=self, text=tr("LevelSelector", "object_set", "Object Set"))
        self.object_set_dropdown = QComboBox(self)
        self.object_set_dropdown.addItems(
            [
                tr("Common", object_set_key, object_set_item)
                for object_set_item, object_set_key in zip(OBJECT_SET_ITEMS, OBJECT_SET_ITEM_KEYS)
            ]
        )
        self.object_set_dropdown.currentTextChanged.connect(self._on_object_set_change)

        self.button_ok = QPushButton(tr("Common", "ok_title", "Ok"), self)
        self.button_ok.setEnabled(False)
        self.button_ok.clicked.connect(self._on_ok)
        self.button_ok.setFocus()

        self.button_cancel = QPushButton(tr("Common", "cancel", "Cancel"), self)
        self.button_cancel.clicked.connect(self.close)

        # adding the tabs
        self.source_selector = QTabWidget()

        tab_index = 0

        self._stock_level_widget = StockLevelWidget()

        self._stock_level_widget.world_list.itemDoubleClicked.connect(self._on_ok)
        self._stock_level_widget.level_list.itemDoubleClicked.connect(self._on_ok)

        self._stock_level_widget.level_list.itemSelectionChanged.connect(self._on_stock_level_selected)

        self.source_selector.addTab(self._stock_level_widget, tr("LevelSelector", "stock_levels", "Stock Levels"))
        self.source_selector.setTabIcon(tab_index, icon("list.svg"))

        tab_index += 1

        if ROM.additional_data.found_levels:
            self._found_level_widget = FoundLevelWidget()
            self._found_level_widget.level_table.itemSelectionChanged.connect(self._on_found_level_selected)
            self._found_level_widget.level_table.itemDoubleClicked.connect(self._on_ok)

            self.source_selector.addTab(self._found_level_widget, tr("LevelSelector", "found_levels", "Found Levels"))
            self.source_selector.setTabIcon(tab_index, icon("list.svg"))
            tab_index += 1

        for world_number in range(1, WORLD_COUNT):
            world_map_select = WorldMapLevelSelect(world_number)
            world_map_select.level_clicked.connect(self._on_level_selected_via_world_map)
            world_map_select.level_selected.connect(self._on_level_selected_via_world_map)
            world_map_select.level_selected.connect(self._on_ok)

            self.source_selector.addTab(
                world_map_select,
                tr("LevelSelector", "world_world_number", "World {world_number}").format(world_number=world_number),
            )
            self.source_selector.setTabIcon(tab_index + world_number - 1, icon("globe.svg"))

        # show world 1 by default
        if self.source_selector.count() > tab_index:
            self.source_selector.setCurrentIndex(tab_index)

        # level previews
        self._horizontal_level_preview = _LevelPreviewWidget()
        self._horizontal_level_preview.hide()

        self._vertical_level_preview = _LevelPreviewWidget(vertical=True)
        self._vertical_level_preview.hide()

        data_layout = QGridLayout()

        data_layout.addWidget(self.enemy_data_label, 0, 0)
        data_layout.addWidget(self.object_data_label, 0, 1)
        data_layout.addWidget(self.enemy_data_spinner, 1, 0)
        data_layout.addWidget(self.object_data_spinner, 1, 1)

        data_layout.addWidget(self.object_set_label, 2, 0)
        data_layout.addWidget(self.object_set_dropdown, 2, 1)

        data_layout.addWidget(self.button_ok, 3, 0)
        data_layout.addWidget(self.button_cancel, 3, 1)

        selection_layout = QVBoxLayout()
        selection_layout.addWidget(self.source_selector)
        selection_layout.addWidget(self._horizontal_level_preview)
        selection_layout.addLayout(data_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(selection_layout)
        main_layout.addWidget(self._vertical_level_preview)

        self.setLayout(main_layout)

        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_PageUp), self, self._one_tab_left)
        QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_PageDown),
            self,
            self._one_tab_right,
        )
        QShortcut(QKeySequence(Qt.Key.Key_Return), self, self._on_ok)
        QShortcut(QKeySequence(Qt.Key.Key_Enter), self, self._on_ok)

        if ROM.additional_data.found_levels:
            self._on_found_level_selected()
        else:
            self._on_stock_level_selected()

        # connect here, so we don't trigger the level preview on the automatically selected levels
        self.enemy_data_spinner.valueChanged.connect(self._update_level_preview)
        self.object_data_spinner.valueChanged.connect(self._update_level_preview)
        self.object_set_dropdown.currentTextChanged.connect(self._update_level_preview)

    def _one_tab_left(self):
        """Move selection to the previous source tab, wrapping at the start."""
        current_index = self.source_selector.currentIndex()
        tab_count = self.source_selector.count()

        new_index = (current_index - 1) % tab_count

        self.source_selector.setCurrentIndex(new_index)

    def _one_tab_right(self):
        """Move selection to the next source tab, wrapping at the end."""
        current_index = self.source_selector.currentIndex()
        tab_count = self.source_selector.count()

        new_index = (current_index + 1) % tab_count

        self.source_selector.setCurrentIndex(new_index)

    def retranslate_ui(self) -> None:
        """Refresh visible dialog text while preserving staged selection data.

        The selector rewrites labels, source-tab titles, object-set display
        names, and child widgets in place. The staged object set, level/enemy
        addresses, selected source tab, and clicked world-map pointer remain
        the same stable data payloads, so live language switching cannot alter
        the level that would be returned from the dialog.
        """
        self.setWindowTitle(tr("LevelSelector", "level_selector", "Level Selector"))
        self.enemy_data_label.setText(tr("LevelSelector", "enemy_data", "Enemy Data"))
        self.object_data_label.setText(tr("LevelSelector", "object_data", "Object Data"))
        self.object_set_label.setText(tr("LevelSelector", "object_set", "Object Set"))
        self.button_ok.setText(tr("Common", "ok_title", "Ok"))
        self.button_cancel.setText(tr("Common", "cancel", "Cancel"))
        _retranslate_object_set_dropdown(self.object_set_dropdown)

        for index in range(self.source_selector.count()):
            widget = self.source_selector.widget(index)
            if widget is self._stock_level_widget:
                self.source_selector.setTabText(index, tr("LevelSelector", "stock_levels", "Stock Levels"))
            elif hasattr(self, "_found_level_widget") and widget is self._found_level_widget:
                self.source_selector.setTabText(index, tr("LevelSelector", "found_levels", "Found Levels"))
            elif isinstance(widget, WorldMapLevelSelect):
                world_number = index
                if hasattr(self, "_found_level_widget"):
                    world_number -= 1
                self.source_selector.setTabText(
                    index,
                    tr("LevelSelector", "world_world_number", "World {world_number}").format(world_number=world_number),
                )

            retranslate = getattr(widget, "retranslate_ui", None)
            if callable(retranslate):
                retranslate()

    def _on_object_set_change(self, _):
        """Enable accepting only for editable object sets.

        Parameters
        ----------
        _ : str
            New combo-box text emitted by Qt.
        """
        self.button_ok.setEnabled(self.object_set_dropdown.currentIndex() != WORLD_MAP_OBJECT_SET)

    def keyPressEvent(self, key_event: QKeyEvent):
        """Reject the dialog when Escape is pressed.

        Parameters
        ----------
        key_event : QKeyEvent
            Key event being handled.
        """
        if key_event.key() == Qt.Key.Key_Escape:
            self.reject()

    def goto_world(self, world_number: int):
        # default to world 1's tab
        """Select the tab and stock list for a world.

        Parameters
        ----------
        world_number : int
            One-based SMB3 world number to show.
        """
        tab_index = 1

        # if we got a valid world number, navigate to its tab
        if world_number in range(1, WORLD_COUNT + 1):
            tab_index = world_number

        if ROM.additional_data.found_levels:
            # if found levels are present, we added another tab in front of the world tabs
            tab_index += 1

        self.source_selector.setCurrentIndex(tab_index)

        self._stock_level_widget.world_number = world_number

    def deactivate_level_list(self):
        """Disable the stock-level source tab."""
        self.source_selector.setTabEnabled(0, False)

    def _on_stock_level_selected(self):
        """Stage the selected stock-table level in the shared controls.

        Stock rows feed their object set and addresses into the same editable
        controls used by found-level and world-map sources so the accept path
        only has one set of staged fields to read.
        """
        self.world_index = self._stock_level_widget.world_number
        self.level_name = self._stock_level_widget.level_name

        self.enemy_data_spinner.setDisabled(self._stock_level_widget.level_is_overworld)
        self.button_ok.setDisabled(self._stock_level_widget.level_is_overworld)

        self.fill_in_data(
            self._stock_level_widget.object_set_number,
            self._stock_level_widget.level_address,
            self._stock_level_widget.enemy_address,
        )

    def fill_in_data(self, object_set: int, layout_address: int, enemy_address: int):
        """Stage addresses and object set in the editable controls.

        Signals are blocked while values are copied in so address staging does
        not recursively trigger selection handlers; the preview is refreshed once
        the full triple has been staged.

        Parameters
        ----------
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        layout_address : int
            ROM address of the level or world map layout data.
        enemy_address : int
            ROM address of the enemy/item data.
        """
        self.object_set_dropdown.blockSignals(True)
        self.object_data_spinner.blockSignals(True)
        self.enemy_data_spinner.blockSignals(True)

        self.object_set_dropdown.setCurrentIndex(object_set)
        self.object_data_spinner.setValue(layout_address)
        self.enemy_data_spinner.setValue(enemy_address)

        self.object_set_dropdown.blockSignals(False)
        self.object_data_spinner.blockSignals(False)
        self.enemy_data_spinner.blockSignals(False)

        self._update_level_preview()

    def _update_level_preview(self):
        # make into a global helper function?
        """Refresh the thumbnail preview for the staged editable level.

        Preview rendering is skipped when the user disables widget previews or
        when the staged object set is a world map, mushroom house, or spade
        bonus set. Otherwise the method chooses the horizontal or vertical
        preview widget based on the staged layout header, renders the thumbnail
        for the staged addresses, and then resizes the dialog around the active
        preview surface. In practice this is the fan-in point where stock-list,
        found-level, world-map, spinner, and object-set changes all converge:
        every selection source updates the same staged controls first, and this
        method turns that staged state into one consistent preview outcome.
        """
        app_settings = Settings("mchlnix", "foundry")

        if app_settings.value("editor/level_preview_type") != LevelPreviewType.WIDGET:
            return

        self._horizontal_level_preview.hide()
        self._vertical_level_preview.hide()

        object_set = self.object_set_dropdown.currentIndex()
        layout_address = self.object_data_spinner.value()
        enemy_address = self.enemy_data_spinner.value()

        if object_set in [
            WORLD_MAP_OBJECT_SET,
            MUSHROOM_OBJECT_SET,
            SPADE_BONUS_OBJECT_SET,
        ]:
            return

        if _should_use_vertical_preview(layout_address):
            preview_widget = self._vertical_level_preview
        else:
            preview_widget = self._horizontal_level_preview

        preview_widget.set_level_preview(object_set, layout_address, enemy_address)
        preview_widget.show()

        self.adjustSize()

    def _on_level_selected_via_world_map(self, level_name: str, level_pointer: LevelPointerData):
        """Stage the level pointer selected from a world-map tab.

        Re-clicking the same pointer accepts immediately, which makes map
        selection behave like a double-click source without requiring separate
        per-tab state.

        Parameters
        ----------
        level_name : str
            Display name for the level.
        level_pointer : LevelPointerData
            World-map pointer carrying object set, layout address, enemy
            address, and world metadata.
        """
        self.level_name = level_name

        if self.clicked_level_pointer == level_pointer:
            # same level was clicked again,
            self._on_ok()
        else:
            self.clicked_level_pointer = level_pointer

        self.world_index = level_pointer.world.index + 1

        self.fill_in_data(
            level_pointer.object_set,
            level_pointer.level_address,
            level_pointer.enemy_address,
        )

        self.button_ok.setEnabled(True)
        self.button_ok.setFocus()

    def _on_found_level_selected(self):
        """Stage the selected discovered level in the shared controls.

        Found-level rows already carry parsed object set and address metadata,
        so the handler only needs to copy those values into the common staging
        controls and enable acceptance.
        """
        self.fill_in_data(
            self._found_level_widget.object_set_number,
            self._found_level_widget.level_address,
            self._found_level_widget.enemy_address,
        )

        self.world_index = self._found_level_widget.world_number

        self.button_ok.setEnabled(True)
        self.button_ok.setFocus()

    def _on_ok(self, _=None):
        """Accept the staged level when it is editable.

        Parameters
        ----------
        _ : object, optional
            Optional Qt signal payload.
        """
        if self.object_set_dropdown.currentIndex() == WORLD_MAP_OBJECT_SET:
            return

        if self.object_set_dropdown.currentIndex() in (
            MUSHROOM_OBJECT_SET,
            SPADE_BONUS_OBJECT_SET,
        ):
            QMessageBox.warning(
                self,
                tr("LevelSelector", "no_can_do", "No can do"),
                tr(
                    "LevelSelector",
                    "error.unsupported_bonus_level",
                    "Spade and mushroom house levels are currently not supported, and can't be edited.",
                ),
            )
            return

        self.object_set = self.object_set_dropdown.currentIndex()
        self.object_data_offset = self.object_data_spinner.value()
        self.enemy_data_offset = self.enemy_data_spinner.value()

        self.accept()

    def closeEvent(self, _close_event: QCloseEvent):
        """Reject the dialog when the window is closed.

        Parameters
        ----------
        _close_event : QCloseEvent
            Qt close event.
        """
        self.reject()
