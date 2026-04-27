"""Palette inspection and editing surfaces for SMB3 object palettes.

This module groups the reference palette viewer, interactive swatches, chooser
dialog, and active side-panel palette editor used by Foundry. The workflow is
ROM-backed palette data -> palette-group and swatch widgets -> preview or
commit callbacks that either reload the level for temporary feedback or push
undoable palette commands into the main editor.

See Also
--------
foundry.gui.commands.UpdatePalette
    Command used when accepted palette edits are committed to the undo stack.
foundry.gui.level_settings.level_settings_dialog
    Companion settings surface that changes the active object palette group.
"""

from itertools import product
from typing import Callable

from PySide6.QtCore import QSize, Signal, SignalInstance
from PySide6.QtGui import QColor, QMouseEvent, QPixmap, Qt, QUndoStack
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from foundry.game.File import ROM
from foundry.game.gfx import change_color
from foundry.game.gfx.Palette import (
    COLORS_PER_PALETTE,
    PALETTE_GROUPS_PER_OBJECT_SET,
    PALETTES_PER_PALETTES_GROUP,
    NESPalette,
    load_palette_group,
)
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.commands import UpdatePalette
from foundry.gui.dialogs.CustomDialog import CustomDialog


class PaletteViewer(CustomDialog):
    """Inspect every palette group available to the level's object set.

    The dialog shows the full palette-group table for the active object set so
    maintainers can compare how SMB3 colors are organized beyond the one group
    currently selected for the level.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the edited level.

    Attributes
    ----------
    level_ref : LevelRef
        Level whose object set determines which palette groups are shown.
    palettes_per_row : int
        Number of palette-group columns displayed per row.

    See Also
    --------
    PaletteWidget
        Renders one palette inside a group and can expose color editing.
    SidePalette
        Focused palette editor for the level's selected object palette group.
    """

    palettes_per_row = 4

    def __init__(self, parent, level_ref: LevelRef):
        """Build the palette-group grid for the active object set.

        Construction reads the level's object-set selection from ``level_ref``,
        allocates one group box per palette group, and fills each group with
        ``PaletteWidget`` rows. That creates a reference surface where one
        level setting fans out into every ROM-backed palette grouping that the
        object set can use. The dialog does not own preview or commit logic
        itself; instead, it materializes the full comparison grid that other
        palette workflows use to understand which group a level setting will
        eventually activate.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the edited level.
        """
        title = f"Palette Groups for Object Set {level_ref.level.object_set_number}"

        super(PaletteViewer, self).__init__(parent, title=title)

        self.level_ref = level_ref

        layout = QGridLayout(self)

        for palette_group_number in range(PALETTE_GROUPS_PER_OBJECT_SET):
            group_box = QGroupBox()
            group_box.setTitle(f"Palette Group {palette_group_number}")

            group_box_layout = QVBoxLayout(group_box)
            group_box_layout.setSpacing(0)

            for palette_no in range(PALETTES_PER_PALETTES_GROUP):
                group_box_layout.addWidget(PaletteWidget(level_ref, palette_group_number, palette_no))

            row = palette_group_number // self.palettes_per_row
            col = palette_group_number % self.palettes_per_row

            layout.addWidget(group_box, row, col)


