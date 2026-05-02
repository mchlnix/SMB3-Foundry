"""Editable SMB3 overworld model and world-map object adaptation.

This module adapts :mod:`smb3parse` world-map records into editor-facing
objects that participate in selection, rendering, undo, and save workflows.
It is the main bridge between ROM-backed overworld data and Foundry's
:class:`~foundry.game.level.LevelLike.LevelLike` interaction model.

Notes
-----
This file mixes ROM-backed SMB3 world data with editor-facing selection and
rendering concerns. For low-level or encoded-field explanations, use Git
history, NESdev references, and SMB3 disassembly context only when the
implementation itself confirms them.

See Also
--------
foundry.game.level.Level
    In-level sibling model that shares the broader editor workflow surface.
foundry.gui.visualization.world.WorldView
    Interactive view that turns world-map gestures into undoable commands.
foundry.gui.visualization.world.WorldDrawer
    Renderer that consumes this model's objects and palette state.
"""

from typing import cast

from PySide6.QtCore import QObject, QPoint, QRect, QSize, Signal, SignalInstance

from foundry.game.File import ROM
from foundry.game.gfx import BlockCache
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.objects.world_map.airship_point import AirshipTravelPoint
from foundry.game.gfx.objects.world_map.level_pointer import LevelPointer
from foundry.game.gfx.objects.world_map.locks import Lock
from foundry.game.gfx.objects.world_map.map_tile import MapTile
from foundry.game.gfx.objects.world_map.sprite import Sprite
from foundry.game.gfx.objects.world_map.start_posiiton import StartPosition
from foundry.game.gfx.Palette import load_palette_group
from foundry.game.level.LevelLike import LevelLike
from foundry.game.ObjectSet import ObjectSet
from smb3parse.constants import MAPOBJ_EMPTY, WORLD_MAP_OBJECT_SET
from smb3parse.data_points import Position
from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.levels.world_map import WORLD_MAP_HEIGHT
from smb3parse.levels.world_map import WorldMap as _WorldMap
from smb3parse.levels.world_map import list_world_map_addresses
from smb3parse.util.rect import Point
from smb3parse.util.rom import Rom

OVERWORLD_GRAPHIC_SET = 0


class WorldSignaller(QObject):
    """Expose Qt signals emitted by an editable world map.

    :class:`WorldMap` owns one signaller so non-Qt overworld model code can
    notify views when tile, sprite, pointer, or palette state changes. It
    keeps one shared event vocabulary in front of several distinct overworld
    concerns so renderers, pointer tools, and palette-aware widgets can
    subscribe to the slice of change they actually care about.

    Attributes
    ----------
    data_changed : SignalInstance
        Emitted when editable world-map data changes.
    dimensions_changed : SignalInstance
        Emitted when loaded map dimensions change.
    jumps_changed : SignalInstance
        Emitted when level-entry pointer state changes.
    level_changed : SignalInstance
        Emitted after a different world map is loaded.
    needs_redraw : SignalInstance
        Emitted when views should repaint the map.
    palette_changed : SignalInstance
        Emitted when palette-dependent rendering data changes.

    Notes
    -----
    The signaller keeps Qt notification plumbing out of the overworld decode
    layer while still giving world views, pointer editors, and redraw code one
    stable event surface. That boundary matters because overworld tools share
    one ROM-backed model but react to different slices of change: palette
    updates, pointer edits, redraw requests, and full world swaps do not all
    imply the same downstream work.

    See Also
    --------
    WorldMap
        Owns this signal bridge and emits these notifications as overworld
        state changes.
    foundry.gui.visualization.world.WorldView
        Consumes these notifications to keep the interactive world canvas in
        sync with the active overworld model.

    Examples
    --------
    World-facing widgets usually subscribe through :class:`WorldMap` and then react
    only to the slice of overworld change they render::

        world_map = WorldMap.from_world_number(1)
        world_map.needs_redraw.connect(view.update)
        world_map.data_changed.connect(sidebar.refresh)

    A palette tool can stay narrower than a full world reload because palette
    swaps change rendering without replacing the decoded object lists::

        world_map.palette_changed.connect(palette_panel.refresh)
        world_map.level_changed.connect(world_selector.reload)

    Tile rereads and world swaps also separate data-shape changes from canvas
    sizing, which lets views avoid polling the whole model after each edit::

        world_map.jumps_changed.connect(pointer_list.refresh)
        world_map.dimensions_changed.connect(scroll_area.updateGeometry)

    That split is what keeps redraw, property panels, and world-selection
    shells decoupled even though they all observe the same ROM-backed model.
    """

    needs_redraw: SignalInstance = cast(SignalInstance, Signal())
    data_changed: SignalInstance = cast(SignalInstance, Signal())
    dimensions_changed: SignalInstance = cast(SignalInstance, Signal())
    jumps_changed: SignalInstance = cast(SignalInstance, Signal())
    level_changed: SignalInstance = cast(SignalInstance, Signal())
    palette_changed: SignalInstance = cast(SignalInstance, Signal())


