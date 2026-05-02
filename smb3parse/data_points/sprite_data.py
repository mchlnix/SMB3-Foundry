"""ROM-backed world-map sprite records for SMB3 overworld editing.

This module models one movable overworld sprite entry inside the world-map
structure block parsed by :class:`~smb3parse.data_points.world_map_data.WorldMapData`.
``SpriteData`` resolves the per-world pointer tables that store sprite
screens, coordinates, sprite types, and reward items, then exposes that data as
mutable Python attributes that can be cleared or written back to a ROM.

The class sits between world-map metadata discovery and higher-level editing
tools. ``WorldMapData`` owns the shared structure-data base offset for a world,
``SpriteData`` converts that structure into concrete record addresses for one
sprite index, and callers then mutate those decoded fields before persisting
them through :class:`~smb3parse.util.rom.Rom`.

See Also
--------
smb3parse.data_points.world_map_data.WorldMapData
    Provides the world-specific structure block that sprite records are indexed
    from.
smb3parse.data_points.util.DataPoint
    Defines the ROM-backed load and save lifecycle implemented by
    ``SpriteData``.
"""

from smb3parse.constants import (
    BASE_OFFSET,
    MAPITEM_NOITEM,
    MAPOBJ_EMPTY,
    OFFSET_SIZE,
    PAGE_C000_OFFSET,
    Constants,
)
from smb3parse.data_points.util import DataPoint, _IndexedMixin, _PositionMixin
from smb3parse.data_points.world_map_data import WorldMapData
from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.util.rom import Rom


