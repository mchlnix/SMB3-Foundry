"""World-map sprite wrappers for SMB3 moving overworld objects.

This module adapts ROM-backed sprite records into selectable editor objects.
The workflow is sprite record -> wrapper -> shared world-map draw and movement
state, so wandering enemies, airships, and item icons can all reuse the same
world-map tools.

See Also
--------
foundry.game.gfx.objects.world_map.map_object
    Defines the shared position and drawing contract for world-map objects.
foundry.game.level.WorldMap
    Owns the sprite records that feed these wrappers.
"""

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor

from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.constants import (
    MAPITEM_ANCHOR,
    MAPITEM_FIREFLOWER,
    MAPITEM_FROG,
    MAPITEM_HAMMER,
    MAPITEM_HAMMERSUIT,
    MAPITEM_JUDGEMS,
    MAPITEM_LEAF,
    MAPITEM_MUSHROOM,
    MAPITEM_MUSICBOX,
    MAPITEM_NOITEM,
    MAPITEM_PWING,
    MAPITEM_STAR,
    MAPITEM_TANOOKI,
    MAPITEM_UNKNOWN1,
    MAPITEM_UNKNOWN2,
    MAPITEM_WHISTLE,
    MAPOBJ_AIRSHIP,
    MAPOBJ_BATTLESHIP,
    MAPOBJ_BOOMERANGBRO,
    MAPOBJ_CANOE,
    MAPOBJ_COINSHIP,
    MAPOBJ_EMPTY,
    MAPOBJ_FIREBRO,
    MAPOBJ_HAMMERBRO,
    MAPOBJ_HEAVYBRO,
    MAPOBJ_HELP,
    MAPOBJ_NAMES,
    MAPOBJ_NSPADE,
    MAPOBJ_TANK,
    MAPOBJ_UNK0C,
    MAPOBJ_UNK08,
    MAPOBJ_W7PLANT,
    MAPOBJ_W8AIRSHIP,
    MAPOBJ_WHITETOADHOUSE,
)
from smb3parse.data_points import Position, SpriteData
from smb3parse.levels import FIRST_VALID_ROW

EMPTY_IMAGE = load_from_object_sprite_sheet(0, 53)

MAP_OBJ_SPRITES = {
    MAPOBJ_EMPTY: EMPTY_IMAGE,
    MAPOBJ_HELP: load_from_object_sprite_sheet(43, 2),
    MAPOBJ_AIRSHIP: load_from_object_sprite_sheet(44, 2),
    MAPOBJ_HAMMERBRO: load_from_object_sprite_sheet(45, 2),
    MAPOBJ_BOOMERANGBRO: load_from_object_sprite_sheet(46, 2),
    MAPOBJ_HEAVYBRO: load_from_object_sprite_sheet(47, 2),
    MAPOBJ_FIREBRO: load_from_object_sprite_sheet(48, 2),
    MAPOBJ_W7PLANT: load_from_object_sprite_sheet(49, 2),
    MAPOBJ_UNK08: load_from_object_sprite_sheet(50, 2),
    MAPOBJ_NSPADE: load_from_object_sprite_sheet(51, 2),
    MAPOBJ_WHITETOADHOUSE: load_from_object_sprite_sheet(52, 2),
    MAPOBJ_COINSHIP: load_from_object_sprite_sheet(53, 2),
    MAPOBJ_UNK0C: load_from_object_sprite_sheet(54, 2),
    MAPOBJ_BATTLESHIP: load_from_object_sprite_sheet(55, 2),
    MAPOBJ_TANK: load_from_object_sprite_sheet(56, 2),
    MAPOBJ_W8AIRSHIP: load_from_object_sprite_sheet(57, 2),
    MAPOBJ_CANOE: load_from_object_sprite_sheet(58, 2),
}


EMPTY_IMAGE = load_from_object_sprite_sheet(0, 53)

MAP_ITEM_SPRITES = {
    MAPITEM_NOITEM: EMPTY_IMAGE,
    MAPITEM_MUSHROOM: load_from_object_sprite_sheet(6, 48),
    MAPITEM_FIREFLOWER: load_from_object_sprite_sheet(16, 53),
    MAPITEM_LEAF: load_from_object_sprite_sheet(57, 53),
    MAPITEM_FROG: load_from_object_sprite_sheet(56, 53),
    MAPITEM_TANOOKI: load_from_object_sprite_sheet(54, 53),
    MAPITEM_HAMMERSUIT: load_from_object_sprite_sheet(58, 53),
    MAPITEM_JUDGEMS: load_from_object_sprite_sheet(19, 51),
    MAPITEM_PWING: load_from_object_sprite_sheet(55, 53),
    MAPITEM_STAR: load_from_object_sprite_sheet(5, 48),
    MAPITEM_ANCHOR: load_from_object_sprite_sheet(61, 53),
    MAPITEM_HAMMER: load_from_object_sprite_sheet(63, 53),
    MAPITEM_WHISTLE: load_from_object_sprite_sheet(60, 53),
    MAPITEM_MUSICBOX: load_from_object_sprite_sheet(62, 53),
    MAPITEM_UNKNOWN1: EMPTY_IMAGE,
    MAPITEM_UNKNOWN2: EMPTY_IMAGE,
}


