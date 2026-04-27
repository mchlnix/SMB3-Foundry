"""World-map wrappers for fortress-lock and bridge-trigger records.

This module adapts fortress-effect data into selectable world-map objects. The
workflow is fortress-effect record -> wrapper -> shared world-map editing
state, with the replacement-tile preview kept beside the editable position so
the editor can show both the lock marker and the terrain revealed when the
lock clears.

See Also
--------
foundry.game.gfx.objects.world_map.map_object
    Defines the shared position and drawing contract for world-map objects.
foundry.game.level.WorldMap
    Owns the fortress-effect records that feed these objects.
"""

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QPainter

from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.data_points import FortressFXData, Position

KEY_IMG = load_from_object_sprite_sheet(63, 2)


class Lock(MapObject):
    """Model one fortress lock or bridge trigger on the world map.

    SMB3 stores this behavior as fortress-effects data that can later reveal a
    replacement tile. This wrapper makes that ROM record selectable and
    drawable in the overworld editor while preserving the replacement-block
    metadata needed when the lock is cleared.

    The data flow is fortress-effects record -> lock object wrapper -> editor
    drawing and movement, with the replacement tile kept alongside the editable
    position data.

    Parameters
    ----------
    fortress_fx_data : FortressFXData
        Data for the fortress fx value.

    Attributes
    ----------
    data : FortressFXData
        Fortress-effect record that owns the lock position and replacement tile index.
    replacement_tile : Block
        Decoded tile shown after the lock or bridge is removed.

    Examples
    --------
    The editor uses this wrapper as fortress-effect record -> ``Lock`` ->
    shared world-map selection, movement, and preview tools.
    """

    def __init__(self, fortress_fx_data: FortressFXData):
        """Wrap one ROM-backed fortress-lock record for editing.

        Parameters
        ----------
        fortress_fx_data : FortressFXData
            Data for the fortress fx value.
        """
        super(Lock, self).__init__()

        self.data = fortress_fx_data

        self.replacement_tile = get_worldmap_tile(self.data.replacement_block_index)

    def draw(self, painter: QPainter, block_length, transparent, selected=False):
        """Draw the key icon used for a fortress lock.

        The redraw path uses the shared selection state and the cached
        replacement preview so lock editing stays aligned with the same record
        later written back to the overworld data.

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

        painter.drawImage(rect.topLeft(), KEY_IMG.scaled(block_length, block_length))

        if selected:
            painter.fillRect(rect, QColor(0x00, 0xFF, 0x00, 0x80))

    def set_position(self, x, y):
        """Update the lock position in world-map coordinates.

        Movement writes straight through to the wrapped fortress-effect record
        so drag operations update the same position state later serialized by
        the world-map model.

        Parameters
        ----------
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.

        Examples
        --------
        Move the lock and update the wrapped fortress-effect record::

            lock.set_position(5, 9)
            lock.get_position()
            (5, 9)
        """
        self.data.pos = Position.from_xy(x, y)

    def get_position(self) -> tuple[int, int]:
        """Normalized lock coordinates for the shared map-object workflow.

        Selection, hit-testing, and redraw paths all read this tuple through
        the base world-map object API, so the lock stays interchangeable with
        other overworld objects even though its state is stored in
        ``FortressFXData``.

        Returns
        -------
        tuple[int, int]
            X and Y coordinates of the lock.
        """
        return self.data.pos.xy

    def change_type(self, new_type):
        """Ignore type changes for fortress locks.

        Parameters
        ----------
        new_type : int
            Ignored replacement type identifier.
        """
        pass
