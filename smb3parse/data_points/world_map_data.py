"""Parse and rewrite one SMB3 world-map metadata record.

This module exposes :class:`WorldMapData`, the central ROM-backed data point
that gathers all per-world overworld state needed by editors and serializers.
It resolves the address tables for map layout tiles, palette and animation
settings, screen-scoped level pointers, fortress lock records, airship travel
routes, and the world-specific special-level destinations such as coin ships
and Toad warp houses. Callers mutate those decoded Python attributes and then
persist the staged state back into a :class:`~smb3parse.util.rom.Rom`.

``WorldMapData`` sits above the smaller world-map record types. It owns the
shared structure-block offsets that :class:`~smb3parse.data_points.level_pointer_data.LevelPointerData`
and :class:`~smb3parse.data_points.sprite_data.SpriteData` index into, and it
also keeps the per-world special-level offsets that higher-level Scribe and
Foundry tools surface in overworld editors.

See Also
--------
smb3parse.data_points.level_pointer_data.LevelPointerData
    Parses one level-pointer record from the pointer lists owned by a world.
smb3parse.data_points.sprite_data.SpriteData
    Parses one world-map sprite record from the same structure block family.
smb3parse.levels.world_map.WorldMap
    Higher-level world-map model that consumes the decoded metadata while
    rendering or editing a full overworld.
"""

from collections import defaultdict

from smb3parse.constants import (
    AIR_SHIP_OBJECT_SET,
    AIRSHIP_TRAVEL_SET_COUNT,
    AIRSHIP_TRAVEL_SET_SIZE,
    BASE_OFFSET,
    MUSHROOM_OBJECT_SET,
    OFFSET_SIZE,
    Constants,
)
from smb3parse.data_points import FortressFXData
from smb3parse.data_points.level_pointer_data import LevelPointerData
from smb3parse.data_points.util import DataPoint, Position, _IndexedMixin
from smb3parse.levels import (
    MAX_SCREEN_COUNT,
    WORLD_MAP_BASE_OFFSET,
    WORLD_MAP_BLANK_TILE_ID,
    WORLD_MAP_LAYOUT_DELIMITER,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_WARP_WORLD_INDEX,
)
from smb3parse.objects.object_set import ObjectSet
from smb3parse.util.rom import Rom