class SpriteData(_PositionMixin, _IndexedMixin, DataPoint):
    """Represent one overworld sprite record inside a world-map data block.

    Instances of this class decode the five parallel sprite lists used by SMB3
    world maps: screen, x position, y position, sprite type, and carried item.
    The object keeps both the resolved ROM addresses and the editable decoded
    values so callers can inspect, clear, or rewrite one sprite entry without
    recalculating the surrounding table layout.

    Parameters
    ----------
    world_map_data : WorldMapData
        Parsed world-map data that owns the shared ROM handle and the per-world
        structure-data block containing sprite lists.
    index : int
        Zero-based sprite entry inside the world's sprite tables.

    Attributes
    ----------
    world : WorldMapData
        World-map record that owns the shared ROM and structure-data block.
    index : int
        Zero-based sprite slot addressed by this object.
    screen_address : int
        Address of the sprite's screen-selection byte.
    screen : int
        Zero-based world-map screen that the sprite belongs to.
    _x_pos_address : int
        Address of the nibble-packed x-position byte.
    x : int
        Column inside the selected screen.
    _y_pos_address : int
        Address of the nibble-packed y-position byte.
    y : int
        Row inside the selected screen.
    _type_address : int
        Address of the sprite-type byte.
    type : int
        Encoded overworld sprite identifier, such as Hammer Brother or
        airship.
    _item_address : int
        Address of the item-reward byte.
    item : int
        Encoded reward item granted after defeating the sprite, when the sprite
        family uses one.

    Notes
    -----
    SMB3 stores world-map sprite fields as five parallel lists rather than as
    packed records. ``SpriteData`` preserves that layout by calculating each
    list address once and then reading or writing the entry at ``index`` across
    all five lists.
    """

    def __init__(self, world_map_data: WorldMapData, index: int):
        """Initialize an editable view of one world-map sprite entry.

        The constructor records the owning world-map data object, allocates
        placeholders for the resolved sprite-field addresses, and seeds the
        decoded values with empty defaults. The inherited ``DataPoint``
        lifecycle then uses the shared ROM from ``world_map_data`` to calculate
        addresses and load the entry's persisted values.

        Parameters
        ----------
        world_map_data : WorldMapData
            Parsed world-map data object that owns the ROM handle and the
            world-specific structure-data block.
        index : int
            Zero-based sprite slot inside that world's parallel sprite lists.
        """
        self.world = world_map_data
        self.index = index

        self.screen_address = 0x0
        self.screen = 0

        self._x_pos_address = 0x0
        self.x = 0

        self._y_pos_address = 0x0
        self.y = 0

        self._type_address = 0x0
        self.type = MAPOBJ_EMPTY

        self._item_address = 0x0
        self.item = MAPITEM_NOITEM

        super(SpriteData, self).__init__(self.world._rom)

    def calculate_addresses(self):
        """Resolve the ROM addresses for this sprite across all field lists.

        SMB3 keeps world-map sprite coordinates, screen indices, sprite types,
        and reward items in five separate per-world lists. This method walks
        the structure block owned by :attr:`world` to locate the list for the
        selected world and then stores the concrete entry address for
        :attr:`index` in each list.
        """
        map_sprite_y_pos_list = Constants.Map_List_Object_Ys
        map_sprite_screen_list = map_sprite_y_pos_list + 8 * OFFSET_SIZE  # 8 for the eight non-warp world maps
        map_sprite_x_pos_list = map_sprite_screen_list + 8 * OFFSET_SIZE
        map_sprite_types_list = map_sprite_x_pos_list + 8 * OFFSET_SIZE
        map_sprite_items_list = map_sprite_types_list + 8 * OFFSET_SIZE

        self._y_pos_address = self._get_address_from_list(map_sprite_y_pos_list)

        self.screen_address = self._get_address_from_list(map_sprite_screen_list)

        self._x_pos_address = self._get_address_from_list(map_sprite_x_pos_list)

        self._type_address = self._get_address_from_list(map_sprite_types_list)

        self._item_address = self._get_address_from_list(map_sprite_items_list)

    def _get_address_from_list(self, list_of_list_address: int) -> int:
        """Resolve this sprite's entry address from a per-world pointer table.

        The structure block stores one pointer table per sprite field. Each
        entry in that table points to the field list for one world. This helper
        first resolves the list address for :attr:`world.index`, then advances
        to :attr:`index` inside that world's list. :meth:`calculate_addresses`
        calls this helper once for every parallel sprite field so one sprite
        object can keep a stable set of ROM addresses while :meth:`read_values`
        and :meth:`write_back` move decoded state through those addresses.

        Parameters
        ----------
        list_of_list_address : int
            Address of the per-world pointer table for one sprite field.

        Returns
        -------
        int
            Concrete ROM address of this sprite's field entry inside the
            resolved world-specific list.
        """
        list_offset = self._rom.little_endian(list_of_list_address + self.world.index * OFFSET_SIZE)
        list_address = BASE_OFFSET + PAGE_C000_OFFSET + list_offset

        return list_address + self.index

    def read_values(self):
        """Load the sprite's decoded values from its resolved ROM addresses.

        After :meth:`calculate_addresses` has located the five field entries,
        this method reads the stored screen, unpacked x and y coordinates,
        sprite type, and optional reward item into the mutable attributes that
        editors consume.
        """
        self.screen = self._rom.int(self.screen_address)

        # lower nibble is 0 and is unused
        self.x, _ = self._rom.nibbles(self._x_pos_address)
        self.y, _ = self._rom.nibbles(self._y_pos_address)

        self.type = self._rom.int(self._type_address)
        self.item = self._rom.int(self._item_address)

    def clear(self):
        """Reset the decoded sprite values to the empty-world-map defaults.

        This does not remove the sprite from ROM by itself. Instead it stages a
        blank entry that callers can later persist with :meth:`write_back`,
        using the same default values SMB3 expects for an unused sprite slot.
        """
        self.screen = 0
        self.x = 0
        self.y = FIRST_VALID_ROW
        self.type = MAPOBJ_EMPTY
        self.item = MAPITEM_NOITEM

    def write_back(self, rom: Rom | None = None):
        """Persist the staged sprite values back into a ROM image.

        Parameters
        ----------
        rom : Rom | None, optional
            Alternate ROM target to write into. When omitted, the method writes
            back into the same ROM instance used during decoding.

        Notes
        -----
        The x and y coordinates are stored as nibble-packed bytes in SMB3's
        world-map sprite data. ``write_back`` preserves that encoding by using
        :meth:`~smb3parse.util.rom.Rom.write_nibbles` for the coordinate
        fields while writing the remaining fields as full bytes.
        """
        if rom is None:
            rom = self._rom

        rom.write(self.screen_address, self.screen)
        rom.write_nibbles(self._x_pos_address, self.x)
        rom.write_nibbles(self._y_pos_address, self.y)
        rom.write(self._type_address, self.type)
        rom.write(self._item_address, self.item)
