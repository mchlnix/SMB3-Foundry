"""World-map wrappers for Mario's starting-position record.

This module adapts the ROM-backed start-position record into the shared
world-map object contract. The workflow is start-position record -> wrapper ->
shared world-map draw and move state, so the editor can treat the starting
marker like other overworld objects even though SMB3 stores it differently.

See Also
--------
foundry.game.gfx.objects.world_map.map_object
    Defines the shared position and drawing contract for world-map objects.
foundry.game.level.WorldMap
    Owns the start-position record wrapped here.
"""

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter

from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.data_points import Position

mario_png = load_from_object_sprite_sheet(59, 53)


class StartPosition(MapObject):
    """Model Mario's overworld starting position.

    The start marker is a special world-map object: it is selectable and
    drawable like other overworld items, but the underlying SMB3 position data
    only exposes the row that can be changed in-editor.

    The data flow is ROM starting-position record -> map object wrapper ->
    start-marker rendering, with edits writing back to the stored position.

    Parameters
    ----------
    start_pos : Position
        ROM-backed starting-position record.

    Attributes
    ----------
    pos : Position
        ROM-backed starting-position record.

    Examples
    --------
    The editor uses this wrapper as start-position record -> ``StartPosition``
    -> shared world-map selection and drawing tools.
    """

    def __init__(self, start_pos: Position):
        """Wrap the ROM-backed start-position record for editing.

        Parameters
        ----------
        start_pos : Position
            ROM-backed starting-position record.
        """
        super(StartPosition, self).__init__()

        self.pos = start_pos

    def set_position(self, x, y):
        """Update Mario's starting row on the world map.

        The editor routes movement through the shared map-object API even
        though SMB3 only persists the vertical component for the start marker,
        so this method narrows the generic movement contract down to the one
        coordinate the ROM record actually owns.

        Parameters
        ----------
        x : int
            Ignored horizontal coordinate.
        y : int
            Vertical coordinate stored in the starting-position record.

        Examples
        --------
        Dragging the start marker reuses the shared map-object API, but only
        the vertical coordinate is written back to the ROM-backed record::

            >>> class _Pos:
            ...     def __init__(self, x, y):
            ...         self.x = x
            ...         self.y = y
            ...     @property
            ...     def xy(self):
            ...         return (self.x, self.y)
            >>> start = StartPosition(_Pos(4, 7))
            >>> start.set_position(12, 9)
            >>> start.get_position()
            (4, 9)
        """
        self.pos.y = y

    def get_position(self):
        """Normalized starting-marker coordinates for shared map-object tools.

        Selection, hit-testing, and redraw code consume this tuple through the
        same API used by other overworld objects, which lets the special start
        marker participate in generic editor workflows despite its narrower ROM
        record.

        Returns
        -------
        tuple[int, int]
            X and Y coordinates of the starting position.
        """
        return self.pos.xy

    def draw(self, painter: QPainter, block_length, transparent):
        """Draw Mario's starting-position marker.

        The world-map view uses the normalized position from ``get_position``
        and the shared block length so the start marker redraws in the same
        pass as other overworld objects while still rendering its dedicated
        Mario icon. The method therefore carries the ROM-backed start-position
        state through the same paint cycle and selection geometry flow used by
        the rest of the overworld object wrappers.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        block_length : int
            Rendered block size in pixels.
        transparent : bool
            Ignored transparency flag from the shared map-object API.
        """
        x, y = self.get_position()

        painter.drawImage(QPoint(x, y) * block_length, mario_png.scaled(block_length, block_length))

    def change_type(self, new_type):
        """Ignore type changes for the starting-position marker.

        Parameters
        ----------
        new_type : int
            Ignored replacement type identifier.
        """
        pass
