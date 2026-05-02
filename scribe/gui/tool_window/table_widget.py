"""Provide Scribe table widgets and item delegates for world-map editing.

This module adapts Foundry's generic table widget support to Scribe's world
overview editors. :class:`TableWidget` sits between the shared
:class:`~foundry.game.level.LevelRef` model and the concrete tool-window tables:
level-ref signals and undo-stack moves trigger row rebuilds, row rebuilds ask
for tile previews from the active :class:`~foundry.game.level.WorldMap`, and
delegate editors commit per-cell edits back into the table model. The delegate
classes supply the editing widgets that those tool-window tables use for
enumerated choices, numeric fields, and informational dialogs.

See Also
--------
foundry.gui.widgets.table_widget.TableWidget
    Base drag-and-drop table behavior reused by the Scribe tool window.
scribe.gui.tool_window.tool_window
    Hosts the concrete tables that populate these delegates and respond to
    their edits.
"""

from typing import cast

from PySide6.QtCore import QAbstractItemModel, QSize, Signal, SignalInstance
from PySide6.QtGui import QImage, QPainter, QPixmap, QUndoStack
from PySide6.QtWidgets import (
    QComboBox,
    QMessageBox,
    QStyledItemDelegate,
    QTableWidgetItem,
    QWidget,
)

from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.widgets.Spinner import SPINNER_MAX_VALUE, Spinner
from foundry.gui.widgets.table_widget import TableWidget as FoundryTableWidget


class TableWidget(FoundryTableWidget):
    """Share world-aware table behavior across Scribe tool-window editors.

    Concrete Scribe tables inherit this class so they can project the same
    shared world-edit timeline into different row layouts without reimplementing
    signal wiring, undo-history tracking, or tile preview helpers.

    Parameters
    ----------
    parent : QWidget
        Parent widget that owns the table inside the tool window.
    level_ref : LevelRef
        Shared world reference that emits change notifications whenever the
        active world, palette, or backing data changes.

    Attributes
    ----------
    selection_changed : SignalInstance
        Signal emitted by subclasses when the selected row should focus a
        matching world object elsewhere in the editor.
    level_ref : LevelRef
        Shared level reference that supplies the active world map and editor
        change notifications.

    Notes
    -----
    The base class handles drag/drop behavior and icon sizing here so concrete
    Scribe tables can focus on row-specific model updates in
    :meth:`update_content`. It also centralizes the signal wiring that keeps
    every world table synchronized with the same level-ref and undo-history
    timeline.
    """

    selection_changed: SignalInstance = Signal(int)

    def __init__(self, parent, level_ref: LevelRef):
        """Configure shared repaint triggers for a world-editing table.

        This constructor establishes the table as a passive view over the
        shared world state: it stores the level reference, subscribes to every
        model signal that can invalidate visible rows, and subscribes to
        undo-stack moves so replayed commands rebuild against the same data.

        Parameters
        ----------
        parent : QWidget
            Parent widget that owns the table instance.
        level_ref : LevelRef
            Shared reference whose signals announce when the loaded world map,
            palette, or serialized data changed and the visible rows need to
            be regenerated.

        Notes
        -----
        The constructor wires every world-change signal and the undo-stack
        cursor to :meth:`update_content`. Subclasses therefore only need to
        rebuild their rows when asked. The resulting flow is: a world edit or
        undo-stack move updates the shared model state, the signal lands here,
        and the subclass rebuilds its rows against the new world snapshot.
        """
        super(TableWidget, self).__init__(parent)

        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setIconSize(QSize(32, 32))

        self.level_ref = level_ref

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.palette_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.undo_stack.indexChanged.connect(self.update_content)

    @property
    def world(self) -> WorldMap:
        """Expose the world map that row rebuilds and icon previews consume.

        Concrete tables and helper methods use this property as the handoff
        from level-ref coordination into direct world-model reads. It keeps row
        generation, icon rendering, and edit targeting aligned with the same
        world object that emitted the most recent change signal. That means a
        row rebuild triggered by :attr:`level_ref` and a delegate commit that
        immediately asks for tile or level data both resolve through the same
        current world snapshot instead of caching their own copies.

        Returns
        -------
        foundry.game.level.WorldMap.WorldMap
            The world model currently exposed through ``level_ref``.
        """
        return self.level_ref.level

    @property
    def undo_stack(self) -> QUndoStack:
        """Resolve the shared undo stack that drives table refreshes.

        Table widgets query the enclosing editor instead of storing their own
        stack so every delegate commit, row move, and external command refresh
        against the same history position.

        Returns
        -------
        QUndoStack
            Undo stack registered by the parent editor window.

        Notes
        -----
        Scribe tables do not own independent history. They query the enclosing
        window so drag/drop edits, delegate edits, and external commands all
        repaint against the same undo or redo position.
        """
        return cast(QUndoStack, self.window().parent().findChild(QUndoStack, "undo_stack"))

    def update_content(self):
        """Rebuild the visible rows for the latest world-editing state.

        Notes
        -----
        Subclasses override this hook to regenerate table items after world
        changes, palette changes, serialized-data changes, or undo-stack moves.
        The base implementation is intentionally empty because each concrete
        table chooses its own row layout, delegates, and selection-to-world
        focus behavior.
        """
        pass

    def _set_map_tile_as_icon(self, item: QTableWidgetItem, pos: tuple[int, int]):
        """Render a world-map tile into a table cell icon.

        Subclasses call this helper while rebuilding rows so a table item can
        mirror the referenced world tile without duplicating palette lookup and
        pixmap creation logic.

        Parameters
        ----------
        item : QTableWidgetItem
            Table item that should receive the rendered icon.
        pos : tuple[int, int]
            Tile position inside the active world map.

        Notes
        -----
        The helper exits early for out-of-bounds points so subclasses can call
        it while rebuilding mixed tables without duplicating boundary checks.
        Rendering uses the active world palette so undo, redo, and palette
        edits keep the icon preview synchronized with the map model.
        """
        if not self.world.point_in(*pos):
            return

        block_icon = QPixmap(self.iconSize())

        painter = QPainter(block_icon)
        get_worldmap_tile(self.world.tile_at(*pos), self.world.data.palette_index).draw(
            painter, 0, 0, self.iconSize().width()
        )
        painter.end()

        item.setIcon(block_icon)