class PaletteWidget(QWidget):
    # index in palette, color index in NES palette
    """Render one four-color NES palette and optionally open the color table.

    The widget reads one palette out of a palette group, paints four
    ``ColorSquare`` children, and emits preview/commit signals when editing is
    enabled. ``SidePalette`` uses those signals to separate temporary preview
    changes from undoable committed edits.

    Parameters
    ----------
    level_ref : LevelRef
        Reference to the edited level.
    group_number : int
        Palette-group index to display.
    palette_number : int
        Palette index inside the group.

    Attributes
    ----------
    _color_squares : list[ColorSquare]
        Squares that display the colors of this palette.
    _palette_number : int
        Palette index inside the palette group.
    clickable : bool
        Whether clicking colors should open the color chooser.
    color_changed : SignalInstance
        Signal emitted for temporary preview changes.
    color_committed : SignalInstance
        Signal emitted for committed palette edits.
    group_number : int
        Palette-group index currently being displayed.
    level_ref : LevelRef
        Level whose object set selects the palette-group table.

    See Also
    --------
    ColorTable
        Dialog used to choose a replacement NES palette color.
    SidePalette
        Connects the preview and commit signals to runtime preview and undo
        behavior.
    """
    color_changed: SignalInstance = Signal(int, int)
    color_committed: SignalInstance = Signal(int, int)

    def __init__(self, level_ref: LevelRef, group_number: int, palette_number: int):
        """Create one palette row for a specific group and palette index.

        The widget immediately builds four reusable swatches, then keeps them in
        sync with palette-group data loaded from ROM whenever preview or commit
        paths refresh the palette.

        Parameters
        ----------
        level_ref : LevelRef
            Reference to the edited level.
        group_number : int
            Palette-group index to display.
        palette_number : int
            Palette index inside the group.
        """
        super(PaletteWidget, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 2, 0, 2)

        self.level_ref = level_ref
        self.group_number = group_number
        self._palette_number = palette_number

        self.clickable = False

        self._color_squares = []

        for color_index in range(COLORS_PER_PALETTE):
            square = ColorSquare()
            square.clicked.connect(self._open_color_table)

            self._color_squares.append(square)

            layout.addWidget(square)

        self._update_colors()

    @property
    def _palette_group(self):
        """Load the decoded palette group for this widget's group index.

        The property resolves through ``level_ref`` each time so palette preview
        and commit paths always read the latest ROM-backed colors for the active
        object set.

        Returns
        -------
        list[list[int]]
            Palette-group color indexes loaded from ROM data.
        """
        return load_palette_group(self.level_ref.level.object_set_number, self.group_number)

    def update(self):
        """Refresh the displayed colors from the loaded palette group."""
        self._update_colors()

    def _open_color_table(self):
        """Open the color picker and emit preview/commit updates.

        While the chooser is open, clicked colors are previewed through
        ``color_changed``. After the dialog closes, the original color is
        restored unless the user accepted a different selection, in which case
        ``color_committed`` carries the undoable edit.
        """
        if not self.clickable:
            return

        index_in_palette = self.layout().indexOf(self.sender())
        original_color_index = self.sender().color_index

        color_table = ColorTable()
        color_table.color_clicked.connect(lambda x: self.color_changed.emit(index_in_palette, x))
        color_table.color_clicked.connect(self._update_colors)

        answer = color_table.exec()

        self.color_changed.emit(index_in_palette, original_color_index)

        if answer == QDialog.Accepted:
            if color_table.selected_color_index != original_color_index:
                self.color_committed.emit(index_in_palette, color_table.selected_color_index)

        self._update_colors()

    def _update_colors(self):
        """Repaint the palette squares from the loaded palette group."""
        for color_index, color_square in zip(self._palette_group[self._palette_number], self._color_squares):
            color_square.set_color(color_index)


