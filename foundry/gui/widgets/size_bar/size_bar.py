"""Paint compact byte-budget bars for level editor status widgets.

This file provides :class:`SizeBar`, the low-level widget used by Foundry's
level and enemy size displays. The widget consumes a
:class:`~foundry.game.level.LevelRef.LevelRef` so it can honor whether a level
is attached, then turns a live serialized-byte count and a byte budget into a
thin horizontal bar. Higher-level widgets such as
:class:`~foundry.gui.widgets.size_bar.LevelSizeBar.LevelSizeBar` and the enemy
size variant format labels and feed numbers into this shared painter.

Read the surrounding size-bar widgets next when tracing how serialized object
or enemy usage becomes the status strip shown beneath the editor canvas.

See Also
--------
foundry.gui.widgets.size_bar.LevelSizeBar.LevelSizeBar
    Wraps :class:`SizeBar` with the object-byte label and level-size workflow.
foundry.game.level.LevelRef.LevelRef
    Supplies attachment state and the live level data that higher-level size
    widgets translate into bar values.
"""

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

from foundry.game.level.LevelRef import LevelRef


class SizeBar(QWidget):
    """Draw a compact bar that visualizes serialized-byte usage.

    The size bar is the low-level drawing primitive used by the level and enemy
    size widgets. It compares a live byte count against the original or allowed
    byte budget and turns red when the serialized data grows beyond that budget.

    Parameters
    ----------
    level_ref : LevelRef
        Level reference whose attachment state determines whether the bar can be
        meaningfully drawn.

    Attributes
    ----------
    DEFAULT_SIZE : QSize
        Default height used by the bar widget.
    current_value : float
        Serialized size currently being visualized.
    level : LevelRef
        Level reference associated with the bar.
    original_value : float
        Serialized size budget visualized as the non-overflow threshold.
    value_color : QColor
        Fill color used while the usage stays within budget.
    """

    DEFAULT_SIZE = QSize(10, 10)

    def __init__(self, level_ref: LevelRef):
        """Create an empty size bar for a level reference.

        Parameters
        ----------
        level_ref : LevelRef
            Level reference whose attachment state determines whether the bar
            can be meaningfully drawn.
        """
        super(SizeBar, self).__init__()

        self.level = level_ref

        self.original_value: float = 1.0
        self.current_value: float = 1.0
        self.value_color = QColor.black

    def sizeHint(self) -> QSize:
        """Keep the byte-budget bar at the standard compact status height.

        The widget keeps its standard thin profile regardless of the width
        chosen by the surrounding layout.
        That fixed-height behavior is what lets the higher-level object and
        enemy budget bars sit under the editor as compact status indicators
        during layout, instead of competing with the canvas for space.

        Returns
        -------
        QSize
            QWidget size hint with the standard size-bar height applied.
        """
        size = super(SizeBar, self).sizeHint()

        size.setHeight(self.DEFAULT_SIZE.height())

        return size

    def paintEvent(self, event: QPaintEvent):
        """Paint serialized byte usage into the editor's budget bar.

        The filled portion represents the edited serialized byte count while
        the total width represents the original or allowed budget.
        In Foundry this is the rendering step for the level-size workflow:
        serialized object or enemy bytes are converted into a compact status
        bar, and overflow turns red before save-time validation runs.

        Parameters
        ----------
        event : QPaintEvent
            Paint event describing the update region.
        """
        painter = QPainter(self)

        painter.fillRect(event.rect(), self.palette().base())

        if self.level.level is None:
            return

        total_length = max(self.current_value, self.original_value, 1)

        pixels_per_byte = event.rect().width() / total_length

        bar = QRect(event.rect())
        bar.setWidth(int(pixels_per_byte * self.current_value))

        if self.current_value > self.original_value:
            painter.fillRect(bar, Qt.red)
        else:
            painter.fillRect(bar, self.value_color)