class DropdownDelegate(QStyledItemDelegate):
    """Create combo-box editors for enumerated table fields.

    The delegate turns table cells that store constrained world-edit choices
    into popup selectors, optionally pairing each choice with a rendered icon.
    In the tool-window workflow it bridges a row model's stored value and the
    curated set of values that the user is allowed to commit.

    Parameters
    ----------
    parent : QWidget
        Table view that owns the delegate.
    items : list[str]
        Display names inserted into the combo box for each selectable value.
    icons : list[QImage] | None, optional
        Optional preview images aligned with ``items`` for tile or sprite
        driven selections.
    data : list[object] | None, optional
        Optional stable payloads aligned with ``items`` by index. When
        supplied, delegate commits use these values rather than translated
        display labels.

    Attributes
    ----------
    _items : list[str]
        Ordered labels inserted into each combo-box editor.
    _data : list[object] | None
        Stable row payloads aligned with ``_items``.
    _icons : list[QImage]
        Optional preview images aligned with ``_items`` by index.

    See Also
    --------
    TableWidget
        Host table base that installs delegates for concrete world editors.
    """

    def __init__(
        self,
        parent,
        items: list[str],
        icons: list[QImage] | None = None,
        data: list[object] | None = None,
    ):
        """Capture dropdown choices and optional preview art.

        The stored choices become the immutable editing contract for every cell
        that uses this delegate. Each editor instance is therefore rebuilt from
        one stable source of truth instead of inferring choices from ad hoc row
        state.

        Parameters
        ----------
        parent : QWidget
            Table view that installs the delegate.
        items : list[str]
            Ordered labels shown in the popup editor.
        icons : list[QImage] | None, optional
            Preview art matched by position to ``items``. When omitted, the
            delegate creates a plain text combo box.
        data : list[object] | None, optional
            Stable values stored in each combo-box row while ``items`` remains
            the translated display label.

        Notes
        -----
        ``items``, ``icons``, and ``data`` are parallel sequences. If stable
        ``data`` is provided, it must use the same order as the visible labels
        and optional icons so translated text can change without altering the
        committed command value.
        """
        super(DropdownDelegate, self).__init__(parent)

        self._items = items
        self._data = data

        if icons is None:
            self._icons = []
        else:
            self._icons = icons

    def createEditor(self, parent: QWidget, option, index) -> QWidget:
        """Build the combo-box editor used for a table cell.

        Qt calls this when a world-table cell enters edit mode. The delegate
        turns the row's constrained value set into a popup selector and
        attaches icon previews when the surrounding table is representing tiles
        or sprites. This is the point where display labels, preview art, and
        model-backed choices are bundled into one editing surface.

        Parameters
        ----------
        parent : QWidget
            Parent widget provided by Qt for the editor instance.
        option
            Unused Qt style option for the editor request.
        index
            Model index being edited.

        Returns
        -------
        QWidget
            Combo box populated with the configured labels and optional icons.

        Notes
        -----
        The editor is rebuilt from ``_items`` and ``_icons`` each time Qt
        enters edit mode so the row model does not need to own widget state.
        That keeps delegate commits deterministic: the model provides the cell
        value, this hook provides the allowed choices, and the selected result
        goes back through the table's normal item-change flow.
        """
        combobox = QComboBox(parent)
        combobox.currentTextChanged.connect(lambda _: combobox.clearFocus())

        if not self._icons:
            for index, name in enumerate(self._items):
                combobox.addItem(name, self._item_data(index))
        else:
            for index, (icon, name) in enumerate(zip(self._icons, self._items)):
                combobox.addItem(QPixmap(icon.scaled(32, 32)), name, self._item_data(index))

        combobox.setIconSize(QSize(32, 32))

        return combobox

    def _item_data(self, index: int) -> object | None:
        """Resolve stable payload data for one visible dropdown row.

        This helper is the delegate's display/data boundary. Translated labels
        may change during live retranslation, but command payloads come from
        the parallel ``_data`` sequence so encoded sprite, item, object-set, or
        tile ids remain stable through the commit workflow.

        Parameters
        ----------
        index : int
            Position of the visible dropdown row.

        Returns
        -------
        object | None
            Stable payload from ``_data`` when one was supplied, otherwise
            ``None`` so Qt uses the display text only.

        """
        if self._data is None:
            return None
        return self._data[index]

    def setEditorData(self, editor, index):
        """Synchronize the combo-box editor with the cell's stored value.

        This method bridges the row model's persisted display value and the
        transient combo-box selection that Qt presents for one edit session.
        It ensures the editor opens already aligned with the cell's current
        choice before the user picks a replacement.

        Parameters
        ----------
        editor
            Editor widget created by :meth:`createEditor`.
        index
            Model index whose display value should be selected.

        Notes
        -----
        The method seeds the combo box from the row model and then opens the
        popup immediately so table edits behave like a direct choice action
        instead of a two-step click-then-open workflow. That keeps enumerated
        world edits feeling like a controlled pick list instead of a free-form
        widget embedded inside the table. In practice this is the handoff from
        one persisted table value to the transient editor state that the user
        will confirm or replace during the same edit interaction.
        """
        assert isinstance(editor, QComboBox)

        editor.setCurrentText(index.data())

        editor.showPopup()