class Sprite(MapObject):
    """Model one movable overworld sprite.

    These records cover Hammer Bros., airships, wandering item icons, and
    other world-map sprites. The wrapper keeps the ROM-backed ``SpriteData`` in
    sync with editor coordinates and type changes while reusing the generic
    map-object selection and drawing workflow.

    Parameters
    ----------
    sprite_data : SpriteData
        Data for the sprite value.

    Attributes
    ----------
    data : SpriteData
        ROM-backed sprite record being edited and drawn.

    Examples
    --------
    Wrap a ROM-backed world-map sprite record, then inspect the editor-facing
    fields that stay synchronized with the underlying data::

        sprite_data = SpriteData(Position.from_xy(7, 4), MAPOBJ_HAMMERBRO, 0)
        sprite = Sprite(sprite_data)

        sprite.get_position()
        (7, 4)
        sprite.name
        "Sprite 'Hammer Brother'"
    """

    def __init__(self, sprite_data: SpriteData):
        """Wrap one ROM-backed overworld sprite record.

        Parameters
        ----------
        sprite_data : SpriteData
            Sprite record being edited and rendered.
        """
        super(Sprite, self).__init__()

        self.data = sprite_data

        if self.data.row < FIRST_VALID_ROW:
            self.data.row = FIRST_VALID_ROW

    @property
    def name(self):
        """Display name for the sprite type stored in the record.

        World-map lists and status text derive the label directly from the
        SMB3 sprite-name table, so changing ``type`` immediately changes the
        label shown throughout the editor without maintaining a second name
        field on the sprite object or desynchronizing it from ROM data.
        The property therefore acts as the read-only UI view of the same type
        field consumed by draw and change-type workflows.

        Returns
        -------
        str
            Editor-facing name derived from ``MAPOBJ_NAMES``.
        """
        return f"Sprite '{MAPOBJ_NAMES[self.data.type]}'"

    @name.setter
    def name(self, value):
        """Ignore external name assignments.

        Parameters
        ----------
        value : str
            Ignored because the name is derived from ``data.type``.
        """
        pass

    @property
    def type(self):
        """Overworld sprite type id stored in the record.

        Changing this value swaps the icon and behavior represented by the
        world-map sprite without changing its position or other record fields,
        which keeps type cycling localized to the record field that the ROM
        actually stores.
        Draw, status-text, and serialization paths all read the same value, so
        this property marks the central boundary between editor interactions
        and the underlying ``SpriteData`` payload.

        Returns
        -------
        int
            Sprite type stored in ``data``.
        """
        return self.data.type

    @type.setter
    def type(self, value):
        """Change the overworld sprite type.

        Parameters
        ----------
        value : int
            Replacement sprite type id.
        """
        self.change_type(value)

    def draw(self, painter, block_length, transparent, selected=False):
        """Draw the sprite icon at its world-map position.

        The map view uses the decoded sprite-sheet image rather than the raw
        ROM record so moving sprites redraw immediately.

        Parameters
        ----------
        painter : QPainter
            Painter receiving the sprite image.
        block_length : int
            Pixel size of one world-map tile.
        transparent : bool
            Unused compatibility flag for shared draw call sites.
        selected : bool, optional
            Whether to overlay the selection highlight.
        """
        pos = QPoint(*self.data.pos.xy) * block_length

        rect = QRect(pos, QSize(block_length, block_length))

        painter.drawImage(
            rect.topLeft(),
            MAP_OBJ_SPRITES[self.data.type].scaled(block_length, block_length),
        )

        if selected:
            painter.fillRect(rect, QColor(0x00, 0xFF, 0x00, 0x80))

    def set_position(self, x, y):
        """Store a new world-map position for the sprite.

        Dragging and keyboard movement update the underlying ``SpriteData``
        through this shared position API.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.
        """
        self.data.pos = Position.from_xy(x, y)

    def get_position(self) -> tuple[int, int]:
        """World-map position for the sprite.

        Shared map-object tools consume the tuple without depending on the
        underlying ``SpriteData`` structure.

        Returns
        -------
        tuple[int, int]
            Horizontal and vertical tile coordinates.
        """
        return self.data.pos.xy

    def change_type(self, new_type):
        """Store a new sprite type in the ROM-backed record.

        Parameters from selection widgets and keyboard cycling write through to
        the stored ``SpriteData`` field here so redraw, labeling, and ROM-save
        code all observe the same type change.

        Parameters
        ----------
        new_type : int
            Replacement sprite type id.

        Examples
        --------
        Change the shared sprite type field and verify that the wrapped
        ``SpriteData`` record reflects the same update::

            sprite_data = SpriteData(Position.from_xy(3, 5), MAPOBJ_HELP, 0)
            sprite = Sprite(sprite_data)

            sprite.change_type(MAPOBJ_AIRSHIP)

            sprite.type
            MAPOBJ_AIRSHIP
            sprite.data.type
            MAPOBJ_AIRSHIP
        """
        self.data.type = new_type