class ColorSquare(QLabel):
    """Display one NES palette color as a clickable square.

    The widget stores both the NES palette index and the resolved Qt color so it
    can draw the swatch and choose a visible selection border. ``PaletteWidget``
    and ``ColorTable`` both reuse this class, so the same widget carries color
    identity from passive display rows into the active chooser dialog. The
    lifecycle is tiny but important: a palette index comes in, the swatch caches
    the resolved color, and clicks push that identity back out through
    ``clicked`` for preview or commit handling elsewhere.

    Parameters
    ----------
    color_index : int, optional
        Index of the color.
    square_length : int, optional
        Side length in pixels.

    Attributes
    ----------
    clicked : SignalInstance
        Signal emitted when the square is clicked.
    square_size : QSize
        Fixed size of the square.

    See Also
    --------
    PaletteWidget
        Uses swatches for palette display and editing entry points.
    ColorTable
        Uses the same swatch widget for the 64-color chooser grid.
    """

    clicked: SignalInstance = Signal()

    def __init__(self, color_index=-1, square_length=16):
        """Create a swatch for one NES palette entry.

        The constructor immediately establishes both halves of the swatch's
        identity: the NES palette index used by palette-edit workflows and the
        resolved Qt color used for display and border contrast. That keeps the
        same widget ready for passive palette display and active chooser use.

        Parameters
        ----------
        color_index : int, optional
            Index of the color.
        square_length : int, optional
            Side length in pixels.
        """
        super(ColorSquare, self).__init__()

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.square_size = QSize(square_length, square_length)

        self._set_color(color_index)

    def _set_color(self, color_index: int):
        """Cache and repaint the swatch for one NES palette index.

        The method records which NES entry the swatch now represents, resolves
        the corresponding Qt color, rebuilds the pixmap, and clears any stale
        highlight border. Preview callbacks and chooser selection logic then
        read one coherent swatch state instead of separate cached fields.

        Parameters
        ----------
        color_index : int
            Index of the color.
        """
        self.color_index = color_index

        if color_index != -1:
            color = NESPalette[color_index]
        else:
            color = QColor(Qt.white)

        self.color = color
        color_square = QPixmap(self.square_size)
        color_square.fill(color)

        self.setPixmap(color_square)

        self.select(False)

    def set_color(self, color_index: int):
        """Update the swatch from a palette color index.

        Parameters
        ----------
        color_index : int
            Index of the color.
        """
        self._set_color(color_index)
        self.update()

    def select(self, selected):
        """Toggle the selection border for the swatch.

        Parameters
        ----------
        selected : bool
            Whether the square should be drawn as selected.
        """
        if selected:
            if self.color.lightnessF() < 0.25:
                self.setStyleSheet("border-color: rgb(255, 255, 255); border-width: 2px; border-style: solid")
            else:
                self.setStyleSheet("border-color: rgb(0, 0, 0); border-width: 2px; border-style: solid")
        else:
            rgb = self.color.getRgb()
            self.setStyleSheet(
                f"border-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border-width: 2px; border-style: solid"
            )

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Emit the click signal and forward the mouse-release event.

        This keeps the swatch lightweight: it only identifies which color was
        clicked, while higher-level palette widgets decide whether that click
        means preview, selection, or a committed edit.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by ``QLabel.mouseReleaseEvent``.
        """
        self.clicked.emit()

        return super(ColorSquare, self).mouseReleaseEvent(event)


class ColorTable(QDialog):
    """Show the 64-color NES palette as a chooser dialog.

    The dialog is the narrow translation layer between Foundry's palette-edit
    workflows and the raw NES color table. Callers use it for two different
    phases of the same edit: preview clicks stream candidate NES indices back
    to the owner, while acceptance freezes one choice so the caller can turn
    that preview into an undoable ROM-level palette edit. Keeping this chooser
    separate from ``PaletteWidget`` and ``SidePalette`` preserves a clean
    boundary between "pick one NES color from the canonical 64-entry table"
    and the higher-level editor logic that decides whether a change is only a
    temporary preview, a committed undo command, or a cancelled experiment.

    Attributes
    ----------
    _currently_selected_square : ColorSquare
        Square currently marked as selected.
    buttons : QDialogButtonBox
        OK/Cancel buttons for the chooser.
    color_clicked : SignalInstance
        Signal emitted when the hovered selection changes.
    color_table_layout : QGridLayout
        Grid containing all palette squares.
    ok_clicked : SignalInstance
        Signal emitted when a color is accepted.
    selected_color_index : int
        Accepted NES palette index.
    square_length : int
        Side length for chooser swatches.
    table_columns : int
        Number of columns in the chooser grid.
    table_rows : int
        Number of rows in the chooser grid.

    See Also
    --------
    PaletteWidget
        Opens this dialog and converts its result into preview and commit
        signals.
    SidePalette
        Owns the focused palette-edit workflow that previews and commits the
        chooser result against the active level palette.
    """

    table_rows = 4
    table_columns = 16

    color_clicked: SignalInstance = Signal(int)
    ok_clicked: SignalInstance = Signal(int)

    def __init__(self):
        """Create the NES palette chooser grid.

        The dialog builds a 4x16 swatch table once, then tracks only the
        currently selected square and accepted color index while callers listen
        for preview clicks. That keeps the chooser itself dumb about ROM state:
        it owns only the canonical NES color table presentation and leaves
        preview reloads, undo commands, and palette-group updates to the caller
        that opened it.
        """
        super(ColorTable, self).__init__()

        self.setWindowTitle("NES Color Table")

        self._currently_selected_square: ColorSquare = ColorSquare()
        self.selected_color_index = 0
        """Index into the NES Palette, that was selected."""

        self.square_length = 24

        self.color_table_layout = QGridLayout()
        self.color_table_layout.setSpacing(0)

        for row, column in product(range(self.table_rows), range(self.table_columns)):
            color_index = row * self.table_columns + column

            square = ColorSquare(color_index, self.square_length)
            square.setLineWidth(0)

            square.clicked.connect(self._on_click)

            self.color_table_layout.addWidget(square, row, column)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttons.clicked.connect(self._on_button)

        layout = QVBoxLayout(self)
        layout.addLayout(self.color_table_layout)

        layout.addWidget(self.buttons, alignment=Qt.AlignCenter)

    def _on_click(self):
        """Preview one NES color choice without committing it yet.

        A click in the chooser means "treat this swatch as the active candidate
        color" rather than "write this color immediately." The method therefore
        updates the table's single selected swatch first, then emits the NES
        palette index so the owning palette workflow can preview that candidate
        against level graphics without crossing the commit boundary.
        """
        color_index = self.sender().color_index
        self.select_square(self.sender())
        self.color_clicked.emit(color_index)

    def select_square(self, color_square: ColorSquare):
        """Mark one chooser square as selected.

        The method removes the border from the previously selected swatch before
        highlighting the new one so preview clicks always leave a single active
        selection in the table. That invariant matters because callers read the
        chooser as a single-candidate control: when the user eventually presses
        OK, there must be exactly one swatch whose NES index represents the
        color that will cross the preview-to-commit boundary.

        Parameters
        ----------
        color_square : ColorSquare
            Swatch that should become the active chooser selection.
        """
        self._currently_selected_square.select(False)

        color_square.select(True)

        self._currently_selected_square = color_square

    def _on_button(self, button: QAbstractButton):
        """Accept or reject the chooser based on the clicked button.

        Accepting stores the index of the selected swatch so callers can commit
        that NES color after the modal dialog closes. Rejecting leaves the
        preview owner free to restore its original palette state, which keeps
        this dialog responsible only for chooser state while higher-level
        palette widgets own rollback, reload, and undo behavior.

        Parameters
        ----------
        button : QAbstractButton
            Dialog button that was clicked.
        """
        if button is self.buttons.button(QDialogButtonBox.Ok):  # ok button
            color_index = self.color_table_layout.indexOf(self._currently_selected_square)

            self.selected_color_index = color_index
            self.accept()
        else:
            self.reject()


class SidePalette(QWidget):
    """Edit the level's active object palette group.

    Unlike ``PaletteViewer``, which shows every palette group for reference,
    this widget stays attached to the active level and wires color changes into
    live preview updates plus undoable palette edits.

    Parameters
    ----------
    level_ref : LevelRef
        Reference to the edited level.

    Attributes
    ----------
    _palette_widgets : list[PaletteWidget]
        Palette rows used for the level's active palette group.
    level_ref : LevelRef
        Level whose palette group is being edited.

    See Also
    --------
    UpdatePalette
        Undo command used when a color change is committed.
    PaletteWidget
        Emits the preview and commit signals this widget consumes.
    """

    def __init__(self, level_ref: LevelRef):
        """Create the active-palette editor for a level.

        The widget listens for ``LevelRef.data_changed`` so header changes,
        palette reloads, and committed color edits all flow back into the active
        palette display without rebuilding the surrounding side panel.

        Parameters
        ----------
        level_ref : LevelRef
            Reference to the edited level.
        """
        super(SidePalette, self).__init__()

        self.level_ref = level_ref

        self.level_ref.data_changed.connect(self.update)

        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)

        self._palette_widgets: list[PaletteWidget] = []

        self.update()

        self.setWhatsThis(
            "<b>Object Palettes</b><br/>"
            "This shows the current palette group of the level, which can be changed in the level header "
            "editor.<br/>"
            "By clicking on the individual colors, you can change them.<br/><br/>"
            ""
            "Note: The first color (the left most one) is always the same among all 4 palettes."
        )

    @property
    def palette_group(self):
        """Load the palette group for the level's active object palette index.

        The property is used by preview callbacks and committed undo commands so
        both paths operate on the same ROM-backed palette data.

        Returns
        -------
        list[list[int]]
            Palette-group color indexes loaded from ROM data.
        """
        return load_palette_group(self.level_ref.object_set_number, self.level_ref.object_palette_index)

    @property
    def undo_stack(self) -> QUndoStack:
        """Expose the main-window undo stack used for palette commits.

        Preview changes bypass undo, but accepted color edits are translated
        into ``UpdatePalette`` commands on this shared stack.

        Returns
        -------
        QUndoStack
            Undo stack used to record committed palette edits.
        """
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def _setup(self):
        """Create palette rows and connect preview/commit callbacks."""
        for palette_no in range(PALETTES_PER_PALETTES_GROUP):
            widget = PaletteWidget(self.level_ref, self.level_ref.object_palette_index, palette_no)
            widget.color_changed.connect(self.on_color_change(palette_no))
            widget.color_committed.connect(self.on_color_commit(palette_no))
            widget.clickable = True

            self.layout().addWidget(widget)
            self._palette_widgets.append(widget)

    def update(self):
        """Refresh palette rows for the level's active object palette group."""
        if self.layout().isEmpty() and ROM.is_loaded() and self.level_ref:
            self._setup()

        for widget in self._palette_widgets:
            widget.group_number = self.level_ref.level.header.object_palette_index
            widget.update()

    def on_color_change(self, palette_no: int) -> Callable:
        """Build a preview callback for one palette row.

        The returned function mutates the loaded palette group in memory and
        reloads the level so object graphics preview the candidate NES color
        immediately. No undo command is created until the chooser is accepted.

        Parameters
        ----------
        palette_no : int
            Zero-based row inside the level's active palette group.

        Returns
        -------
        Callable
            Callback that applies a temporary preview change and reloads level
            graphics.
        """

        def actual_changer(index_in_palette, index_in_nes_color_table):
            change_color(
                self.palette_group,
                palette_no,
                index_in_palette,
                index_in_nes_color_table,
            )

            self.level_ref.level.reload()

        return actual_changer

    def on_color_commit(self, palette_no: int) -> Callable:
        """Build a commit callback for one palette row.

        The callback closes the preview loop by translating the accepted color
        choice into an ``UpdatePalette`` command on the shared editor undo
        stack.

        Parameters
        ----------
        palette_no : int
            Zero-based row inside the level's active palette group.

        Returns
        -------
        Callable
            Callback that pushes an ``UpdatePalette`` command onto the shared
            undo stack after the chooser is accepted.
        """

        def actual_commiter(index_in_palette, index_in_nes_color_table):
            self.undo_stack.push(
                UpdatePalette(
                    self.level_ref,
                    palette_no,
                    index_in_palette,
                    index_in_nes_color_table,
                )
            )

        return actual_commiter