class SpinBoxDelegate(QStyledItemDelegate):
    """Create numeric editors for world-table cells.

    The delegate normalizes numeric table edits so world-data fields can be
    edited through the same spinner widget regardless of whether the backing
    model stores decimal values or hex text. In the tool-window workflow it
    owns the conversion boundary between model storage and numeric editing UI.

    Parameters
    ----------
    parent : QWidget
        Table view that owns the delegate.
    minimum : int, optional
        Lowest accepted value for the editor.
    maximum : int, optional
        Highest accepted value for the editor.
    base : int, optional
        Numeric base used to interpret and write values.

    Attributes
    ----------
    minimum : int
        Lowest accepted value for the editor.
    maximum : int
        Highest accepted value for the editor.
    base : int
        Numeric base used to decode existing cell text and encode committed
        values.
    """

    def __init__(self, parent, minimum=0, maximum=SPINNER_MAX_VALUE, base=16):
        """Store numeric editing bounds for later editor creation.

        The delegate packages one numeric policy for a whole column or field
        family so each edit session reuses the same range limits and encoding
        rules instead of recomputing them from per-row state.

        Parameters
        ----------
        parent : QWidget
            Table view that installs the delegate.
        minimum : int, optional
            Lowest accepted value for the editor.
        maximum : int, optional
            Highest accepted value for the editor.
        base : int, optional
            Numeric base that should be used when reading text cells and
            writing values back to the model.

        Notes
        -----
        These bounds are reused each time Qt instantiates a new editor for a
        cell, keeping every edit in the column aligned with the same numeric
        contract.
        """
        super(SpinBoxDelegate, self).__init__(parent)

        self.minimum = minimum
        self.maximum = maximum
        self.base = base

    def createEditor(self, parent: QWidget, option, index) -> QWidget:
        """Create the spinner used to edit a numeric table field.

        The delegate creates a fresh spinner each time a numeric cell enters
        edit mode so the editor starts from the same bounds and numeric base
        that the owning table expects for that column. This is the step where
        a table cell's stored representation becomes the constrained numeric
        editor that the user can manipulate safely before commit.

        Parameters
        ----------
        parent : QWidget
            Parent widget provided by Qt for the editor instance.
        option
            Unused Qt style option for the editor request.
        index
            Model index being edited.

        Returns
        -------
        QWidget
            Spinner configured for the delegate's maximum and numeric base.
        """
        return Spinner(parent, self.maximum, self.base)

    def setEditorData(self, editor: QWidget, index):
        """Load the cell value into the spinner editor.

        The method converts hex text to an integer before seeding the editor so
        tables can present SMB3-oriented values in text form without giving up
        numeric editing behavior. It is the decode step between model storage
        and the interactive spinner state shown to the user.

        Parameters
        ----------
        editor : QWidget
            Spinner instance returned by :meth:`createEditor`.
        index
            Model index whose value should seed the editor.
        """
        if isinstance(value := index.data(), str):
            value = int(value, self.base)

        assert isinstance(editor, Spinner)
        editor.setValue(value)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index) -> None:
        """Write the edited numeric value back to the table model.

        The committed value is translated back into the representation that the
        table model expects for that column before Qt closes the editor.

        Parameters
        ----------
        editor : QWidget
            Spinner instance containing the committed value.
        model : QAbstractItemModel
            Model that should receive the updated value.
        index
            Model index being committed.

        Notes
        -----
        Hex-backed fields preserve the string representation expected by the
        world editors, while decimal-backed fields write the integer directly.
        """
        assert isinstance(editor, Spinner)

        if self.base == 16:
            model.setData(index, hex(editor.value()))
        else:
            model.setData(index, editor.value())


