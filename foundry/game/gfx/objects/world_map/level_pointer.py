"""World-map wrappers for SMB3 level-entry pointer records.

This module adapts ROM-backed level-pointer data into the shared world-map
object contract used by selection, movement, and drawing tools. The workflow
is pointer record -> wrapper -> shared world-map editing state, so level-entry
tiles behave like other overworld objects while still writing changes back
into the underlying pointer record.

See Also
--------
foundry.game.gfx.objects.world_map.map_object
    Defines the shared position and drawing contract for world-map objects.
foundry.game.level.WorldMap
    Owns the pointer records that this wrapper exposes to the editor.
"""

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QPen

from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.data_points import LevelPointerData, Position
from smb3parse.levels.world_map import level_name


class LevelPointer(MapObject):
    """Model one overworld level-entry pointer.

    A level pointer marks the tile that opens a playable stage on the world
    map. The editor treats it as a selectable map object while the underlying
    ``LevelPointerData`` continues to own the ROM-facing position and target
    data.

    The data flow is ROM pointer record -> world-map object wrapper -> outline
    drawing and position edits, with the wrapper writing coordinate changes
    back into the ``LevelPointerData`` record.

    Parameters
    ----------
    level_pointer_data : LevelPointerData
        Data for the level pointer value.

    Attributes
    ----------
    data : LevelPointerData
        ROM-backed level-pointer record being edited.

    Examples
    --------
    The world-map editor decodes ROM-backed pointer data once and then routes
    movement, labels, and selection through the wrapper instead of reaching
    into the raw pointer record at each call site::

        pointer = LevelPointer(level_pointer_data)
        pointer.name
        pointer.get_position()

    The important shape is ``LevelPointerData`` in, shared ``MapObject``
    position and draw behavior out. World-map tools can therefore treat stage
    entrances like other overworld objects even though the ROM record still
    owns the target-level data.
    """

    def __init__(self, level_pointer_data: LevelPointerData):
        """Wrap one ROM-backed level-pointer record for editing.

        Parameters
        ----------
        level_pointer_data : LevelPointerData
            Data for the level pointer value.
        """
        super(LevelPointer, self).__init__()

        self.data = level_pointer_data

    @property
    def name(self):
        """Editor-facing level label derived from the pointer target.

        The label is derived from the ROM-backed pointer target so world-map
        lists and status surfaces always reflect the level that would open from
        this tile, even after pointer edits or model reloads.

        Returns
        -------
        str
            Editor-facing label for the pointed-at level.
        """
        return f"Level Pointer '{level_name(self.data)}'"

    @name.setter
    def name(self, value):
        """Ignore attempts to rename the level-pointer wrapper.

        Parameters
        ----------
        value : str
            Ignored replacement label.
        """
        pass

    def draw(self, painter: QPainter, block_length, transparent, selected=False):
        """Draw the world-map outline used for a level pointer.

        The view renders level pointers as an outline overlay rather than a
        sprite so maintainers can distinguish playable-entry tiles from other
        overworld objects without hiding the underlying terrain tile.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        block_length : int
            Rendered block size in pixels.
        transparent : bool
            Ignored transparency flag from the shared map-object API.
        selected : bool, optional
            Whether the object should be drawn as selected.
        """
        pos = QPoint(*self.data.pos.xy) * block_length

        rect = QRect(pos, QSize(block_length, block_length))

        if selected:
            painter.fillRect(rect, QColor(0x00, 0xFF, 0x00, 0x80))

        painter.setPen(QPen(QColor(0xFF, 0x00, 0x00, 0x80), 4))

        painter.drawRect(rect)

    def set_position(self, x, y):
        """Update the level-pointer tile position.

        Position changes replace the pointer's ROM-backed coordinate record so
        later save and reload paths observe the same tile location used during
        editor movement and hit testing.

        Parameters
        ----------
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.

        Examples
        --------
        Pointer move commands update the wrapped ROM-backed coordinate through
        the normalized world-map API::

            pointer = LevelPointer(level_pointer_data)
            pointer.set_position(6, 9)
            pointer.get_position()
        """
        self.data.pos = Position.from_xy(x, y)

    def get_position(self) -> tuple[int, int]:
        """Normalized tile coordinates for the pointer wrapper.

        World-map selection and sorting code reads this tuple instead of
        reaching into ``LevelPointerData`` directly, which keeps pointer
        records aligned with the shared ``MapObject`` contract.

        Returns
        -------
        tuple[int, int]
            X and Y coordinates of the pointer.
        """
        return self.data.pos.xy

    def change_type(self, new_type):
        """Ignore type changes for level pointers.

        Parameters
        ----------
        new_type : int
            Ignored replacement type identifier.
        """
        pass

    def __lt__(self, other):
        """Compare level pointers using their underlying ROM-backed data.

        Ordering by the wrapped pointer record keeps editor lists and redraw
        passes aligned with the same ROM-backed ordering used by the world-map
        model, so list state and render state stay consistent.

        Parameters
        ----------
        other : object
            Other object or pointer record to compare against.

        Returns
        -------
        bool
            ``True`` when this pointer sorts before ``other``.
        """
        if isinstance(other, LevelPointer):
            other = other.data

        return self.data < other
