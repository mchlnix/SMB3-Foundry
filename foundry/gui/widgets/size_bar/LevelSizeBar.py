"""Show the active level's object-byte usage in the editor status strip.

``LevelSizeBar`` combines a numeric label with the generic
:class:`~foundry.gui.widgets.size_bar.size_bar.SizeBar` painter to display how
many bytes the active level's object stream currently consumes. The widget
reads the live object-byte count from
:class:`~foundry.game.level.LevelRef.LevelRef`, compares it with the level's
original ROM allocation and any managed free-space allowance exposed through
:class:`~foundry.game.File.ROM`, and keeps both the text and filled bar in sync
as edits change serialized size.

Read :mod:`foundry.gui.widgets.size_bar.size_bar` next for the shared drawing
primitive, then :mod:`foundry.game.level.LevelRef` for the change signals and
size queries that drive this display.

See Also
--------
foundry.gui.widgets.size_bar.size_bar.SizeBar
    Low-level bar widget that renders byte usage against the allowed budget.
foundry.game.level.LevelRef.LevelRef
    Level-facing model wrapper that emits data-change notifications for the
    active editor selection.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef

from .size_bar import SizeBar


class LevelSizeBar(QWidget):
    """Display object-data usage for the active level.

    This widget pairs a numeric label with :class:`SizeBar` to show how much
    object-data space the level consumes. It follows the active ``LevelRef`` so
    the display updates whenever object edits change the serialized size, and it
    expands the budget when Foundry's managed free-space metadata is available.

    Parameters
    ----------
    parent : QWidget
        Parent widget that owns the size bar.
    level : LevelRef
        Level reference whose object usage should be displayed.

    Attributes
    ----------
    level_ref : LevelRef
        Level reference that supplies object-size data.
    size_bar : SizeBar
        Bar widget that visualizes relative size usage.
    info_label : QLabel
        Label that shows the numeric size values in bytes.
    """

    def __init__(self, parent, level: LevelRef):
        """Create the object-size bar for a level reference.

        The widget subscribes to level data changes so the numeric label and
        filled bar stay synchronized with every edit that changes serialized
        object size.

        Parameters
        ----------
        parent : QWidget
            Parent widget that owns the size bar.
        level : LevelRef
            Level reference whose object usage should be displayed.
        """
        super(LevelSizeBar, self).__init__(parent)

        self.level_ref = level

        self.level_ref.data_changed.connect(self.update)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.setWhatsThis(
            "<b>Level Size Bar</b><br/>"
            "The objects inside a level, like platforms and item blocks, are stored as bytes in the ROM. "
            "Since levels are stored one after another, saving a level with more objects, than it originally "
            "had, would overwrite another level and probably cause the game to crash, if you would enter it, "
            "while playing.<br/>"
            "This bar shows, how much of the available space for level objects is currently taken up. It will turn "
            "red, when too many level objects have been placed (or if the level objects would result in more bytes, "
            "than the level originally had)."
        )

        self.size_bar = SizeBar(self.level_ref)
        self.size_bar.value_color = self.value_color

        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.size_bar)
        layout.addWidget(self.info_label)

    def update(self):
        """Synchronize the label and fill bar with the level's live byte usage.

        ``LevelRef.data_changed`` drives this refresh path after object edits,
        imports, or undo operations change the serialized object stream. The
        widget first formats the human-readable byte string for the status
        label, then republishes the same live size and budget numbers into the
        embedded ``SizeBar`` so Qt repaints both surfaces from one consistent
        snapshot of level state.

        Returns
        -------
        None
            Result returned by the base Qt update chain.
        """
        original_value_string = "∞" if self.max_value == float("INF") else str(self.max_value)
        self.info_label.setText(f"{self.value_description}: {self.current_value}/{original_value_string} Bytes")

        self.size_bar.current_value = self.current_value
        self.size_bar.original_value = self.max_value

        return super(LevelSizeBar, self).update()

    @property
    def value_color(self):
        """Define the in-budget fill color for the object-byte status bar.

        ``SizeBar`` reads this property when it renders the active level's
        object-byte usage, so the color choice defines the normal visual state
        before the bar switches into its over-budget warning path.

        Returns
        -------
        QColor
            Green fill color used while object data stays within budget.
        """
        return QColor.fromRgb(0x58D858)

    @property
    def value_description(self):
        """Name the byte counter that :meth:`update` renders for object usage.

        :meth:`update` combines this label with :attr:`current_value` and
        :attr:`max_value` each time the active level changes, so the returned
        text identifies which serialized ROM budget the status row is
        reporting.

        Returns
        -------
        str
            Description shown before the byte counts in the info label.
        """
        return "Objects"

    @property
    def max_value(self) -> float:
        """Report the object-byte budget available to the active level.

        Detached levels report an infinite budget until they are attached to a
        ROM. When managed level positions are available, the budget includes the
        free space tracked for the active object set.

        Returns
        -------
        float
            Maximum serialized object-data size available to the level.
        """
        level_size = self.level_ref.object_size_on_disk

        if not self.level_ref.level.attached_to_rom and level_size == 0:
            level_size = float("INF")

        elif ROM().additional_data.managed_level_positions:
            free_space_in_bank = ROM().additional_data.free_space_for_object_set(self.level_ref.level.object_set_number)
            level_size += free_space_in_bank

        return level_size

    @property
    def current_value(self) -> float:
        """Report the live byte count for the active level's object stream.

        The value comes from the live level model, so it reflects unsaved edits
        rather than only the last on-disk size.

        Returns
        -------
        float
            Serialized size of the active level's object data in bytes.
        """
        return self.level_ref.current_object_size()