class DialogDelegate(QStyledItemDelegate):
    """Create informational dialog editors for read-only table actions.

    Some table cells act as launch points for explanatory dialogs rather than
    mutable data fields. This delegate preserves the table editing contract
    while routing the interaction through a message box. It exists so the
    table can expose help or explanatory affordances through the same delegate
    installation path used for editable columns, without teaching the row
    model or host table about transient dialog widgets.

    Parameters
    ----------
    parent : QWidget
        Table view that owns the delegate.
    title : str
        Dialog title shown when the editor opens.
    text : str
        Informational body shown to the user.

    Attributes
    ----------
    title : str
        Dialog title shown whenever the editor opens.
    text : str
        Informational body shown whenever the editor opens.

    Notes
    -----
    ``DialogDelegate`` intentionally keeps the table-model boundary read-only.
    Qt still asks the delegate to participate in editor creation and model
    commit, but the delegate treats those hooks as a UI-only interaction:
    ``createEditor`` opens a transient message box and ``setModelData`` leaves
    the underlying cell value untouched. Future extensions should preserve
    that no-mutation contract so informational cells do not accidentally join
    the undoable world-edit workflow used by the other delegates.

    See Also
    --------
    DropdownDelegate
        Delegate that maps cell edits onto curated enumerated values.
    SpinBoxDelegate
        Delegate that commits numeric edits back into the table model.
    """

    def __init__(self, parent, title: str, text: str):
        """Store the message-box content used during editing.

        The delegate captures a stable explanatory payload once so each
        activated cell can open the same read-only guidance without consulting
        external state. That keeps the table-side contract simple: rows choose
        which explanatory delegate to install, while the delegate owns the
        full dialog payload needed at edit time.

        Parameters
        ----------
        parent : QWidget
            Table view that installs the delegate.
        title : str
            Dialog title shown when the editor opens.
        text : str
            Informational message shown inside the dialog.

        Notes
        -----
        The delegate stores only static dialog content because each edit
        interaction simply needs a transient message box, not a persistent
        widget with independent state or undo participation.
        """
        super(DialogDelegate, self).__init__(parent)

        self.title = title
        self.text = text

    def createEditor(self, parent: QWidget, option, index) -> QWidget:
        """Create the informational dialog for the selected cell.

        Qt requests this editor when a read-only information cell is activated.
        Returning a message box keeps the interaction inside the delegate flow
        without pretending that the cell owns editable data. The surrounding
        table therefore reuses standard delegate wiring for an action-like
        column while still presenting the interaction as an editor to Qt.

        Parameters
        ----------
        parent : QWidget
            Parent widget provided by Qt for the editor instance.
        option
            Unused Qt style option for the editor request.
        index
            Model index being edited.

        Returns
        -------
        QWidget
            Message box configured with the stored title and text.

        Notes
        -----
        The dialog is constructed on demand instead of being cached on the
        delegate. That keeps each activation transient and prevents stale Qt
        parentage from leaking across tables or editing sessions.
        """
        dialog = QMessageBox(
            QMessageBox.Information,
            self.title,
            self.text,
            parent=parent,
        )

        return dialog

    def setModelData(self, editor: QWidget, model, index) -> None:
        """Leave the model unchanged after the dialog is dismissed.

        The delegate participates in Qt's editing lifecycle, but its only job
        is to show information. Returning the existing model value makes that
        no-op commit explicit to maintainers reading the delegate contract and
        documents that this delegate is outside the mutable world-data path.

        Parameters
        ----------
        editor : QWidget
            Dialog widget created for the cell.
        model
            Model associated with the edited index.
        index
            Model index associated with the dialog interaction.

        Returns
        -------
        object
            Existing model data for the index, preserving the read-only nature
            of the dialog interaction.

        Notes
        -----
        Qt calls this hook after editor use even when the delegate is acting
        as a pure informational affordance. Preserving the existing value
        avoids spurious model writes and keeps informational cells out of the
        undo history that editable delegates feed.
        """
        return model.data(index)