class WorldMap(LevelLike):
    """Model one editable SMB3 overworld map.

    The world map combines tile data, moving sprites, level pointers, locks,
    airship paths, and the player start position. This class loads those ROM
    structures into editor objects, keeps shared rendering resources available,
    and exposes a :class:`~foundry.game.level.LevelLike.LevelLike` interface so
    the rest of Foundry can treat overworlds and normal levels uniformly where
    that makes sense.

    Parameters
    ----------
    layout_address : int
        ROM address of the level or world map layout data.

    Attributes
    ----------
    _signal_emitter : WorldSignaller
        Qt signal owner used to notify world-map views and dialogs.
    airship_travel_sets : list[list[AirshipTravelPoint]]
        Airship travel paths grouped by set.
    graphics_set : GraphicsSet
        Overworld graphics source used for map-object rendering.
    internal_world_map : _WorldMap
        Underlying :mod:`smb3parse` world-map model.
    level_pointers : list[LevelPointer]
        Selectable level-entry pointers on the map.
    locks_and_bridges : list[Lock]
        Fortress lock and bridge trigger objects.
    name : str
        Editor-facing world-map name.
    objects : list[MapTile]
        Terrain tiles in draw order.
    palette_group : object
        Overworld palette group used for tile and sprite rendering.
    size : tuple[int, int]
        Current world-map size in blocks.
    sprites : list[Sprite]
        Movable overworld sprites such as Hammer Bros. and airships.
    start_pos : StartPosition
        Mario's starting position on the overworld.
    tsa_data : bytes
        TSA data used to decode world-map blocks.

    Notes
    -----
    :class:`WorldMap` is the adapter between :mod:`smb3parse`'s specialized
    overworld records and Foundry's generic level-editor surface. It turns ROM
    records into selectable map objects while still fitting the broader
    :class:`~foundry.game.level.LevelLike.LevelLike` workflow. The long-lived
    constraint is that world editing must keep both sides coherent: generic
    editor code should be able to treat the overworld like another editable
    surface, but ROM-specific save and decode behavior still has to preserve
    the separate sprite, pointer, lock, and tile tables SMB3 uses internally.

    See Also
    --------
    WorldSignaller
        Qt signal bridge that publishes redraw, palette, and data-change events
        for this overworld model.

    Examples
    --------
    Selector and world-view code usually enter through the SMB3 world number
    and then work with the fully decoded overworld model::

        world_map = WorldMap.from_world_number(1)
        first_tile = world_map.get_all_objects()[0]
        bounds = world_map.get_rect()

    A typical world-editing round trip is "decode -> mutate editor objects ->
    serialize tile order -> save ROM-backed records"::

        world_map = WorldMap.from_world_number(1)
        original_type = world_map.tile_at(0, FIRST_VALID_ROW)
        world_map.objects[0].type = original_type + 1
        world_map.write_tiles()
        world_map.save_to_rom()

    The example shows the important data-shape boundary in this file:
    :attr:`objects` holds editable
    :class:`~foundry.game.gfx.objects.world_map.map_tile.MapTile` wrappers,
    while :meth:`write_tiles` copies their ordered ``type`` values back into
    ``data.tile_data`` before :meth:`save_to_rom` commits the world map, start
    position, and sprite tables.
    """

    def __init__(self, layout_address):
        """Load ROM-backed overworld data into editor-facing objects.

        Construction decodes terrain tiles, sprites, level pointers, locks,
        airship paths, and the start position up front so world-view tools can
        work with selectable editor objects instead of raw :mod:`smb3parse`
        records. That eager decode step is what makes the overworld fit the
        broader :class:`~foundry.game.level.LevelLike.LevelLike` editing
        workflow as soon as the instance exists. The result is a
        :class:`~foundry.game.level.LevelLike.LevelLike`-compatible world model
        that the rest of the editor can treat much like a normal level for
        selection and redraw purposes while still preserving the separate
        overworld data structures that are written back to ROM later.

        Parameters
        ----------
        layout_address : int
            ROM address of the level or world map layout data.
        """
        self.internal_world_map = _WorldMap(layout_address, ROM())

        object_set = ObjectSet.from_number(WORLD_MAP_OBJECT_SET)

        super(WorldMap, self).__init__(object_set, self.internal_world_map.layout_address)

        self.name = f"World {self.data.index + 1} - Overworld"
        self._signal_emitter = WorldSignaller()

        self.graphics_set = GraphicsSet.from_number(OVERWORLD_GRAPHIC_SET)
        self.palette_group = load_palette_group(WORLD_MAP_OBJECT_SET, self.data.palette_index)

        self.tsa_data = ROM.get_tsa_data(self.object_set.number)

        self.size = 0, 0

        self.objects: list[MapTile] = []

        self._load_objects()
        self._load_sprites()
        self._load_level_pointers()
        self._load_starting_position()
        self._load_airship_points()
        self._load_locks_and_bridges()

        self._calc_size()

    @property
    def data(self):
        """Expose the underlying :mod:`smb3parse` world-map record.

        Callers use this when they need the ROM-backed structure that owns tile
        bytes, sprite tables, palette indexes, and other overworld metadata
        beyond the editor adapters created by :class:`WorldMap`. Save paths and
        specialized overworld tools cross this boundary when they need the
        underlying :mod:`smb3parse` record rather than a Foundry wrapper
        object.

        Returns
        -------
        object
            Parsed overworld data owned by :attr:`internal_world_map`.
        """
        return self.internal_world_map.data

    @property
    def width(self):
        """Report the decoded overworld width in tiles.

        Width is derived from decoded tile count because the editor keeps a
        flat tile list and adapts it into rows at render and hit-test time.
        ``_calc_size``, ``q_size``, world-view geometry, and hit testing all
        reuse this decoded width instead of recomputing map geometry from ROM
        data independently. Construction, tile reloads, and canvas sizing all
        read this property when they turn the tile stream back into map bounds.

        Returns
        -------
        int
            Number of tile columns in the loaded map.
        """
        return len(self.objects) // WORLD_MAP_HEIGHT

    @property
    def height(self):
        """Report the fixed overworld height in tiles.

        SMB3 overworld maps use a fixed tile height, so this property anchors
        the rest of the editor's size, rectangle, scroll, and hit-test
        calculations regardless of how wide the loaded world is. ``_calc_size``
        and ``get_rect`` rely on this fixed height when they rebuild cached
        geometry after decode or tile reloads.

        Returns
        -------
        int
            Number of tile rows in the loaded map.
        """
        return WORLD_MAP_HEIGHT

    @staticmethod
    def from_world_number(world_index: int):
        """Load an overworld from SMB3's world-address table.

        The helper translates a user-facing SMB3 world number into the ROM
        layout-table entry that owns that overworld and then runs the full
        ``WorldMap`` decode pipeline for that address. By the time it returns,
        the caller has a world model whose tiles, sprites, level pointers,
        locks, palette state, and signals are already hydrated for editor use.
        Selector dialogs and world-view bootstrapping rely on that lifecycle
        guarantee so they can move directly from "the user chose World 3" to an
        interactive world surface without a second initialization phase. In
        other words, this is the handoff from user-visible world identity to a
        fully decoded ``LevelLike`` model ready for rendering, hit testing,
        selection, and later save-back to ROM.

        Parameters
        ----------
        world_index : int
            Index of the world.

        Returns
        -------
        WorldMap
            Loaded world map for that SMB3 world.

        Raises
        ------
        ValueError
            If ``world_index`` falls outside SMB3's supported world range.
        """
        if not 1 <= world_index <= 9:
            raise ValueError(f"World Number of '{world_index} not allowed. Keep it between 1 and 9.")

        return WorldMap(list_world_map_addresses(ROM())[world_index - 1])

    def _load_objects(self):
        """Decode world-map terrain tiles into ``MapTile`` objects."""
        self.objects.clear()

        for index, tile in enumerate(self.data.tile_data):
            pos = Position.from_tile_data_index(index)

            block = BlockCache.block(tile, WORLD_MAP_OBJECT_SET, self.palette_group.index, self.graphics_set.number)

            self.objects.append(MapTile(block, pos))

        assert len(self.objects) % WORLD_MAP_HEIGHT == 0

        self._calc_size()

    def _load_sprites(self):
        """Decode overworld sprite records into selectable ``Sprite`` objects."""
        self.sprites: list[Sprite] = []

        for sprite_data in self.internal_world_map.gen_sprites():
            self.sprites.append(Sprite(sprite_data))

    def _load_level_pointers(self):
        """Decode level-entry pointers into selectable editor objects."""
        self.level_pointers: list[LevelPointer] = []

        for level_pointer_data in self.internal_world_map.level_pointers:
            self.level_pointers.append(LevelPointer(level_pointer_data))

    def _load_starting_position(self):
        """Wrap the ROM-backed start position in an editor object."""
        self.start_pos = StartPosition(self.internal_world_map.start_pos)

    def _load_airship_points(self):
        """Decode airship travel sets into selectable path points."""
        self.airship_travel_sets: list[list[AirshipTravelPoint]] = []

        for set_no, airship_travel_set in enumerate(self.data.airship_travel_sets):
            self.airship_travel_sets.append(
                [AirshipTravelPoint(pos, set_no, index) for index, pos in enumerate(airship_travel_set)]
            )

    def _load_locks_and_bridges(self):
        """Decode fortress locks and bridge triggers into editor objects."""
        self.locks_and_bridges: list[Lock] = []

        for fortress_fx in self.data.fortress_fx:
            self.locks_and_bridges.append(Lock(fortress_fx))

    def _calc_size(self):
        """Recompute cached map dimensions and emit resize notifications."""
        old_size = self.size

        self.size = self.width, self.height

        if self.size != old_size:
            self.dimensions_changed.emit()

    def move_level_pointers(self, source_index: int, target_index: int):
        """Reorder level pointers and rewrite their serialized indexes.

        World-map pointer order matters because the backing data points store
        their own indexes. After reordering the editor-facing list, this helper
        rewrites every pointer's index so later save operations preserve the new
        ordering in ROM.

        Parameters
        ----------
        source_index : int
            Index of the source.
        target_index : int
            Index of the target.
        """
        if source_index == target_index:
            return

        moved_level_pointer = self.level_pointers.pop(source_index)
        self.level_pointers.insert(target_index, moved_level_pointer)

        for index, level_pointer in enumerate(self.level_pointers):
            level_pointer.data.change_index(index)

    def move_sprites(self, source_index: int, target_index: int):
        """Reorder sprites and rewrite their serialized indexes.

        Like level pointers, overworld sprites carry index-based identities in
        their backing records. Reindexing keeps the editor list and ROM write
        order aligned after drag-reordering.

        Parameters
        ----------
        source_index : int
            Index of the source.
        target_index : int
            Index of the target.
        """
        if source_index == target_index:
            return

        moved_sprite = self.sprites.pop(source_index)
        self.sprites.insert(target_index, moved_sprite)

        for index, sprite in enumerate(self.sprites):
            sprite.data.change_index(index)

    @property
    def q_size(self):
        """Compute the Qt canvas size for the decoded map.

        Views use this cached conversion from tile dimensions to pixels for
        scroll areas, canvas sizing, and repaint geometry.

        Returns
        -------
        QSize
            Pixel dimensions derived from ``size`` and tile side length.
        """
        return QSize(*self.size) * Block.SIDE_LENGTH

    @property
    def needs_redraw(self):
        """Expose the signal emitted when world-map views should repaint.

        Canvas widgets use this as the redraw boundary for tile edits, sprite
        edits, and palette-sensitive changes without assuming every change also
        alters map dimensions or replaces the loaded world.

        Returns
        -------
        SignalInstance
            Redraw signal from ``_signal_emitter``.
        """
        return self._signal_emitter.needs_redraw

    @property
    def dimensions_changed(self):
        """Expose the signal emitted when decoded map dimensions change.

        Scroll areas and view sizing listen to this after tile reloads or
        world-map swaps so geometry-dependent widgets can resize together.

        Returns
        -------
        SignalInstance
            Dimensions-changed signal from ``_signal_emitter``.
        """
        return self._signal_emitter.dimensions_changed

    @property
    def data_changed(self):
        """Expose the signal emitted when editable overworld data changes.

        Tile editors, save-state widgets, and world-map views use this to
        refresh after in-place map edits without treating them like a full
        overworld reload.

        Returns
        -------
        SignalInstance
            Data-changed signal from ``_signal_emitter``.
        """
        return self._signal_emitter.data_changed

    @property
    def jumps_changed(self):
        """Expose the signal emitted when level-entry pointer data changes.

        Level-pointer lists and related overlays use this narrower channel so
        they can refresh pointer state without rebuilding every world-map pane.

        Returns
        -------
        SignalInstance
            Jump-change signal from ``_signal_emitter``.
        """
        return self._signal_emitter.jumps_changed

    @property
    def level_changed(self):
        """Expose the signal emitted after a different overworld is loaded.

        Editor shells use this when a new world replaces the active one and the
        rest of the UI needs to rebuild around different tiles, pointers,
        sprites, and palette state.

        Returns
        -------
        SignalInstance
            Level-change signal from ``_signal_emitter``.
        """
        return self._signal_emitter.level_changed

    @property
    def palette_changed(self):
        """Expose the signal emitted when palette-dependent map rendering changes.

        Palette viewers and redraw code use this to update map blocks whose
        decoded tiles stay the same while their rendered colors change. It is
        the narrower notification path for "render the same overworld data with
        different palette state" instead of a broader world reload or tile-data
        mutation.

        Returns
        -------
        SignalInstance
            Palette-change signal from ``_signal_emitter``.
        """
        return self._signal_emitter.palette_changed

    def draw(self, dc, zoom, transparency=None, show_expansion=None):
        """Draw the terrain-tile layer of the overworld.

        ``WorldMap`` satisfies the shared ``LevelLike`` API, but only the tile
        layer is rendered here. Sprites, pointers, locks, and selection
        overlays stay in the world-view rendering stack, so this method is the
        terrain stage of the wider world render pipeline: it consumes the
        already decoded tile list, turns each tile into painter commands at the
        requested zoom, and leaves later overlay stages to add interaction
        affordances on top. That lifecycle matters because redraw requests and
        palette changes reuse the same stable terrain pass rather than asking
        every world-aware tool to redraw from raw ROM bytes. In practice, this
        is the model-side handoff from decoded world data to the base canvas
        image that later view layers compose over.

        Parameters
        ----------
        dc : QPainter
            Painter used to render the world map.
        zoom : int
            Tile zoom factor used for the draw pass.
        transparency : object, optional
            Unused compatibility argument for the shared level-like draw API.
        show_expansion : object, optional
            Unused compatibility argument for the shared level-like draw API.
        """
        for obj in self.objects:
            obj.draw(dc, Block.SIDE_LENGTH * zoom, transparency)

    def index_of(self, obj):
        """Map a terrain tile back to its serialized tile index.

        This lookup maps a ``MapTile`` back into the serialized terrain order
        that selection, painting, and save logic treat as the primary editable
        world-map surface even though sprites and pointers are stored
        elsewhere.

        Parameters
        ----------
        obj : MapTile
            Tile object to locate.

        Returns
        -------
        int
            Index of the tile in ``objects``.
        """
        return self.objects.index(obj)

    def get_all_objects(self):
        """Expose the terrain tile stream used as the primary selection surface.

        ``WorldMap`` treats tiles as the shared selection surface for the
        ``LevelLike`` interface even though sprites, pointers, and locks live
        in separate editor lists. Returning tiles here preserves the contract
        that generic selection and marquee tools can ask any ``LevelLike`` for
        its primary editable object stream.

        Returns
        -------
        list[MapTile]
            World-map tiles backing the terrain layer.
        """
        return self.objects

    def object_at(self, x, y):
        """Look up the topmost tile under the supplied coordinate.

        Hit testing walks the tile list in reverse so selection matches the
        same topmost-object rule used elsewhere in Foundry.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.

        Returns
        -------
        MapTile | None
            Topmost tile at that map coordinate, if one exists.
        """
        point = Point(x, y)

        for obj in reversed(self.objects):
            if obj.get_rect().point_in(*point):
                return obj

        return None

    def write_tiles(self):
        """Copy the edited terrain order into the ROM-backed tile table.

        Tile painting mutates ``MapTile`` objects in memory, while SMB3 stores
        the terrain layer as raw tile bytes. This method is the conversion step
        between those two representations, rebuilding the serialized tile stream
        so later persistence writes commit the edited terrain layout.
        """
        world_data = self.data
        old_tile_data = bytearray([obj.type for obj in sorted(self.objects)])

        if len(world_data.tile_data) < len(old_tile_data):
            world_data.tile_data = old_tile_data[: len(world_data.tile_data)]
        else:
            world_data.tile_data[: len(old_tile_data)] = old_tile_data

    def reread_tiles(self):
        """Rebuild editor tile objects from the ROM-backed world data.

        This is the refresh path after world data was changed externally or
        reloaded from ROM. It throws away the existing tile wrappers, decodes
        fresh ``MapTile`` objects, and notifies listeners that the editor's
        terrain surface changed under them.
        """
        self._load_objects()

        self.data_changed.emit()

    def level_pointer_at(self, x: int, y: int) -> LevelPointer | None:
        """Look up the level-entry pointer at a world-map coordinate.

        Pointer editing uses this helper to switch from tile-space gestures to
        the separate pointer objects that control where world-map level nodes
        load the player.

        Parameters
        ----------
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.

        Returns
        -------
        LevelPointer | None
            Level pointer at the supplied world-map coordinate, if one exists.
        """
        pos = Position.from_xy(x, y)

        for level_pointer in self.level_pointers:
            if level_pointer.data.is_at(pos):
                return level_pointer
        else:
            return None

    def level_name_at_position(self, x: int, y: int) -> str:
        """Look up the stock level name assigned to a map coordinate.

        Tooltips and selector UI use the underlying ``smb3parse`` lookup here
        rather than rebuilding the naming rules in Foundry.

        Parameters
        ----------
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.

        Returns
        -------
        str
            Level name assigned to the supplied world-map position.
        """
        pos = Position.from_xy(x, y)

        return self.internal_world_map.level_name_for_position(pos)

    def sprite_at(self, x, y) -> Sprite | None:
        """Look up the topmost non-empty overworld sprite at a coordinate.

        Sprite hit testing stays separate from terrain hit testing because
        world sprites live in a different ROM table even though they visually
        sit on top of the tile layer.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.

        Returns
        -------
        Sprite | None
            Sprite at the supplied world-map coordinate, if one exists.
        """
        pos = Position.from_xy(x, y)

        for sprite in reversed(self.sprites):
            if sprite.data.is_at(pos) and sprite.type != MAPOBJ_EMPTY:
                return sprite
        else:
            return None

    def airship_point_at(self, x, y, airship_travel_set_visibility=0):
        """Look up the visible airship path point at a world-map coordinate.

        Visibility is filtered through the active travel-set bitmask so the
        editor only hit-tests path points the user asked to see. That keeps the
        gesture path aligned with the overlays and toggles the world view is
        showing.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.
        airship_travel_set_visibility : int, optional
            Bitmask of visible airship travel sets.

        Returns
        -------
        AirshipTravelPoint | None
            Visible airship point at the supplied coordinate, if one exists.
        """
        pos = Position.from_xy(x, y)

        for index, airship_travel_set in reversed(list(enumerate(self.airship_travel_sets))):
            if airship_travel_set_visibility & 2**index != 2**index:
                continue

            for airship_point in reversed(airship_travel_set):
                if airship_point.pos == pos:
                    return airship_point

        return None

    def tile_at(self, x, y):
        """Look up the terrain tile id stored at a map coordinate.

        Tile-painting and fill tools use this to compare the ROM-backed tile
        value rather than a rendered block image.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.

        Returns
        -------
        int
            Tile type at the supplied coordinate.
        """
        pos = Position.from_xy(x, y)

        return self.objects[pos.tile_data_index].type

    def locks_at(self, x, y):
        """Look up the lock or bridge trigger at a map coordinate.

        Fortress effects and bridge toggles are stored separately from terrain
        tiles, so they need their own hit-test path during overworld editing.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.

        Returns
        -------
        Lock | None
            Lock object at the supplied coordinate, if one exists.
        """
        pos = Position.from_xy(x, y)

        for lock in reversed(self.locks_and_bridges):
            if lock.data.is_at(pos):
                return lock
        else:
            return None

    @staticmethod
    def pipe_at(_, __):
        """State that overworld editing exposes no pipe object through ``LevelLike``.

        World maps do not expose editable pipe objects through this interface,
        so the method always returns ``None`` to satisfy the shared ``LevelLike``
        API without inventing a fake pipe layer for overworld editing. The
        helper exists only to keep generic editor code from needing a separate
        overworld-specific capability check.

        Parameters
        ----------
        _ : int
            Horizontal tile coordinate.
        __ : int
            Vertical tile coordinate.

        Returns
        -------
        None
            Always ``None`` for world maps.
        """
        return None

    def get_selected_tiles(self) -> list[MapTile]:
        """Collect the terrain tiles marked as selected.

        Tile-selection tools treat only the terrain layer as marquee-selectable;
        sprites, pointers, and locks use their own specialized selection logic.

        Returns
        -------
        list[MapTile]
            Selected terrain tiles in draw order.
        """
        selected_objs = [obj for obj in self.objects if obj.selected]

        return selected_objs

    # TODO check if better in parent class
    def get_rect(self, block_length: int = 1):
        """Translate world-map bounds into a scaled rectangle.

        Views and selection helpers use this as the geometry bridge between
        tile-space map size and Qt rectangle math. Scroll sizing, tile hit
        testing, marquee bounds, and world-view drawing all derive the same
        panel bounds from this rectangle instead of each subsystem recomputing
        map geometry independently. The returned rectangle is therefore the
        shared canvas boundary for painting, hit testing, and scroll-area
        sizing.

        Parameters
        ----------
        block_length : int, optional
            Rendered block size in pixels.

        Returns
        -------
        QRect
            Rectangle spanning the full map at that scale.
        """
        width, height = self.size

        return QRect(QPoint(0, 0), QSize(width, height) * block_length)

    def point_in(self, x, y):
        """Check whether a coordinate lies inside editable world bounds.

        The overwrite subtracts SMB3's reserved top rows before delegating to
        the shared ``LevelLike`` bounds logic, so callers can work in the same
        coordinate space used by world-map editing tools.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.

        Returns
        -------
        bool
            ``True`` when the coordinate is inside the loaded map.
        """
        y -= FIRST_VALID_ROW
        return super(WorldMap, self).point_in(x, y)

    @property
    def fully_loaded(self):
        """Indicate that world-map construction finished successfully.

        Overworlds decode eagerly during construction, so a ``WorldMap``
        instance is either ready for editing or construction would already have
        failed. Callers use this to align with the broader ``LevelLike``
        contract even though overworld loading does not have the staged
        partially-loaded state that some other editor surfaces may expose.

        Returns
        -------
        bool
            Always ``True`` after construction succeeds.
        """
        return True

    def save_to_rom(self, rom: Rom | None = None):
        """Write edited world-map state back to ROM.

        Saving first serializes the edited terrain ordering back into the
        underlying world-map tile table, then commits start-position and other
        ROM-backed overworld records through the parsed ``smb3parse`` model.
        Sprite records are rewritten afterward so their calculated addresses and
        serialized order stay aligned with the editor state that tools have been
        mutating in memory. This makes the method the final persistence
        boundary for overworld editing: decoded editor objects are folded back
        into ROM-facing records here and only here. Tile edits, sprite moves,
        and start-position changes remain editor-side mutations until this call
        turns them back into authoritative ROM data. Once it returns, later ROM
        readers and future editor sessions see the same overworld state the
        current session was displaying. Maintainers should keep that
        persistence boundary centralized here so world-edit tools do not start
        writing partial ROM updates through scattered helper paths.

        Parameters
        ----------
        rom : Rom | None, optional
            Alternate ROM target. Defaults to the active global ROM.

        Examples
        --------
        World-editing commands usually mutate the active model first and then
        persist the whole overworld back to the active ROM::

            world_map = WorldMap.from_world_number(1)
            world_map.write_tiles()
            world_map.save_to_rom()
        """
        self.write_tiles()

        self.data.map_start_y = self.start_pos.pos.y << 4

        self.data.write_back(rom)

        # sprites
        for sprite in self.sprites:
            sprite.data.calculate_addresses()
            sprite.data.write_back(rom)