class WorldMapData(_IndexedMixin, DataPoint):
    """Represent one SMB3 overworld's complete ROM-backed metadata bundle.

    ``WorldMapData`` is the coordination point for per-world overworld data.
    The class resolves the address tables that locate layout tiles, structure
    blocks, level-pointer lists, fortress lock selections, world-map palette
    settings, and the special destination levels that SMB3 routes to from the
    overworld. Once loaded, callers can treat those values as editable Python
    attributes and then write the updated state back while preserving SMB3's
    pointer-table and offset conventions.

    Parameters
    ----------
    rom : Rom
        ROM image that stores the overworld tables and structure blocks for
        all worlds.
    world_index : int
        Zero-based world index whose metadata should be decoded.

    Attributes
    ----------
    index : int
        Zero-based world index addressed by this instance.
    palette_index_address : int
        Address of the per-world tile-palette selector byte.
    palette_index : int
        World-map tile palette selected for this overworld.
    obj_color_index_address : int
        Address of the per-world overworld-sprite palette selector byte.
    obj_color_index : int
        Overworld-sprite palette selected for moving map objects.
    map_start_y_address : int
        Address of the per-world Mario start-row byte.
    map_start_y : int
        Mario's starting row when the world map is entered.
    map_scroll_address : int
        Address of the per-world horizontal-scroll enable byte.
    map_scroll : int
        Flag that controls whether the player can pan into later screens.
    tile_data_offset_address : int
        Address of the per-world pointer that locates the layout tile buffer.
    tile_data_offset : int
        Layout buffer offset relative to :data:`WORLD_MAP_BASE_OFFSET`.
    tile_data : bytearray
        Contiguous tile-id buffer for all screens in this world, excluding the
        delimiter byte stored after the layout in ROM.
    bottom_border_tile_address : int
        Address of the per-world table entry that stores
        ``bottom_border_tile``.
    bottom_border_tile : int
        Tile id used to fill the bottom border row around the world map.
    frame_tick_count_address : int
        Address of the animation-speed table entry used for this world.
    frame_tick_count : int
        Animation timing value that controls how quickly animated world tiles
        advance.
    structure_data_offset_address : int
        Address of the per-world pointer that locates the structure block.
    structure_data_offset : int
        Structure-block offset relative to :data:`WORLD_MAP_BASE_OFFSET`.
    pos_offsets_for_screen : bytearray
        Four-byte table that records the starting level-pointer index for each
        world-map screen.
    y_pos_list_start_address : int
        Address of the per-world pointer to the y-position list.
    y_pos_list_start : int
        Absolute ROM address of the structure-block list that stores the
        y-coordinate for each level pointer.
    x_pos_list_start_address : int
        Address of the per-world pointer to the x-position list.
    x_pos_list_start : int
        Absolute ROM address of the structure-block list that stores the
        x-coordinate for each level pointer.
    enemy_offset_list_offset_address : int
        Address of the per-world pointer to the enemy-offset list.
    enemy_offset_list_offset : int
        Structure-block-relative offset to the enemy-address list paired with
        ``level_pointers``.
    level_offset_list_offset_address : int
        Address of the per-world pointer to the level-layout offset list.
    level_offset_list_offset : int
        Structure-block-relative offset to the level-layout list paired with
        ``level_pointers``.
    level_pointers : list[LevelPointerData]
        Decoded list of level-pointer records owned by this world.
    fortress_fx : list[FortressFXData]
        Decoded lock and bridge animation records selected by this world.
    fortress_fx_indexes : list[int]
        Fortress-effect index bytes staged between the world-local selector
        table and the decoded ``fortress_fx`` records.
    fortress_fx_base_index : int
        Starting index into the shared fortress-effect selector table for this
        world.
    fortress_fx_base_index_address : int
        Address of the per-world selector-table entry that stores
        ``fortress_fx_base_index``.
    fortress_fx_count : int
        Number of fortress effect records currently selected for the world.
    airship_travel_sets : tuple[list[Position], list[Position], list[Position]]
        Three candidate six-step airship routes that SMB3 may choose from when
        loading the world.
    airship_travel_x_set_address : int
        Address of the pointer table for the x/screen halves of the world's
        airship routes.
    airship_travel_y_set_address : int
        Address of the pointer table for the y halves of the world's airship
        routes.
    airship_travel_base_index : int
        Starting selector index for the world's three airship travel routes.
    airship_travel_base_index_address : int
        Address of the per-world selector-table entry that stores
        ``airship_travel_base_index``.
    airship_level_offset_address : int
        Address of the per-world airship-layout offset table entry.
    airship_level_offset : int
        Offset to the world-specific airship layout within the fixed airship
        object-set bank.
    airship_enemy_offset_address : int
        Address of the per-world airship-enemy offset table entry.
    airship_enemy_offset : int
        Base-offset-relative pointer to the world-specific airship enemy
        stream.
    coin_ship_level_offset_address : int
        Address of the per-world coin-ship layout offset table entry.
    coin_ship_level_offset : int
        Offset to the world-specific coin-ship layout within the fixed airship
        object-set bank.
    coin_ship_enemy_offset_address : int
        Address of the per-world coin-ship enemy offset table entry.
    coin_ship_enemy_offset : int
        Base-offset-relative pointer to the world-specific coin-ship enemy
        stream.
    generic_exit_object_set_address : int
        Address of the per-world object-set byte for the generic-exit
        destination.
    generic_exit_object_set : int
        Object-set id used when resolving the world's generic-exit fallback
        destination.
    generic_exit_level_offset_address : int
        Address of the per-world generic-exit layout offset table entry.
    generic_exit_level_offset : int
        Offset to the generic-exit layout within ``generic_exit_object_set``.
    generic_exit_enemy_offset_address : int
        Address of the per-world generic-exit enemy offset table entry.
    generic_exit_enemy_offset : int
        Base-offset-relative pointer to the generic-exit enemy stream.
    big_q_block_object_set_address : int
        Address of the per-world object-set byte for the big-question-block
        destination.
    big_q_block_object_set : int
        Object-set id used when resolving the world's big-question-block
        destination.
    big_q_block_level_offset_address : int
        Address of the per-world big-question-block layout offset table entry.
    big_q_block_level_offset : int
        Offset to the big-question-block layout within
        ``big_q_block_object_set``.
    big_q_block_enemy_offset_address : int
        Address of the per-world big-question-block enemy offset table entry.
    big_q_block_enemy_offset : int
        Base-offset-relative pointer to the big-question-block enemy stream.
    toad_warp_level_offset_address : int
        Address of the per-world Toad-house layout offset table entry.
    toad_warp_level_offset : int
        Offset to the world-specific Toad-house reward layout within the fixed
        mushroom-house object-set bank.
    toad_warp_item_address : int
        Address of the per-world reward-item byte for the Toad house.
    toad_warp_item : int
        Encoded reward item value that SMB3 reads from the Toad-house object
        slot.
    music_index_address : int
        Address of the per-world world-map theme table entry.
    music_index : int
        Theme played when the world is entered fresh.
    music_arrival_index_address : int
        Address of the per-world reentry theme table entry.
    music_arrival_index : int
        Theme played when reentering the world after returning from a level.
    structure_block_address : int
        Absolute ROM address of the structure block derived from
        ``structure_data_offset``.
    generic_exit_level_address : int
        Absolute ROM address derived from the generic-exit object set plus its
        stored layout offset.
    generic_exit_enemy_address : int
        Absolute ROM address derived from the generic-exit enemy offset stored
        in the world tables.
    toad_warp_object_set : int
        Fixed object-set id SMB3 always uses for world-specific Toad-house
        reward levels.
    tile_data_size : int
        Serialized size of ``tile_data`` plus the delimiter byte that SMB3
        writes after the map layout.
    screen_count : int
        Number of layout screens implied by the decoded ``tile_data`` buffer.
    level_count : int
        Number of decoded level-pointer records implied by the structure-block
        list boundaries.
    level_count_screen_1 : int
        Derived count of level pointers assigned to screen 1.
    level_count_screen_2 : int
        Derived count of level pointers assigned to screen 2.
    level_count_screen_3 : int
        Derived count of level pointers assigned to screen 3.
    level_count_screen_4 : int
        Derived count of level pointers assigned to screen 4.

    Notes
    -----
    SMB3 stores world-map metadata as a mix of direct per-world tables and
    structure blocks reached through little-endian offsets. This class keeps
    both the resolved addresses and the decoded values so editors can
    rearrange world state without recalculating every pointer table by hand.
    """

    def __init__(self, rom: Rom, world_index: int):
        """Decode one world's editable overworld metadata.

        The initializer records the target world index, allocates placeholders
        for every address-backed field that participates in the overworld
        workflow, and seeds mutable containers for the variable-length data
        sets such as tile buffers, level pointers, fortress locks, and airship
        routes. The inherited :class:`DataPoint` lifecycle then calculates the
        ROM addresses for those fields and immediately loads the persisted
        values from ``rom``.

        Parameters
        ----------
        rom : Rom
            ROM image that stores the world-map tables and structure blocks.
        world_index : int
            Zero-based world slot to decode.
        """
        self.index = world_index

        self.tile_data_offset_address = 0x0
        self.tile_data_offset = 0x0
        """The offset into the RAM the tile data for this World Map is located, when its PRG is loaded."""

        self.tile_data = bytearray()
        """
        All the Tile IDs, that make up the layout of the World Map. Will be a multiple of 16 x 9 tile IDs, depending on
        how many screens there are.
        """

        self.bottom_border_tile_address = 0x0
        self.bottom_border_tile = 0x0
        """The Tile ID, that is used to fill the bottom row of the border around the World Map."""

        self.palette_index_address = 0x0
        self.palette_index = 0
        """Which color palette should be used with this World Map."""

        self.obj_color_index_address = 0x0
        self.obj_color_index = 0
        """Which color palette should be used for the Overworld Sprites, like Hammer Bros."""

        self.frame_tick_count_address = 0
        self.frame_tick_count = 0
        """
        How many ticks each animation frame stays on screen, before switching to the next. The higher this value is, the
        slower the animated Tiles are changing. 0 means no animation.
        """

        self.structure_data_offset_address = 0x0
        self.structure_data_offset = 0x0
        """
        The structure data is a handful of lists for the Level and Sprite Locations and their types and items. All the
        lists appear one after another, making it one block of data.
        """

        self.map_start_y_address = 0x0
        self.map_start_y = 0
        """
        The y Position of where Mario starts, when entering the Overworld. In the vanilla game the x coordinate is hard
        coded to column 2, so only the y/row position can be changed.
        """

        self.map_scroll_address = 0x0
        self.map_scroll = 0
        """
        Determines, whether the screen should scroll onto the next, when the player reaches the edge of their current
        screen.
        If disabled, it can hide, that this world has multiple screens, as in World 5.
        """

        self.airship_travel_base_index_address = 0x0
        self.airship_travel_base_index = 0
        """
        All Airship travel routes are in one large list. Every World Map can have 3 indexes into this list, therefore
        selecting 3 of these routes for it to use. Which one of these three is then used is determined randomly, when
        the World Map is initially loaded.

        These 3 times 8 (without Warp World) indexes are in one long list and each World Map remembers where its 3
        indexes are by saving that index. In the Vanilla Game, the indexes are simply the world number (0-indexed)
        times 3, so 0x0, 0x3, 0x6 etc.

        One could change this, so that two worlds use the exact same indexes, for example. But since there is enough
        space for every World to choose its own 3 indexes, there is no reason to do such a thing.

        So changing this value should not be necessary.
        """

        self.airship_travel_x_set_address = 0x0
        self.airship_travel_y_set_address = 0x0

        self.airship_travel_sets: tuple[list[Position], list[Position], list[Position]] = ([], [], [])
        """
        Each World Map has 3 possible Airship routes, one of which is chosen at random, when the World Map is initially
        loaded.

        Each of them has 6 Positions on the world map, which the Airship is traveling along.
        """

        # lock and bridge data
        self.fortress_fx_base_index_address = 0x0
        self.fortress_fx_base_index = 0
        """
        See also FortressFXData.

        Similar to the Airship routes, there is a list of FortressFX data points, except that each World Map gets 4.

        There are a total of 17 possible locks, which each World can choose from. In the Vanilla game, there is no
        overlap between Worlds, but if the layout makes sense two Worlds can share Locks.

        Since each World has space to define 4 locks, there is no reason to change this value.
        """

        self.fortress_fx_indexes: list[int] = []
        """The 4 indexes into the list of 17 locks, that the World has chosen."""

        self.fortress_fx_count = 0
        """Amount of locks this World has designated. Should always be 4."""

        self.fortress_fx: list[FortressFXData] = []
        """The FortressFxData objects, this World has selected."""

        # level pointer data
        self.pos_offsets_for_screen = bytearray(MAX_SCREEN_COUNT)
        """
        When entering a Level, a list of level positions is combed through. Once the player's current position is found
        that Position's index is used to look up the Level information in another list.

        Since these positions are ordered by screen and to make searching faster, the game saves the first position of
        each screen in this list.

        Four bytes, one for each screen, where the first byte is naturally always 0.
        """

        self.y_pos_list_start_address = 0x0
        self.y_pos_list_start = 0x0
        """
        The address of the list of y Positions for Level Pointers for this World Map.

        When trying to find the Level the player is standing on, first the y Positions are gone through, until a
        suitable one was found, then, from that index on, the x Positions are gone through until a match is found there,
        too.

        That index can then be used to find the Level and Enemy/Item Offset of that Level.
        """

        self.x_pos_list_start_address = 0x0
        self.x_pos_list_start = 0x0
        """See y_pos_list_start."""

        self.enemy_offset_list_offset_address = 0x0
        self.enemy_offset_list_offset = 0x0
        """See y_pos_list_start."""

        self.level_offset_list_offset_address = 0x0
        self.level_offset_list_offset = 0x0
        """See y_pos_list_start."""

        self.level_pointers: list[LevelPointerData] = []
        """
        The parsed information of Position on World Map, location in memory and Object set of all Level Pointers this
        World has defined.
        """

        self.airship_enemy_offset_address = 0x0
        self.airship_enemy_offset = 0x0
        self.airship_level_offset_address = 0x0
        self.airship_level_offset = 0x0
        """
        The Airship Level that leads you to a Koopa Kid is defined per World, so you go to the same one each time. Its
        Object Set is hard coded as Airship.
        """

        self.coin_ship_enemy_offset_address = 0x0
        self.coin_ship_enemy_offset = 0x0
        self.coin_ship_level_offset_address = 0x0
        self.coin_ship_level_offset = 0x0
        """
        The coin ship Bonus Level that you get to via the overworld Sprite. It is defined per World, so you go to the
        same one each time. Its Object Set is hard coded as Airship.
        """

        self.generic_exit_object_set_address = 0x0
        self.generic_exit_object_set = 0
        self.generic_exit_enemy_offset_address = 0x0
        self.generic_exit_enemy_offset = 0x0
        self.generic_exit_level_offset_address = 0x0
        self.generic_exit_level_offset = 0x0
        """
        Some Object Sets have a Pipe, that ignores the Jump Destination of the Header and instead goes to a Level that
        is supposed to be used like a Generic Exit, allowing both this and a bonus level via normal Pipes. That level
        can be set per World. In the Vanilla Game the Object Set is always Plains, but this can actually be configured.
        """

        self.big_q_block_object_set_address = 0x0
        self.big_q_block_object_set = 0
        self.big_q_block_enemy_offset_address = 0x0
        self.big_q_block_enemy_offset = 0x0
        self.big_q_block_level_offset_address = 0x0
        self.big_q_block_level_offset = 0x0
        """
        Some Object Sets have a Pipe, that ignores the Jump Destination of the Header and instead goes to a Level with a
        Big Question Mark Block, that can be set per World. In the Vanilla Game the Object Set is always Underground,
        but this can actually be configured.
        """

        self.toad_warp_level_offset_address = 0x0
        self.toad_warp_level_offset = 0x0
        """
        The address of the Toad Level. Even though it does not look like a normal level, it is still saved in the ROM as
        one. Every Overworld could have its own, but they all have the same in the Vanilla game.
        """

        self.toad_warp_item_address = 0x0
        self.toad_warp_item = 0
        """
        Is saved as an offset, but only determines what is in the Toad Chest in the upper nibble. 0x02(00) for the warp
        whistle, 0x0A(00) for the Anchor.
        """

        self.music_index_address = 0x0
        self.music_index = 0x0
        """
        The index of the music theme, that is played in the overworld, when it is first entered.
        """

        self.music_arrival_index_address = 0x0
        self.music_arrival_index = 0x0
        """
        The index of the music theme, that is played in the overworld, after reentering the level, e.g. after dying. Not
        sure why it is called Arrival in the disassembly.
        """

        super(WorldMapData, self).__init__(rom)

    def calculate_addresses(self):
        """Resolve all per-world ROM addresses that back this metadata bundle.

        SMB3 spreads overworld data across multiple global tables. This method
        translates ``index`` into the concrete addresses for the selected
        world's layout pointer, structure-block pointer, special-level offset
        tables, palette settings, and route-selection tables. Later lifecycle
        stages reuse those resolved addresses so they can read and write values
        without repeating table arithmetic.
        """
        self.tile_data_offset_address = Constants.LAYOUT_LIST_OFFSET + OFFSET_SIZE * self.index

        self.palette_index_address = Constants.Map_Tile_ColorSets + self.index
        self.obj_color_index_address = Constants.Map_Object_ColorSets + self.index

        self.bottom_border_tile_address = Constants.Map_Bottom_Tiles + self.index
        # TODO you can define a separate tick count for each anim frame, not used in game though
        self.frame_tick_count_address = Constants.Map_AnimSpeeds + self.index * 4  # 4 animation frames

        self.structure_data_offset_address = Constants.STRUCTURE_DATA_OFFSETS + OFFSET_SIZE * self.index

        self.y_pos_list_start_address = Constants.LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.index
        self.x_pos_list_start_address = Constants.LEVEL_X_POS_LISTS + OFFSET_SIZE * self.index

        self.enemy_offset_list_offset_address = Constants.LEVEL_ENEMY_LIST_OFFSET + self.index * OFFSET_SIZE
        self.level_offset_list_offset_address = Constants.LEVELS_IN_WORLD_LIST_OFFSET + self.index * OFFSET_SIZE

        self.map_start_y_address = Constants.Map_Y_Starts + self.index
        self.map_scroll_address = Constants.World_Map_Max_PanR + self.index

        # unused, because the value is always 0x03 * world_index
        self.airship_travel_base_index_address = Constants.Map_Airship_Travel_BaseIdx + self.index

        self.airship_travel_x_set_address = (
            Constants.Map_Airship_Dest_XSets + AIRSHIP_TRAVEL_SET_COUNT * OFFSET_SIZE * self.index
        )
        self.airship_travel_y_set_address = (
            Constants.Map_Airship_Dest_YSets + AIRSHIP_TRAVEL_SET_COUNT * OFFSET_SIZE * self.index
        )

        self.fortress_fx_base_index_address = Constants.FortressFXBase_ByWorld + self.index
        self.fortress_fx_base_index = self._rom.int(self.fortress_fx_base_index_address)

        self.airship_level_offset_address = Constants.Airship_Layouts + OFFSET_SIZE * self.index
        self.airship_enemy_offset_address = Constants.Airship_Objects + OFFSET_SIZE * self.index

        self.coin_ship_level_offset_address = Constants.CoinShip_Layouts + OFFSET_SIZE * self.index
        self.coin_ship_enemy_offset_address = Constants.CoinShip_Objects + OFFSET_SIZE * self.index

        self.generic_exit_level_offset_address = Constants.LevelJctGE_Layout + OFFSET_SIZE * self.index
        self.generic_exit_enemy_offset_address = Constants.LevelJctGE_Objects + OFFSET_SIZE * self.index
        self.generic_exit_object_set_address = Constants.LevelJctGE_Tileset + self.index

        self.big_q_block_level_offset_address = Constants.LevelJctBQ_Layout + OFFSET_SIZE * self.index
        self.big_q_block_enemy_offset_address = Constants.LevelJctBQ_Objects + OFFSET_SIZE * self.index
        self.big_q_block_object_set_address = Constants.LevelJctBQ_Tileset + self.index

        self.toad_warp_level_offset_address = Constants.ToadShop_Layouts + OFFSET_SIZE * self.index
        self.toad_warp_item_address = Constants.ToadShop_Objects + OFFSET_SIZE * self.index

        self.music_index_address = Constants.World_BGM + self.index
        self.music_arrival_index_address = Constants.World_BGM_Arrival + self.index

    def read_values(self):
        """Load decoded world-map state from the resolved ROM addresses.

        After :meth:`calculate_addresses` has located the per-world tables,
        this method walks each table and converts the stored bytes into the
        mutable Python attributes that editors consume. That includes the
        variable-length layout tiles, screen-partitioned level-pointer lists,
        fortress lock selections, the three candidate airship routes, and the
        world-specific special-level destinations.

        The load proceeds in dependency order across four stages. First it
        resolves the variable-length layout and structure-block pointers.
        Second it reconstructs the level-pointer structure block, including the
        screen-offset table and the nested :class:`LevelPointerData` records
        that depend on those list starts. Third it rebuilds fortress and
        airship collections that consume world-local selector offsets. Last it
        loads the remaining scalar tables for palette, scroll, music, and the
        world-specific special-level destinations.

        Notes
        -----
        The level-pointer portion of the structure block is self-describing
        only through the screen-offset table and the x/y list spacing. The
        method therefore reconstructs ``level_count`` from the decoded list
        starts before instantiating :class:`LevelPointerData` records.

        The method also establishes the staged-state boundary for the rest of
        the class. Every derived address property, every per-screen level-count
        view, and every special-destination helper reads fields populated here,
        while :meth:`write_back` later serializes those same staged fields back
        into ROM.
        """
        self.tile_data_offset = self._rom.little_endian(self.tile_data_offset_address)
        self.tile_data = self._rom.read_until(self.layout_address, WORLD_MAP_LAYOUT_DELIMITER)

        self.palette_index = self._rom.int(self.palette_index_address)
        self.obj_color_index = self._rom.int(self.obj_color_index_address)

        self.bottom_border_tile = self._rom.int(self.bottom_border_tile_address)
        self.frame_tick_count = self._rom.int(self.frame_tick_count_address)

        self.structure_data_offset = self._rom.little_endian(self.structure_data_offset_address)

        self.pos_offsets_for_screen = self._rom.read(self.structure_block_address, MAX_SCREEN_COUNT)

        self.y_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(self.y_pos_list_start_address)
        self.x_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(self.x_pos_list_start_address)

        self.level_pointers = [LevelPointerData(self, index) for index in range(self.level_count)]

        self.enemy_offset_list_offset = self._rom.little_endian(self.enemy_offset_list_offset_address)
        self.level_offset_list_offset = self._rom.little_endian(self.level_offset_list_offset_address)

        if self.index != WORLD_MAP_WARP_WORLD_INDEX:
            assert self.level_offset_list_offset == self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE, (
                hex(self.level_offset_list_offset - self.enemy_offset_list_offset),
                self.level_count,
            )

        self.map_start_y = self._rom.int(self.map_start_y_address)
        self.map_scroll = self._rom.int(self.map_scroll_address)

        self.airship_travel_base_index = self._rom.int(self.airship_travel_base_index_address)

        for set_number in range(AIRSHIP_TRAVEL_SET_COUNT):
            self.airship_travel_sets[set_number].clear()

            offset_x = self._rom.little_endian(self.airship_travel_x_set_address + set_number * OFFSET_SIZE)
            offset_y = self._rom.little_endian(self.airship_travel_y_set_address + set_number * OFFSET_SIZE)

            for index in range(AIRSHIP_TRAVEL_SET_SIZE):
                x, screen = self._rom.nibbles(BASE_OFFSET + 0xC000 + offset_x + index)
                y, _ = self._rom.nibbles(BASE_OFFSET + 0xC000 + offset_y + index)

                self.airship_travel_sets[set_number].append(Position(x, y, screen))

        self.fortress_fx_base_index = self._rom.int(self.fortress_fx_base_index_address)
        self.fortress_fx_count = self._rom.int(self.fortress_fx_base_index_address + 1) - self.fortress_fx_base_index

        self.fortress_fx.clear()
        self.fortress_fx_indexes.clear()

        for offset in range(self.fortress_fx_count):
            index = self._rom.int(self.fortress_fx_indexes_start_address + offset)

            self.fortress_fx.append(FortressFXData(self._rom, index))
            self.fortress_fx_indexes.append(index)

        self.airship_level_offset = self._rom.little_endian(self.airship_level_offset_address)
        self.airship_enemy_offset = self._rom.little_endian(self.airship_enemy_offset_address)

        self.coin_ship_level_offset = self._rom.little_endian(self.coin_ship_level_offset_address)
        self.coin_ship_enemy_offset = self._rom.little_endian(self.coin_ship_enemy_offset_address)

        self.generic_exit_level_offset = self._rom.little_endian(self.generic_exit_level_offset_address)
        self.generic_exit_enemy_offset = self._rom.little_endian(self.generic_exit_enemy_offset_address)
        self.generic_exit_object_set = self._rom.int(self.generic_exit_object_set_address)

        self.big_q_block_level_offset = self._rom.little_endian(self.big_q_block_level_offset_address)
        self.big_q_block_enemy_offset = self._rom.little_endian(self.big_q_block_enemy_offset_address)
        self.big_q_block_object_set = self._rom.int(self.big_q_block_object_set_address)

        self.toad_warp_level_offset = self._rom.little_endian(self.toad_warp_level_offset_address)
        self.toad_warp_item = self._rom.little_endian(self.toad_warp_item_address)

        self.music_index = self._rom.int(self.music_index_address)
        self.music_arrival_index = self._rom.int(self.music_arrival_index_address)

    def write_back(self, rom: Rom | None = None):
        """Persist the staged world-map metadata back into a ROM image.

        ``WorldMapData`` treats edits as staged Python state until this method
        runs. The method is therefore both a serializer and a normalization
        pass: it rewrites pointer tables, re-derives screen-local level counts
        from the sorted ``level_pointers`` list, and then commits every
        dependent nested record in the order SMB3 expects to read them.

        Parameters
        ----------
        rom : Rom | None, optional
            Alternate ROM target to write into. When omitted, the method writes
            into the same ROM instance used during decoding.

        Notes
        -----
        ``WorldMapData`` owns several interdependent lists inside the world
        structure block, so the commit is staged rather than flat. The method
        first rewrites top-level pointer and scalar tables, then normalizes the
        sorted level-pointer collection and its cumulative screen counts,
        commits the rebuilt structure-block pointers, serializes each nested
        :class:`LevelPointerData`, and finally writes the special-destination,
        fortress, and music values that hang off the same world index. That
        ordering preserves the ROM contract for downstream readers that rebuild
        the same world-map metadata from the stored offsets.

        In practice this is the commit boundary for every derived address
        property in the class. Setters stage offsets in Python attributes, and
        ``write_back`` is what converts that staged world state back into the
        pointer tables and structure-block records the game actually consumes.
        """
        if rom is None:
            rom = self._rom

        # tile_data_offset
        rom.write_little_endian(self.tile_data_offset_address, self.tile_data_offset)

        # tile_data
        rom.write(self.layout_address, self.tile_data + WORLD_MAP_LAYOUT_DELIMITER)

        rom.write(self.palette_index_address, self.palette_index)
        rom.write(self.obj_color_index_address, self.obj_color_index)

        rom.write(self.bottom_border_tile_address, self.bottom_border_tile)
        rom.write(self.frame_tick_count_address, bytearray([self.frame_tick_count] * 4))

        # structure_data_offset
        rom.write_little_endian(self.structure_data_offset_address, self.structure_data_offset)

        # values depending on amount of level pointers per screen
        self.level_pointers.sort()
        assert self.level_count == len(self.level_pointers)

        level_pointer_per_screen: dict[int, int] = defaultdict(int)

        for level_pointer in self.level_pointers:
            level_pointer_per_screen[level_pointer.screen] += 1

        self.level_count_screen_1 = level_pointer_per_screen[0]
        self.level_count_screen_2 = level_pointer_per_screen[1]
        self.level_count_screen_3 = level_pointer_per_screen[2]
        self.level_count_screen_4 = level_pointer_per_screen[3]

        # pos_offsets_for_screen
        rom.write(self.structure_block_address, self.pos_offsets_for_screen)

        # y_pos_list_start
        rom.write_little_endian(
            Constants.LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.index,
            self.y_pos_list_start - WORLD_MAP_BASE_OFFSET,
        )

        # x_pos_list_start
        rom.write_little_endian(
            Constants.LEVEL_X_POS_LISTS + OFFSET_SIZE * self.index,
            self.x_pos_list_start - WORLD_MAP_BASE_OFFSET,
        )

        rom.write_little_endian(self.enemy_offset_list_offset_address, self.enemy_offset_list_offset)
        rom.write_little_endian(
            self.level_offset_list_offset_address,
            self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE,
        )

        for index, level_pointer in enumerate(self.level_pointers):
            level_pointer.change_index(index)
            level_pointer.write_back(rom)

        rom.write(self.map_start_y_address, self.map_start_y)
        rom.write(self.map_scroll_address, self.map_scroll)

        rom.write(self.airship_travel_base_index_address, self.airship_travel_base_index)

        for set_number in range(AIRSHIP_TRAVEL_SET_COUNT):
            offset_x = rom.little_endian(self.airship_travel_x_set_address + set_number * OFFSET_SIZE)
            offset_y = rom.little_endian(self.airship_travel_y_set_address + set_number * OFFSET_SIZE)

            for index in range(AIRSHIP_TRAVEL_SET_SIZE):
                pos: Position = self.airship_travel_sets[set_number][index]

                rom.write_nibbles(BASE_OFFSET + 0xC000 + offset_x + index, pos.x, pos.screen)
                rom.write_nibbles(BASE_OFFSET + 0xC000 + offset_y + index, pos.y)

        rom.write(self.fortress_fx_base_index_address, self.fortress_fx_base_index)

        for offset, fortress_fx_data in enumerate(self.fortress_fx):
            rom.write(self.fortress_fx_indexes_start_address + offset, fortress_fx_data.index)

            fortress_fx_data.write_back(rom)

        rom.write_little_endian(self.airship_level_offset_address, self.airship_level_offset)
        rom.write_little_endian(self.airship_enemy_offset_address, self.airship_enemy_offset)

        rom.write_little_endian(self.coin_ship_level_offset_address, self.coin_ship_level_offset)
        rom.write_little_endian(self.coin_ship_enemy_offset_address, self.coin_ship_enemy_offset)

        rom.write_little_endian(self.generic_exit_level_offset_address, self.generic_exit_level_offset)
        rom.write_little_endian(self.generic_exit_enemy_offset_address, self.generic_exit_enemy_offset)
        rom.write(self.generic_exit_object_set_address, self.generic_exit_object_set)

        rom.write_little_endian(self.big_q_block_level_offset_address, self.big_q_block_level_offset)
        rom.write_little_endian(self.big_q_block_enemy_offset_address, self.big_q_block_enemy_offset)
        rom.write(self.big_q_block_object_set_address, self.big_q_block_object_set)

        rom.write_little_endian(self.toad_warp_level_offset_address, self.toad_warp_level_offset)
        rom.write_little_endian(self.toad_warp_item_address, self.toad_warp_item)

        rom.write(self.music_index_address, self.music_index)
        rom.write(self.music_arrival_index_address, self.music_arrival_index)

    @property
    def fortress_fx_indexes_start_address(self):
        """Start address of this world's fortress-lock index list.

        ``read_values`` and ``write_back`` use this derived address as the handoff
        between the world's selected fortress-effect base index and the concrete
        per-lock index bytes that choose which lock records belong to the map.

        Returns
        -------
        int
            ROM address of the first fortress effect index selected by this
            world.
        """
        return Constants.FortressFX_W1 + self.fortress_fx_base_index

    @property
    def structure_block_address(self):
        """Absolute ROM address of the world's structure block.

        This property is the root for the variable-length overworld lists that
        follow the structure block header. Higher-level code reads it when it
        needs to interpret or repoint the level-pointer portion of the world,
        and the paired setter uses the same address as the canonical source for
        rebuilding the dependent list starts after screen-count or level-list
        edits. In other words, this getter is the shared anchor that turns the
        staged structure-block offset loaded by :meth:`read_values` into the
        concrete ROM location that later list math and :meth:`write_back`
        coordinate around.

        Returns
        -------
        int
            Structure-block address derived from ``structure_data_offset``.
        """
        return WORLD_MAP_BASE_OFFSET + self.structure_data_offset

    @structure_block_address.setter
    def structure_block_address(self, value):
        """Move the structure block and rebuild dependent list starts.

        Parameters
        ----------
        value : int
            New absolute ROM address for the start of the structure block.

        Notes
        -----
        The structure block stores the screen-offset table followed by the
        y-position list, x-position list, enemy-offset list, and level-offset
        list. Repointing the block therefore forces all later list starts to be
        recomputed from the preserved level count.
        """
        self.structure_data_offset = value - WORLD_MAP_BASE_OFFSET

        # we need to save the level count here, since it's a property of the two attributes we change here
        level_count = self.level_count

        self.y_pos_list_start = self.structure_block_address + MAX_SCREEN_COUNT
        self.x_pos_list_start = self.y_pos_list_start + level_count

        self.enemy_offset_list_offset = self.x_pos_list_start + self.level_count - WORLD_MAP_BASE_OFFSET
        self.level_offset_list_offset = self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE

    @property
    def structure_block_size(self):
        """Total byte length of the level-pointer portion of the structure block.

        Callers use this size when moving or repacking the structure block so
        the level-pointer lists stay contiguous after the four-byte screen
        offset table.

        Returns
        -------
        int
            Size of the screen-offset table plus the serialized
            :class:`LevelPointerData` records implied by ``level_count``.
        """
        return self.level_count * LevelPointerData.SIZE + len(self.pos_offsets_for_screen)

    @property
    def layout_address(self):
        """Absolute ROM address of the world's layout tile buffer.

        The layout pointer separates fixed per-world tables from the variable
        tile buffer that editors resize when changing ``screen_count`` or
        rewriting the overworld layout itself. ``read_values`` fills
        ``tile_data_offset`` from ROM, callers mutate ``tile_data`` through the
        decoded buffer, and ``write_back`` uses this derived address to commit
        the staged layout bytes back into the world-map bank.

        Returns
        -------
        int
            Layout address derived from ``tile_data_offset``.
        """
        return WORLD_MAP_BASE_OFFSET + self.tile_data_offset

    @layout_address.setter
    def layout_address(self, value):
        """Repoint the world layout buffer.

        Parameters
        ----------
        value : int
            New absolute ROM address for the first layout tile.
        """
        self.tile_data_offset = value - WORLD_MAP_BASE_OFFSET

    @property
    def airship_level_address(self):
        """Absolute ROM address of the world's airship level layout.

        The overworld stores only an offset for this destination. This property
        turns that per-world offset plus the fixed airship object-set bank into
        the absolute ROM address that callers read after editing or before
        loading the linked airship level. In the class workflow,
        :meth:`read_values` populates ``airship_level_offset``, this getter
        turns that staged offset into a usable ROM address, the paired setter
        converts later edits back into offset form, and :meth:`write_back`
        persists the updated bytes.

        Returns
        -------
        int
            Absolute level-layout address derived from the fixed airship object
            set and this world's stored airship offset.
        """
        return ObjectSet(self._rom, self.airship_level_object_set).level_offset + self.airship_level_offset

    @airship_level_address.setter
    def airship_level_address(self, value):
        """Store a new absolute airship level-layout address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the world's airship layout.
        """
        self.airship_level_offset = value - self.airship_level_object_set.level_offset

    @property
    def airship_level_object_set(self):
        """Object set used when decoding the world airship level.

        The property exists so address helpers and higher-level editors can ask
        the world record for the decoding context that goes with the stored
        offsets instead of hard-coding the constant at every call site. The
        address setters and getters use the same value so repointing the
        airship destination preserves the decode bank that ``write_back`` later
        serializes back into the per-world tables.

        Returns
        -------
        int
            Constant airship object-set id used by SMB3 for all airship levels.
        """
        return AIR_SHIP_OBJECT_SET

    @property
    def airship_enemy_address(self):
        """Absolute ROM address of the world airship enemy data.

        SMB3 stores the enemy stream as a base-offset-relative pointer. This
        view converts it into the absolute address used by loaders and editors
        after they change or inspect the staged enemy offset. In the same
        decode/edit/write-back cycle as :attr:`airship_level_address`, this
        getter is the read-side view and the setter is the write-side
        conversion back to SMB3's stored pointer format. Concretely,
        :meth:`read_values` fills ``airship_enemy_offset`` from the world table,
        this getter exposes the ROM stream that level loaders follow, and the
        paired setter turns a replacement stream address back into the stored
        base-offset-relative byte pattern that :meth:`write_back` commits.

        Returns
        -------
        int
            Absolute enemy-data address for the world's airship encounter.
        """
        return BASE_OFFSET + self.airship_enemy_offset

    @airship_enemy_address.setter
    def airship_enemy_address(self, value):
        """Store a new absolute airship enemy-data address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the airship enemy stream.
        """
        self.airship_enemy_offset = value - BASE_OFFSET

    @property
    def coin_ship_level_address(self):
        """Absolute ROM address of the world's coin-ship level layout.

        Like the airship destination, the coin ship keeps only a world-local
        offset in ROM. This property combines that offset with the fixed object
        set so tools can navigate directly to the target layout after staging
        a new destination.

        Returns
        -------
        int
            Absolute level-layout address derived from the coin-ship offset and
            its fixed airship object set.
        """
        return ObjectSet(self._rom, self.coin_ship_level_object_set).level_offset + self.coin_ship_level_offset

    @coin_ship_level_address.setter
    def coin_ship_level_address(self, value):
        """Store a new absolute coin-ship level-layout address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the coin-ship layout.
        """
        self.coin_ship_level_offset = value - ObjectSet(self._rom, self.coin_ship_level_object_set).level_offset

    @property
    def coin_ship_level_object_set(self):
        """Object set used when decoding the coin-ship level.

        Exposing the constant through the world record keeps the level-address
        helpers and editor code aligned on the same decoding context that the
        offset-based address helpers expect. In practice it is the decoding
        context that lets :attr:`coin_ship_level_address` round-trip between a
        staged absolute ROM address and the offset byte that
        :meth:`write_back` later stores. The getter therefore participates in
        the same data-flow path as the address helpers even though the value is
        fixed for every world: decode offsets, resolve an absolute address in
        this bank, then serialize only the offset back out.

        Returns
        -------
        int
            Constant airship object-set id reused by SMB3 for coin ships.
        """
        return AIR_SHIP_OBJECT_SET

    @property
    def coin_ship_enemy_address(self):
        """Absolute ROM address of the world coin-ship enemy data.

        This is the enemy-stream counterpart to :attr:`coin_ship_level_address`
        and is what downstream level-loading code actually consumes after the
        stored coin-ship enemy offset has been edited. The getter therefore
        bridges the staged per-world offset and the concrete ROM stream that
        loaders and serializers coordinate around.

        Returns
        -------
        int
            Absolute enemy-data address for the world's coin ship.
        """
        return BASE_OFFSET + self.coin_ship_enemy_offset

    @coin_ship_enemy_address.setter
    def coin_ship_enemy_address(self, value):
        """Store a new absolute coin-ship enemy-data address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the coin-ship enemy stream.
        """
        self.coin_ship_enemy_offset = value - BASE_OFFSET

    @property
    def generic_exit_level_address(self):
        """Absolute ROM address of the generic-exit destination layout.

        Some object sets ignore header jump destinations and route through this
        per-world fallback level instead. The property resolves that indirection
        into the concrete layout address that generic-exit tooling reads and
        writes. After ``read_values`` has decoded the per-world object set and
        offset, this getter becomes the stable layout endpoint that editors and
        serializers keep paired with :attr:`generic_exit_enemy_address`.

        Returns
        -------
        int
            Absolute layout address for the world's generic-exit destination.
        """
        return ObjectSet(self._rom, self.generic_exit_object_set).level_offset + self.generic_exit_level_offset

    @generic_exit_level_address.setter
    def generic_exit_level_address(self, value):
        """Store a new generic-exit destination layout address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the generic-exit layout.
        """
        self.generic_exit_level_offset = value - ObjectSet(self._rom, self.generic_exit_object_set).level_offset

    @property
    def generic_exit_enemy_address(self):
        """Absolute ROM address of the generic-exit destination enemy data.

        This property keeps the layout and enemy halves of the generic-exit
        destination in sync for tools that edit both together and then persist
        those offsets back into the world tables. It is the enemy-stream view
        that matches the object-set-dependent layout address returned by
        :attr:`generic_exit_level_address`, so the decode pass, editor-facing
        properties, and write-back step all treat the generic exit as one
        staged destination before it is split back into object-set and offset
        bytes. In other words, :meth:`read_values` loads the offset pair and
        object-set selector, this getter turns the stored base-offset-relative
        enemy pointer into the concrete ROM address that editor code and world
        serializers keep paired with :attr:`generic_exit_level_address`,
        callers use that absolute address while coordinating the paired
        destination, and the setter collapses later edits back into the stored
        pointer format that :meth:`write_back` writes to ROM.

        Returns
        -------
        int
            Absolute enemy-data address paired with the generic-exit layout.
        """
        return BASE_OFFSET + self.generic_exit_enemy_offset

    @generic_exit_enemy_address.setter
    def generic_exit_enemy_address(self, value):
        """Store a new generic-exit enemy-data address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the generic-exit enemy stream.
        """
        self.generic_exit_enemy_offset = value - BASE_OFFSET

    @property
    def big_q_block_level_address(self):
        """Absolute ROM address of the big question-block destination layout.

        This helper resolves the world-specific destination level that certain
        object sets use for the big question-block pipe path, turning the
        stored per-world offset into the address that loaders can follow. It
        gives callers the concrete layout endpoint that corresponds to the
        object-set and offset bytes staged on the world record and later
        serialized back into the world tables.

        Returns
        -------
        int
            Absolute layout address for the world's big question-block level.
        """
        return ObjectSet(self._rom, self.big_q_block_object_set).level_offset + self.big_q_block_level_offset

    @big_q_block_level_address.setter
    def big_q_block_level_address(self, value):
        """Store a new big question-block destination layout address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the big question-block layout.
        """
        self.big_q_block_level_offset = value - ObjectSet(self._rom, self.big_q_block_object_set).level_offset

    @property
    def big_q_block_enemy_address(self):
        """Absolute ROM address of the big question-block enemy data.

        It mirrors :attr:`big_q_block_level_address` for callers that need the
        paired enemy stream alongside the layout stream after edits to the
        world-specific big-question-block target. The property keeps the enemy
        half of that destination in the same decode/edit/write-back workflow as
        the level-layout half.

        Returns
        -------
        int
            Absolute enemy-data address for the big question-block level.
        """
        return BASE_OFFSET + self.big_q_block_enemy_offset

    @big_q_block_enemy_address.setter
    def big_q_block_enemy_address(self, value):
        """Store a new big question-block enemy-data address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the big question-block enemy stream.
        """
        self.big_q_block_enemy_offset = value - BASE_OFFSET

    @property
    def toad_warp_level_address(self):
        """Absolute ROM address of the world's Toad warp-house layout.

        The world stores only the offset to this special level. This property
        expands that offset into the concrete address that warp-house tooling
        reads or rewrites when editing the world-specific Toad reward level.
        Together with :attr:`toad_warp_object_set`, it defines the complete
        staged destination contract: :meth:`read_values` loads the offset,
        callers inspect or replace the derived absolute address, and the setter
        turns the edit back into the offset byte that :meth:`write_back`
        persists. That makes this getter the point where a world-local reward
        offset becomes the concrete ROM layout address consumed by Toad-house
        editors and level loaders before the next write-back pass serializes
        the updated destination.

        Returns
        -------
        int
            Absolute layout address for the special Toad level referenced by
            this world.
        """
        return ObjectSet(self._rom, self.toad_warp_object_set).level_offset + self.toad_warp_level_offset

    @toad_warp_level_address.setter
    def toad_warp_level_address(self, value):
        """Store a new Toad warp-house layout address.

        Parameters
        ----------
        value : int
            Absolute ROM address for the Toad warp-house layout.
        """
        self.toad_warp_level_offset = value - ObjectSet(self._rom, self.toad_warp_object_set).level_offset

    @property
    def toad_warp_object_set(self):
        """Object set used when decoding the Toad warp-house level.

        Keeping the fixed mushroom-house set behind a property lets the world
        record own the full destination contract that its address helper and
        editor consumers rely on. That keeps the Toad-house destination in the
        same property-driven workflow as the other world-specific special
        levels, even though the object set itself never varies by world.

        Returns
        -------
        int
            Fixed mushroom-house object-set id used by SMB3 for this level.
        """
        return MUSHROOM_OBJECT_SET

    @property
    def tile_data_size(self):
        """Serialized size of the world layout, including the delimiter.

        ROM writers need this value when repacking world layouts because SMB3
        terminates the tile buffer with a delimiter byte instead of storing a
        separate length field.

        Returns
        -------
        int
            Layout byte count plus the delimiter byte written after the tile
            data in ROM.
        """
        return len(self.tile_data) + 1  # the delimiter at the end

    @property
    def screen_count(self):
        """Number of 16x9 screens represented by the layout buffer.

        The property is derived from ``tile_data`` rather than stored directly
        in ROM, so editing tools and the ``screen_count`` setter both rely on
        it whenever they need to resize or validate the layout buffer. It is
        the bridge between the decoded layout bytes loaded by
        :meth:`read_values` and the repacked tile buffer that :meth:`write_back`
        later serializes.

        Returns
        -------
        int
            Screen count implied by the decoded ``tile_data`` length.
        """
        return len(self.tile_data) // WORLD_MAP_SCREEN_SIZE

    @screen_count.setter
    def screen_count(self, new_screen_count):
        """Resize the layout buffer to cover a new number of screens.

        Parameters
        ----------
        new_screen_count : int
            Desired total number of screens in the world-map layout.

        Notes
        -----
        Growing the map appends blank tiles for each new screen. Shrinking the
        map truncates the trailing screens from ``tile_data``.
        """
        diff = new_screen_count - self.screen_count

        if new_screen_count > self.screen_count:
            new_tile_data = WORLD_MAP_BLANK_TILE_ID.to_bytes(1, byteorder="big") * diff * WORLD_MAP_SCREEN_SIZE
            self.tile_data.extend(new_tile_data)

        elif new_screen_count < self.screen_count:
            self.tile_data = self.tile_data[: new_screen_count * WORLD_MAP_SCREEN_SIZE]

        assert len(self.tile_data) == self.screen_count * WORLD_MAP_SCREEN_SIZE

    @property
    def level_count(self):
        """Number of level-pointer records owned by this world.

        SMB3 does not store this count as a standalone byte. The count is
        implied by the spacing between the y-position list and x-position list,
        so higher-level code and the screen-count setters use this property
        whenever they need to rebuild or repack the structure block. That makes
        it the canonical count that ties ``level_pointers`` to the four-screen
        cumulative offset table during both decoding and write-back and the
        value the structure-block setter preserves when it repoints the lists.

        Returns
        -------
        int
            Count derived from the spacing between the y-position and x-position
            lists inside the structure block.
        """
        return self.x_pos_list_start - self.y_pos_list_start

    # TODO: the level count influences the level data list, enemy data list, object set list,
    @property
    def level_count_screen_1(self):
        """Count level pointers that belong to screen 1.

        The screen-specific counts are not stored directly. Each getter derives
        its result from the cumulative offset table that SMB3 uses to jump into
        the pointer lists for later screens. In the class workflow, the getter
        exposes the decoded screen partition, the paired setter routes edits
        through :meth:`_update_level_counts`, and the resulting staged offsets
        are what :meth:`write_back` serializes.

        Returns
        -------
        int
            Number of decoded level pointers assigned to screen 1.
        """
        return self.pos_offsets_for_screen[1] - self.pos_offsets_for_screen[0]

    @level_count_screen_1.setter
    def level_count_screen_1(self, value):
        """Adjust the screen-1 level-pointer count.

        Parameters
        ----------
        value : int
            Desired number of level pointers on screen 1.
        """
        diff = value - self.level_count_screen_1

        self._update_level_counts(1, diff)

    @property
    def level_count_screen_2(self):
        """Count level pointers that belong to screen 2.

        This value is derived from the cumulative screen-offset table and is
        mainly used when rebalancing pointer ownership across screens through
        the paired setter.

        Returns
        -------
        int
            Number of decoded level pointers assigned to screen 2.
        """
        return self.pos_offsets_for_screen[2] - self.pos_offsets_for_screen[1]

    @level_count_screen_2.setter
    def level_count_screen_2(self, value):
        """Adjust the screen-2 level-pointer count.

        Parameters
        ----------
        value : int
            Desired number of level pointers on screen 2.
        """
        diff = value - self.level_count_screen_2

        self._update_level_counts(2, diff)

    @property
    def level_count_screen_3(self):
        """Count level pointers that belong to screen 3.

        Editors use this derived count when moving level pointers between the
        later screens of a multi-screen overworld and when recalculating the
        later cumulative offsets. The value comes from the same cumulative
        offset table that :meth:`read_values` decodes from the structure block
        and that :meth:`write_back` later persists after pointer reordering, so
        it acts as a live view into the staged structure-block partitioning for
        the later screens. Screen 3 is also the last cumulative entry before
        the final remainder-based screen-4 count, so this getter is part of the
        handoff between the explicit cumulative offsets and the terminal
        derived count used during repacking. The per-screen setters and
        :meth:`_update_level_counts` use that same staged partitioning when
        callers rebalance pointers before :meth:`write_back`, so this getter is
        the concrete screen-3 view that sits between the decoded cumulative
        offsets in ``pos_offsets_for_screen`` and the later structure-block
        write-back pass. Concretely, screen 3 starts at the cumulative index
        stored for screen 2 and ends at the cumulative index stored for screen
        3, making this property the live slice boundary that later screen-count
        edits and pointer repacking preserve.

        Returns
        -------
        int
            Number of decoded level pointers assigned to screen 3.
        """
        return self.pos_offsets_for_screen[3] - self.pos_offsets_for_screen[2]

    @level_count_screen_3.setter
    def level_count_screen_3(self, value):
        """Adjust the screen-3 level-pointer count.

        Parameters
        ----------
        value : int
            Desired number of level pointers on screen 3.
        """
        diff = value - self.level_count_screen_3

        self._update_level_counts(3, diff)

    @property
    def level_count_screen_4(self):
        """Count level pointers that belong to screen 4.

        The final screen count is computed from the remaining pointer range
        after the earlier cumulative offsets have been accounted for, making it
        the terminal derived value in the four-screen count workflow.

        Returns
        -------
        int
            Number of decoded level pointers assigned to screen 4.
        """
        return self.level_count - self.pos_offsets_for_screen[3]

    @level_count_screen_4.setter
    def level_count_screen_4(self, value):
        """Adjust the screen-4 level-pointer count.

        Parameters
        ----------
        value : int
            Desired number of level pointers on screen 4.
        """
        diff = value - self.level_count_screen_4

        self._update_level_counts(4, diff)

    def _update_level_counts(self, screen: int, diff: int):
        """Shift per-screen offsets after a level-pointer count change.

        The helper is the one place where screen-local level-count edits become
        structural pointer changes. Each per-screen setter funnels through this
        method so the cumulative offset table, the x-position list start, and
        the rest of the structure-block addresses stay synchronized.

        Parameters
        ----------
        screen : int
            One-based screen number whose count changed.
        diff : int
            Signed change in the number of level pointers assigned to that
            screen.

        Notes
        -----
        ``pos_offsets_for_screen`` stores cumulative list starts, so changing
        one screen's count requires incrementing every later screen's offset.
        The method also moves the x-position list start and then reassigns
        ``structure_block_address`` to itself so the dependent structure-block
        list starts are rebuilt from the new counts.

        This helper is the synchronization point between the screen-local count
        setters and the structure-block pointers that :meth:`write_back`
        eventually persists. It first pushes the signed count delta through the
        cumulative per-screen offsets, then moves the x-position list start,
        and finally reuses the structure-block repointing logic so the
        y-position list, x-position list, enemy-offset list, and level-offset
        list all move in lockstep before the next commit.
        """
        for i in range(MAX_SCREEN_COUNT):
            if i >= screen:
                self.pos_offsets_for_screen[i] += diff

        self.x_pos_list_start += diff

        self.structure_block_address = self.structure_block_address
