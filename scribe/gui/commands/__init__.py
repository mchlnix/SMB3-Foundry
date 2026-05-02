"""Undo commands for Scribe world editing workflows.

This module groups the :class:`~PySide6.QtGui.QUndoCommand` implementations
that mutate parsed overworld state inside Scribe. The commands stage values
before an edit, apply the mutation during ``redo()``, and restore the previous
state during ``undo()`` so the editor, ROM-backed data points, and Foundry's
additional-data cache stay in sync.

The commands fall into a few families:

- tile and map-object movement on a :class:`foundry.game.level.WorldMap.WorldMap`
- direct edits to :mod:`smb3parse.data_points` records such as
  :class:`~smb3parse.data_points.LevelPointerData`,
  :class:`~smb3parse.data_points.SpriteData`, and
  :class:`~smb3parse.data_points.WorldMapData`
- save helpers that flush staged world edits back to the ROM-facing records

See Also
--------
scribe.gui.world_overview
    Hosts the world-editing surfaces that enqueue these commands.
scribe.gui.edit_world_info
    Builds dialog-driven command payloads for world metadata edits.
foundry.game.level.WorldMap
    Provides the mutable world model that these commands update.
"""

from PySide6.QtGui import QUndoCommand

from foundry.game.File import ROM
from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.gfx.objects.world_map.level_pointer import LevelPointer
from foundry.game.gfx.objects.world_map.locks import Lock
from foundry.game.gfx.objects.world_map.map_object import MapObject
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.localization import tr, tr_data_name
from smb3parse.constants import (
    MAPITEM_NAMES,
    MAPOBJ_NAMES,
    MUSIC_THEMES,
    OBJECT_SET_NAMES,
    SPRITE_COUNT,
    TILE_NAMES,
)
from smb3parse.data_points import LevelPointerData, Position, SpriteData, WorldMapData
from smb3parse.levels import FIRST_VALID_ROW, NO_MAP_SCROLLING, WORLD_MAP_BLANK_TILE_ID

TR_CONTEXT = "ScribeCommands"


class DirtyAdditionalDataMixin(object):
    """Mark Foundry's cached additional data dirty around undo stack actions.

    This mixin is used by commands whose edits change ROM-backed structures that
    Foundry reparses lazily. It captures the pre-command refresh state, marks
    the cache dirty before delegating to ``redo()`` or ``undo()``, and then
    lets the command-specific implementation perform the actual mutation.

    Parameters
    ----------
    *args
        Positional arguments forwarded to the wrapped undo command.
    **kwargs
        Keyword arguments forwarded to the wrapped undo command.

    Attributes
    ----------
    _dirty_before : bool
        Value of ``ROM.additional_data.needs_refresh`` captured before the
        concrete command finishes initialization.
    """

    def __init__(self, *args, **kwargs):
        """Capture the cache-dirty state before command setup continues.

        The mixin runs before the concrete command finishes staging its own
        fields so later undo-stack operations can compare against the original
        cache-refresh state if needed.

        Parameters
        ----------
        *args
            Positional arguments forwarded to the next ``__init__`` in the MRO.
        **kwargs
            Keyword arguments forwarded to the next ``__init__`` in the MRO.
        """
        self._dirty_before = ROM.additional_data.needs_refresh

        super().__init__(*args, **kwargs)

    def undo(self):
        """Mark additional data dirty before undoing the wrapped command.

        Notes
        -----
        Redoing one of these commands can trigger ROM hot swapping in Foundry.
        Undoing afterward is therefore a new parse-sensitive change, so the
        cache must be flagged for refresh again before the parent command runs.
        The mixin does not perform command-specific mutation; it establishes
        the reparsing boundary and then delegates to the next undo method in
        the MRO so the concrete command can restore its own staged payload.
        """
        # We introduced a ROM hotswapping feature in Foundry, that means after executing the redo of this command, the
        # ROM in fonudry might be reloaded.
        # Undoing this command would now be a new change, necessatating a reparsing of the levels again, so we have to
        # "dirty" the data, so Foundry can realize this.
        ROM.additional_data.needs_refresh = True

        super().undo()  # type: ignore

    def redo(self):
        """Mark additional data dirty before reapplying the wrapped command.

        The redo side mirrors :meth:`undo`: it flags Foundry's additional-data
        cache before the concrete command mutates ROM-backed structures. That
        keeps hot-reload and lazy reparsing behavior aligned with the command
        history without making this mixin own any world-edit payload.
        """
        ROM.additional_data.needs_refresh = True

        super().redo()  # type: ignore


class MoveTile(QUndoCommand):
    """Move one world-map tile from a source position to a destination tile.

    The command snapshots the tile type already present at the destination so
    undo can restore both sides of the move. It is used for drag-style tile
    rearrangement inside the world overview, where a tile edit must preserve
    both the dragged tile identity and the displaced destination tile.

    Parameters
    ----------
    world : WorldMap
        World model that owns the editable tile objects.
    start : Position
        Tile position that supplies the moved tile.
    tile_after : int
        Tile type to place at the destination during ``redo()``.
    end : Position
        Destination tile position.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    start : Position
        Source tile position captured when the command is created.
    end : Position
        Destination tile position captured when the command is created.
    tile_after : int
        Tile type moved into the destination slot.
    tile_before : int
        Tile type originally occupying the destination slot.
    """

    def __init__(
        self,
        world: WorldMap,
        start: Position,
        tile_after: int,
        end: Position,
        parent=None,
    ):
        """Stage a tile move before the undo stack replays it.

        The command freezes the source position, destination position, moved
        tile type, and displaced destination tile before any world objects are
        mutated. That lets ``redo()`` behave like the initial drag outcome
        while ``undo()`` can reconstruct the exact pre-drag tile layout.

        Parameters
        ----------
        world
            World view-model that owns the tile objects being edited.
        start
            Source position whose tile will be removed during ``redo()``.
        tile_after
            Tile type that should appear at ``end`` after the move.
        end
            Destination position that receives ``tile_after``.
        parent
            Optional Qt undo-command parent.
        """
        super(MoveTile, self).__init__(parent)

        self.world = world

        self.start = start
        self.tile_after = tile_after

        self.end = end

        if self.world.point_in(*end.xy):
            self.tile_before = self.world.objects[self.end.tile_data_index].type
        else:
            self.tile_before = WORLD_MAP_BLANK_TILE_ID

        self.setText(
            tr(TR_CONTEXT, "move_tile_tile_name", "Move Tile '{tile_name}'").format(
                tile_name=tr_data_name("Tile", TILE_NAMES[tile_after])
            )
        )

    def undo(self):
        """Restore the source tile and destination tile selection state.

        Undo reconstructs the exact pre-drag arrangement from constructor
        snapshots. Selection flags are restored alongside tile ids so the
        world view can repaint focus consistently after the undo-stack cursor
        moves backward.
        """
        if 0 <= self.start.tile_data_index < len(self.world.objects):
            source_obj = self.world.objects[self.start.tile_data_index]
            source_obj.change_type(self.tile_after)
            source_obj.selected = True

        if 0 <= self.end.tile_data_index < len(self.world.objects):
            target_obj = self.world.objects[self.end.tile_data_index]
            target_obj.change_type(self.tile_before)
            target_obj.selected = False

    def redo(self):
        """Blank the source tile and place the moved tile at the destination.

        Redo applies the staged drag result without recalculating source or
        destination identity. The command updates rendered tile objects only;
        later save paths serialize the world model back to ROM data.
        """
        if 0 <= self.start.tile_data_index < len(self.world.objects):
            source_obj = self.world.objects[self.start.tile_data_index]
            source_obj.change_type(WORLD_MAP_BLANK_TILE_ID)
            source_obj.selected = False

        if 0 <= self.end.tile_data_index < len(self.world.objects):
            target_obj = self.world.objects[self.end.tile_data_index]
            target_obj.change_type(self.tile_after)
            target_obj.selected = True


class MoveMapObject(DirtyAdditionalDataMixin, QUndoCommand):
    """Move a lock, bridge, or level pointer to a new world-map position.

    Unlike :class:`MoveTile`, this command mutates higher-level map objects and
    must also keep Foundry's additional-data cache marked dirty so dependent
    parsing can be refreshed after the command runs. It is the replay boundary
    for drag-style movement of parsed world objects, including grouped locks
    whose shared fortress state must continue to move together.

    Parameters
    ----------
    world : WorldMap
        World model that owns the selected object and any linked locks.
    map_object : MapObject
        Selected world object to move.
    end : Position
        Destination position for the object.
    start : Position, optional
        Explicit source position to restore during ``undo()``.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the move.
    map_object : MapObject
        Selected world object whose position is being updated.
    start : tuple[int, int]
        Source coordinates replayed during ``undo()``.
    end : tuple[int, int]
        Destination coordinates replayed during ``redo()``.
    """

    def __init__(
        self,
        world: WorldMap,
        map_object: MapObject,
        end: Position,
        start: Position | None = None,
        parent=None,
    ):
        """Stage a map-object move for later undo-stack replay.

        The constructor freezes both endpoints before any object is moved
        because selection and hover state in the world view can continue
        changing after the drag completes. Replaying the stored coordinates lets
        ``undo()`` and ``redo()`` move the same parsed object back through the
        same path while the mixin keeps later reparses dirty.

        Parameters
        ----------
        world
            World model that owns the map object and related lock set.
        map_object
            Selected map object to move.
        end
            Destination position for the move.
        start
            Optional explicit origin position. When omitted, the command uses
            the map object's position at command-construction time.
        parent
            Optional Qt undo-command parent.
        """
        super(MoveMapObject, self).__init__(parent)

        self.world = world

        self.map_object = map_object

        if start is None:
            self.start: tuple[int, int] = map_object.get_position()
        else:
            self.start = start.xy

        self.end = end.xy

        self.setText(
            tr(TR_CONTEXT, "move_object_name", "Move {object_name}").format(
                object_name=tr_data_name("MapObject", self.map_object.name)
            )
        )

    def undo(self):
        """Move the object back to its staged origin and refresh parse state."""
        self._move_map_object(self.start)

        super().undo()

    def redo(self):
        """Move the object to the staged destination and refresh parse state."""
        self._move_map_object(self.end)

        super().redo()

    def _move_map_object(self, new_pos: tuple[int, int]):
        """Apply one position update to the selected map object.

        Parameters
        ----------
        new_pos
            World-map coordinates that should become the object's new position.

        Notes
        -----
        Lock objects are grouped by index. When one lock moves, every lock or
        bridge sharing that index must mirror the new position so the fortress
        effect remains coherent.
        """
        self.map_object.set_position(*new_pos)

        if isinstance(self.map_object, Lock):
            for lock in self.world.locks_and_bridges:
                if lock.data.index == self.map_object.data.index:
                    lock.set_position(*new_pos)

        self.world.data_changed.emit()


class PutTile(MoveTile):
    """Place a tile by reusing :class:`MoveTile` with an off-map source.

    Scribe uses this command for paint-style edits where a chosen block should
    overwrite one tile slot immediately. Construction binds the target slot and
    the chosen tile type, ``redo()`` writes that tile into the world grid, and
    ``undo()`` restores the tile that previously occupied the slot by reusing
    :class:`MoveTile`'s destination snapshot.

    Notes
    -----
    The command models insertion as a move from an invalid source position.
    That keeps placement and movement on the same undo path even though the
    implementation detail is slightly awkward, and it means tile insertion
    still benefits from the destination snapshotting logic in
    :class:`MoveTile`.

    Parameters
    ----------
    world : WorldMap
        World model that owns the target tile grid.
    pos : Position
        Destination tile position to overwrite.
    tile_index : int
        Tile type inserted at ``pos``.
    parent : QUndoCommand, optional
        Optional Qt parent command.
    """

    def __init__(self, world: WorldMap, pos: Position, tile_index: int, parent=None):
        """Stage placement of a new tile at an existing map position.

        Tile painting originates as a tool gesture, not as a drag from another
        map tile, but the undo stack still needs the same destination
        snapshot-and-replay behavior that ordinary tile moves use. The
        constructor therefore translates one paint gesture into the
        :class:`MoveTile` workflow by fabricating an off-map source position,
        storing the chosen tile type, and binding the destination slot that
        ``redo()`` will overwrite. That staging step is what lets ``redo()``
        apply a paint-style overwrite while ``undo()`` restores the exact tile
        that occupied the slot before the gesture happened.

        Parameters
        ----------
        world
            World model that owns the target tile grid.
        pos
            Destination tile position to overwrite.
        tile_index
            Tile type to place at ``pos``.
        parent
            Optional Qt undo-command parent.
        """
        super(PutTile, self).__init__(
            world,
            start=Position.from_xy(-1, -1),
            tile_after=tile_index,
            end=pos,
            parent=parent,
        )

    def redo(self):
        """Apply the placement and clear any previous tile selection state."""
        super(PutTile, self).redo()

        for obj in self.world.objects:
            obj.selected = False


class WorldTickPerFrame(QUndoCommand):
    """Change the animation cadence for one overworld's animated tiles.

    The world-info editor exposes animation speed as a standalone world setting
    even though the parsed data stores one timing field. This command snapshots
    the old cadence during construction, writes the new cadence during
    ``redo()``, and restores the old cadence during ``undo()`` while emitting
    the repaint signal that keeps animated-tile previews in sync with the
    parsed value. Construction snapshots the old cadence and stores the new
    cadence so the undo stack can replay one complete timing change through the
    parsed world data and the preview repaint signal.

    Parameters
    ----------
    world : WorldMap
        World model whose animation settings should change.
    new_tick_count : int
        Number of ticks between animation frames, or ``0`` to disable them.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    old_count : int
        Animation cadence restored during ``undo()``.
    new_count : int
        Animation cadence applied during ``redo()``.
    """

    def __init__(self, world: WorldMap, new_tick_count: int):
        """Stage a new frame-tick count for undoable replay.

        The command snapshots the prior cadence because the editor updates the
        world preview immediately after the setting changes, and ``undo()`` must
        restore both the stored value and the rendered animation behavior.

        Parameters
        ----------
        world
            World model whose animation timing should change.
        new_tick_count
            Number of ticks between animated tile frames. ``0`` disables the
            animation path.
        """
        super(WorldTickPerFrame, self).__init__()

        self.world = world
        self.old_count = world.data.frame_tick_count
        self.new_count = new_tick_count

        if self.new_count == 0:
            self.setText(tr(TR_CONTEXT, "deactivate_map_tile_animation", "Deactivate Map Tile Animation"))
        else:
            self.setText(
                tr(
                    TR_CONTEXT, "command.set_tile_animation_ticks", "Set Ticks per Tile Animation Frame to {tick_count}"
                ).format(tick_count=self.new_count)
            )

    def undo(self):
        """Restore the previous animation cadence and repaint palette users."""
        self.world.data.frame_tick_count = self.old_count

        self.world.palette_changed.emit()

    def redo(self):
        """Apply the staged animation cadence and repaint palette users."""
        self.world.data.frame_tick_count = self.new_count

        self.world.palette_changed.emit()


class WorldPaletteIndex(QUndoCommand):
    """Change the palette group used for one overworld.

    Palette selection is edited as a world-level presentation setting rather
    than as a raw parsed byte. The command keeps the parsed palette index and
    the world-view repaint on one replay boundary, with the undo stack swapping
    between two complete palette states.

    Parameters
    ----------
    world : WorldMap
        World model whose palette selection should change.
    new_index : int
        Palette index to write into the world data.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    old_index : int
        Palette index restored during ``undo()``.
    new_index : int
        Palette index applied during ``redo()``.
    """

    def __init__(self, world: WorldMap, new_index: int):
        """Stage a palette-index change for undo replay.

        The command stores both palette choices so the world view can repaint
        immediately in either direction of the undo stack without rereading the
        world data from disk.

        Parameters
        ----------
        world
            World model whose palette selection should change.
        new_index
            New palette index stored in :class:`WorldMapData`.
        """
        super(WorldPaletteIndex, self).__init__()

        self.world = world
        self.old_index = world.data.palette_index
        self.new_index = new_index

        self.setText(
            tr(
                TR_CONTEXT, "setting_palette_index_to_palette_index_x", "Setting Palette Index to {palette_index:#x}"
            ).format(palette_index=new_index)
        )

    def undo(self):
        """Restore the previous world palette index and repaint the view."""
        self.world.data.palette_index = self.old_index

        self.world.palette_changed.emit()

    def redo(self):
        """Apply the staged world palette index and repaint the view."""
        self.world.data.palette_index = self.new_index

        self.world.palette_changed.emit()


class WorldMusicIndex(QUndoCommand):
    """Change the music theme used when entering and traversing a world.

    Scribe presents world music as one semantic choice even though the parsed
    world data stores both arrival and steady-state fields. This command keeps
    those paired fields synchronized through undo and redo so the world never
    lands in a half-updated music state.

    Parameters
    ----------
    world : WorldMap
        World model whose music fields should change.
    new_index : int
        Music theme index to apply.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    old_index : int
        Music theme restored during ``undo()``.
    new_index : int
        Music theme applied during ``redo()``.
    """

    def __init__(self, world: WorldMap, new_index: int):
        """Stage a world-music update for undoable replay.

        The editor treats arrival music and steady-state world music as a
        single user-facing choice, so the command snapshots one old theme and
        replays one new theme into both fields.

        Parameters
        ----------
        world
            World model whose music fields should change.
        new_index
            Music theme index written to both steady-state and arrival slots.
        """
        super(WorldMusicIndex, self).__init__()

        self.world = world
        self.old_index = world.data.music_index
        self.new_index = new_index

        self.setText(
            tr(
                TR_CONTEXT, "command.set_music_theme", "Setting Music Theme to '{music_theme}' ({music_index:#X})"
            ).format(
                music_theme=tr_data_name("MusicTheme", MUSIC_THEMES[new_index]),
                music_index=new_index,
            )
        )

    def undo(self):
        """Restore the previous world music theme in both playback fields."""
        self.world.data.music_index = self.old_index
        self.world.data.music_arrival_index = self.old_index

    def redo(self):
        """Apply the staged world music theme in both playback fields."""
        self.world.data.music_index = self.new_index
        self.world.data.music_arrival_index = self.new_index


class WorldBottomTile(QUndoCommand):
    """Change the border tile used below the visible world map.

    The bottom-border tile is edited from the same world-info workflow that
    changes music, palette, and animation settings. Keeping it in its own
    command gives that workflow a reversible visual-boundary edit instead of an
    anonymous parsed-byte change.

    Parameters
    ----------
    world : WorldMap
        World model whose border tile should change.
    new_index : int
        Tile index to store as the bottom-border tile.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    old_index : int
        Bottom-border tile restored during ``undo()``.
    new_index : int
        Bottom-border tile applied during ``redo()``.
    """

    def __init__(self, world: WorldMap, new_index: int):
        """Stage a bottom-border tile replacement.

        This command isolates the border-art byte from larger world edits so
        the tool window can adjust it with the same undo semantics as movement
        and metadata commands. The constructor snapshots the previous tile
        before the preview changes so ``undo()`` restores the exact border art
        that was visible when the command was created. Construction therefore
        stages one reversible swap between the old border tile and the
        replacement tile by storing both tile indexes for the later replay
        steps.

        Parameters
        ----------
        world
            World model whose border tile should change.
        new_index
            Tile index written into the world data.
        """
        super(WorldBottomTile, self).__init__()

        self.world = world
        self.old_index = world.data.bottom_border_tile
        self.new_index = new_index

        self.setText(
            tr(TR_CONTEXT, "setting_bottom_tile_to_tile_index_x", "Setting Bottom Tile to {tile_index:#x}").format(
                tile_index=new_index
            )
        )

    def undo(self):
        """Restore the previous bottom-border tile index."""
        self.world.data.bottom_border_tile = self.old_index

    def redo(self):
        """Apply the staged bottom-border tile index."""
        self.world.data.bottom_border_tile = self.new_index


class SetLevelAddress(DirtyAdditionalDataMixin, QUndoCommand):
    """Change the ROM address for a world-map level pointer.

    This command is part of Scribe's "retarget this pointer to a different
    level payload" workflow. It keeps the old and new ROM targets on one undo
    boundary while marking Foundry's parse-sensitive state dirty for later
    rereads.

    Parameters
    ----------
    data : LevelPointerData
        Level-pointer record whose level-data address should change.
    new_address : int
        Replacement ROM address for the level payload.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    data : LevelPointerData
        Parsed level-pointer record mutated by the command.
    old_address : int
        Level-data address restored during ``undo()``.
    new_address : int
        Level-data address applied during ``redo()``.
    """

    def __init__(self, data: LevelPointerData, new_address: int, parent=None):
        """Stage a new level-data address for one level pointer.

        The constructor captures the pointer record and its previous ROM target
        before any mutation happens so ``redo()`` can retarget the pointer and
        ``undo()`` can restore the original level binding without rereading the
        world data. That makes one tool-window address edit replay as a clean
        swap between two target payloads rather than a fresh pointer search.

        Parameters
        ----------
        data
            Level pointer record whose level address should change.
        new_address
            New ROM address for the referenced level data.
        parent
            Optional Qt undo-command parent.
        """
        super(SetLevelAddress, self).__init__(parent)

        self.data = data

        self.old_address = data.level_address
        self.new_address = new_address

        self.setText(
            tr(
                TR_CONTEXT,
                "command.set_lp_level_address",
                "Set LP #{pointer_index} Level Address to {level_address:#x}",
            ).format(
                pointer_index=self.data.index + 1,
                level_address=new_address,
            )
        )

    def undo(self):
        """Restore the previous level-data address and mark caches dirty."""
        self.data.level_address = self.old_address

        super().undo()

    def redo(self):
        """Apply the staged level-data address and mark caches dirty."""
        self.data.level_address = self.new_address

        super().redo()


class SetEnemyAddress(DirtyAdditionalDataMixin, QUndoCommand):
    """Change the ROM address for a level pointer's enemy data.

    Enemy-payload retargeting travels through the same workflow as level-data
    retargeting: one pointer row is rebound to a different parsed payload, and
    later reparses must follow that new address in both directions of the undo
    stack.

    Parameters
    ----------
    data : LevelPointerData
        Level-pointer record whose enemy-data address should change.
    new_address : int
        Replacement ROM address for the enemy payload.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    data : LevelPointerData
        Parsed level-pointer record mutated by the command.
    old_address : int
        Enemy-data address restored during ``undo()``.
    new_address : int
        Enemy-data address applied during ``redo()``.
    """

    def __init__(self, data: LevelPointerData, new_address: int, parent=None):
        """Stage a new enemy-data address for one level pointer.

        The constructor snapshots the pointer's current enemy address so the
        command can swap between old and new enemy payloads without reloading
        the surrounding world record.

        Parameters
        ----------
        data
            Level pointer record whose enemy address should change.
        new_address
            New ROM address for the referenced enemy data.
        parent
            Optional Qt undo-command parent.
        """
        super(SetEnemyAddress, self).__init__(parent)

        self.data = data

        self.old_address = data.enemy_address
        self.new_address = new_address

        self.setText(
            tr(
                TR_CONTEXT,
                "command.set_lp_enemy_address",
                "Set LP #{pointer_index} Enemy Address to {enemy_address:#x}",
            ).format(
                pointer_index=self.data.index + 1,
                enemy_address=new_address,
            )
        )

    def undo(self):
        """Restore the previous enemy-data address and mark caches dirty."""
        self.data.enemy_address = self.old_address

        super().undo()

    def redo(self):
        """Apply the staged enemy-data address and mark caches dirty."""
        self.data.enemy_address = self.new_address

        super().redo()


class SetObjectSet(DirtyAdditionalDataMixin, QUndoCommand):
    """Change the object set associated with a level pointer.

    A world-map pointer is not fully specified until Scribe also chooses the
    object-set decode context that Foundry will use later. This command keeps
    that decode-context swap on the same replay seam as pointer-address edits.

    Parameters
    ----------
    data : LevelPointerData
        Level-pointer record whose object set should change.
    object_set_number : int
        Replacement object-set identifier.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    data : LevelPointerData
        Parsed level-pointer record mutated by the command.
    old_object_set : int
        Object-set identifier restored during ``undo()``.
    new_object_set : int
        Object-set identifier applied during ``redo()``.
    """

    def __init__(self, data: LevelPointerData, object_set_number: int, parent=None):
        """Stage a new object-set selection for one level pointer.

        The constructor captures the prior object set before the pointer is
        repointed. That lets ``undo()`` restore the previous decode context
        even if other edits happened after the selection changed. The
        constructor therefore stages one reversible swap between two decode
        contexts for the later replay steps.

        Parameters
        ----------
        data
            Level pointer record whose object set should change.
        object_set_number
            New object-set identifier.
        parent
            Optional Qt undo-command parent.
        """
        super(SetObjectSet, self).__init__(parent)

        self.data = data

        self.old_object_set = data.object_set
        self.new_object_set = object_set_number

        self.setText(
            tr(
                TR_CONTEXT, "command.set_lp_object_set", "Set LP #{pointer_index} Object Set to {object_set_name}"
            ).format(
                pointer_index=self.data.index + 1,
                object_set_name=tr_data_name("ObjectSet", OBJECT_SET_NAMES[object_set_number]),
            )
        )

    def undo(self):
        """Restore the previous object-set selection and dirty parse caches."""
        self.data.object_set = self.old_object_set

        super().undo()

    def redo(self):
        """Apply the staged object-set selection and dirty parse caches."""
        self.data.object_set = self.new_object_set

        super().redo()


class SetSpriteType(QUndoCommand):
    """Change the world-map object type for a sprite entry.

    Sprite editing separates the rendered world-map object kind from any item
    payload the sprite also carries. This command owns the type half of that
    split: construction snapshots the old parsed type and stores the
    replacement type, ``redo()`` writes the replacement type, and ``undo()``
    restores the original sprite identity without touching the separate item
    command. In the editor workflow, one sprite-row type edit becomes one
    reversible mutation of the parsed sprite record, and the undo stack can
    replay that type swap without rebuilding the rest of the row.

    Parameters
    ----------
    data : SpriteData
        Sprite record whose type should change.
    new_type : int
        Replacement world-map object type.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    data : SpriteData
        Parsed sprite record mutated by the command.
    old_type : int
        Sprite type restored during ``undo()``.
    new_type : int
        Sprite type applied during ``redo()``.
    """

    def __init__(self, data: SpriteData, new_type: int, parent=None):
        """Stage a sprite-type replacement.

        The constructor snapshots the parsed type before the tool window
        refreshes so ``undo()`` can restore the original map-object semantics
        without reconstructing the sprite from surrounding world state. The
        constructor therefore stages one reversible type swap that ``redo()``
        applies and ``undo()`` unwinds.

        Parameters
        ----------
        data
            Sprite record whose type should change.
        new_type
            New map-object type identifier.
        parent
            Optional Qt undo-command parent.
        """
        super(SetSpriteType, self).__init__(parent)

        self.data = data

        self.old_type = self.data.type
        self.new_type = new_type

        self.setText(
            tr(TR_CONTEXT, "command.set_sprite_type", "Set Sprite #{sprite_index} Type to {object_name}").format(
                sprite_index=self.data.index + 1,
                object_name=tr_data_name("MapObject", MAPOBJ_NAMES[new_type]),
            )
        )

    def undo(self):
        """Restore the previous sprite type."""
        self.data.type = self.old_type

    def redo(self):
        """Apply the staged sprite type."""
        self.data.type = self.new_type


class SetSpriteItem(QUndoCommand):
    """Change the item payload stored on a sprite entry.

    Some sprite records encode both a visible world-map object and an item or
    reward payload. This command isolates the payload half of that pair:
    construction snapshots the old parsed payload and stores the replacement
    payload, ``redo()`` writes the replacement payload, and ``undo()`` restores
    the original payload without changing the sprite's type. In the editor
    workflow, that makes one item-column edit replay as a payload-only swap on
    the parsed sprite record while the visible sprite type and other row state
    remain untouched.

    Parameters
    ----------
    data : SpriteData
        Sprite record whose item value should change.
    new_item : int
        Replacement map item identifier.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    data : SpriteData
        Parsed sprite record mutated by the command.
    old_item : int
        Item identifier restored during ``undo()``.
    new_item : int
        Item identifier applied during ``redo()``.
    """

    def __init__(self, data: SpriteData, new_item: int, parent=None):
        """Stage a sprite-item replacement.

        The constructor snapshots the parsed payload before the editor updates
        so ``undo()`` can restore the original reward or item state without
        rebuilding the sprite record from scratch. The constructor therefore
        stages one reversible payload swap for the later replay steps.

        Parameters
        ----------
        data
            Sprite record whose item value should change.
        new_item
            New map-item identifier.
        parent
            Optional Qt undo-command parent.
        """
        super(SetSpriteItem, self).__init__(parent)

        self.data = data

        self.old_item = self.data.item
        self.new_item = new_item

        self.setText(
            tr(TR_CONTEXT, "command.set_sprite_item", "Set Sprite #{sprite_index} Item to {item_name}").format(
                sprite_index=self.data.index + 1,
                item_name=tr_data_name("MapItem", MAPITEM_NAMES[new_item]),
            )
        )

    def undo(self):
        """Restore the previous sprite item value."""
        self.data.item = self.old_item

    def redo(self):
        """Apply the staged sprite item value."""
        self.data.item = self.new_item


class SetScreenCount(DirtyAdditionalDataMixin, QUndoCommand):
    """Resize the horizontal screen span of one world map.

    Screen-count edits are structural world changes: they alter how wide the
    world is, how tile data is interpreted, and when a loaded world view must
    reread its tile buffer. The command therefore captures both count and tile
    bytes, not just the parsed count field, so replay moves the world between
    two complete width-and-buffer states.

    Parameters
    ----------
    world_data : WorldMapData
        Parsed world-data record that stores the screen count.
    screen_count : int
        Replacement number of horizontal screens.
    world_map : WorldMap, optional
        Loaded world model to refresh after the tile buffer changes.

    Attributes
    ----------
    world_data : WorldMapData
        Parsed world-data record mutated by the command.
    world_map : WorldMap or None
        Loaded world model to refresh when present.
    old_screen_count : int
        Screen count restored during ``undo()``.
    old_world_data : bytearray
        Snapshot of tile bytes restored during ``undo()``.
    new_screen_count : int
        Screen count applied during ``redo()``.
    """

    def __init__(
        self,
        world_data: WorldMapData,
        screen_count: int,
        world_map: WorldMap | None = None,
    ):
        """Stage a new world width and optional tile reread.

        The constructor snapshots the world's existing tile buffer before the
        width changes because shrinking or expanding the world can change which
        bytes belong to the live map. When a loaded ``WorldMap`` is present,
        the staged payload is enough to replay a full width change and a tile
        reread together, with ``redo()`` applying the new width state and
        ``undo()`` restoring the previous width state.

        Parameters
        ----------
        world_data
            Parsed world-data record that stores the screen count.
        screen_count
            New number of horizontal screens for the world.
        world_map
            Optional loaded world model to refresh after the tile data changes.
        """
        super(SetScreenCount, self).__init__()

        self.world_data = world_data
        self.world_map = world_map

        self.old_screen_count = self.world_data.screen_count
        self.old_world_data = world_data.tile_data.copy()
        self.new_screen_count = screen_count

        self.setText(
            tr(
                TR_CONTEXT,
                "command.set_world_screen_count",
                "Set World {world_number}'s screen count to {screen_count}",
            ).format(
                world_number=self.world_data.index + 1,
                screen_count=screen_count,
            )
        )

    def undo(self):
        """Restore the previous screen span and tile buffer snapshot."""
        self.world_data.screen_count = self.old_screen_count
        self.world_data.tile_data = self.old_world_data

        if self.world_map is not None:
            self.world_map.reread_tiles()

        super().undo()

    def redo(self):
        """Apply the staged screen span and refresh loaded tiles if needed."""
        self.world_data.screen_count = self.new_screen_count

        if self.world_map is not None:
            self.world_map.reread_tiles()

        super().redo()


class ChangeReplacementTile(QUndoCommand):
    """Replace the fortress-effect tile block tied to one lock index.

    Fortress effects are edited as "which replacement block belongs to this
    shared lock group?" decisions. The command translates that one editor
    choice into the four-tile payload stored on the parsed lock records, with
    ``redo()`` expanding the chosen block and ``undo()`` restoring the prior
    four-tile state.

    Parameters
    ----------
    world : WorldMap
        World model containing the editable lock set.
    fortress_fx_index : int
        Shared effect index used to find the targeted locks.
    replacement_tile_index : int
        Replacement world-map block identifier.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    fx_index : int
        Shared fortress-effect index used to match locks.
    replacement_tile_index : int
        Replacement block identifier applied during ``redo()``.
    old_replacement_tile_index : int
        Prior replacement block restored during ``undo()``.
    old_tile_indexes : bytearray
        Prior four-tile block restored during ``undo()``.
    """

    def __init__(
        self,
        world: WorldMap,
        fortress_fx_index: int,
        replacement_tile_index: int,
        parent=None,
    ):
        """Stage a new replacement block for a fortress effect.

        The constructor stores the chosen block identifier because ``redo()``
        will expand it into four tile indexes for every matching lock group,
        and ``undo()`` must later restore both the raw block id and the old
        expanded quartet. That staging lets one block-picker gesture drive
        every matching lock record through the same replay path.

        Parameters
        ----------
        world
            World model containing the lock and bridge objects to update.
        fortress_fx_index
            Shared index that identifies the lock set for one fortress effect.
        replacement_tile_index
            New world-map block identifier that should replace the lock tiles.
        parent
            Optional Qt undo-command parent.
        """
        super(ChangeReplacementTile, self).__init__(parent)

        self.world = world
        self.fx_index = fortress_fx_index
        self.replacement_tile_index = replacement_tile_index

        self.old_replacement_tile_index = -1
        self.old_tile_indexes = bytearray(4)

    def undo(self):
        """Restore the previous tile block for every matching lock set."""
        for lock in self.world.locks_and_bridges:
            if lock.data.index == self.fx_index:
                lock.data.tile_indexes = self.old_tile_indexes
                lock.data.replacement_block_index = self.old_replacement_tile_index

    def redo(self):
        """Expand the replacement block into four tile indexes and apply it."""
        block = get_worldmap_tile(self.replacement_tile_index)

        for lock in self.world.locks_and_bridges:
            if lock.data.index == self.fx_index:
                self.old_tile_indexes = lock.data.tile_indexes
                self.old_replacement_tile_index = lock.data.replacement_block_index

                lock.data.tile_indexes = bytearray(
                    [
                        block.lu_tile.tile_index,
                        block.ru_tile.tile_index,
                        block.ld_tile.tile_index,
                        block.rd_tile.tile_index,
                    ]
                )
                lock.data.replacement_block_index = self.replacement_tile_index


class ChangeLockIndex(QUndoCommand):
    """Move a lock or bridge into a different shared fortress-effect group.

    Locks and bridges that share an index also share replacement-tile behavior
    later in the world lifecycle. This command edits grouping, not just one
    integer field, and keeps replacement-tile coherence when the selected
    object joins an existing group.

    Parameters
    ----------
    world : WorldMap
        World model containing the editable lock set.
    lock : Lock
        Selected lock or bridge whose shared index should change.
    new_index : int
        Replacement fortress-effect index.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    lock : Lock
        Selected lock or bridge being reassigned.
    old_index : int
        Shared index restored during ``undo()``.
    old_replacement_tile : int
        Replacement tile index associated with the old group.
    new_index : int
        Shared index applied during ``redo()``.
    """

    def __init__(self, world: WorldMap, lock: Lock, new_index: int, parent=None):
        """Stage a new shared index for one lock record.

        The constructor snapshots the selected object's old group so replay can
        either join another group's replacement-tile contract or restore the
        original grouping behavior during ``undo()``.

        Parameters
        ----------
        world
            World model containing the editable lock set.
        lock
            Lock or bridge whose shared index should change.
        new_index
            New shared effect index.
        parent
            Optional Qt undo-command parent.
        """
        super(ChangeLockIndex, self).__init__(parent)

        self.world = world
        self.lock = lock

        self.old_index = lock.data.index
        self.old_replacement_tile = lock.data.replacement_block_index
        self.new_index = new_index

    def undo(self):
        """Restore the original shared index for the selected lock."""
        self._change_lock_index(self.old_index)

    def redo(self):
        """Apply the staged shared index for the selected lock."""
        self._change_lock_index(self.new_index)

    def _change_lock_index(self, new_index: int):
        """Apply one lock-index change and keep replacement tiles coherent.

        Parameters
        ----------
        new_index
            Shared fortress-effect index that should be assigned.
        """
        if self.old_index == self.new_index:
            return

        for lock in self.world.locks_and_bridges:
            if lock is self.lock:
                continue

            if lock.data.index == new_index:
                self.lock.data.change_index(new_index)
                self.lock.data.replacement_block_index = lock.data.replacement_block_index
                self.lock.data.set_pos(lock.data.pos)

                break

        else:
            self.lock.data.change_index(new_index)
            self.lock.data.read_values()


class SetWorldScroll(QUndoCommand):
    """Toggle horizontal scrolling for a world map.

    The world-info editor exposes scrolling as a boolean choice, but the parsed
    world data stores either a no-scroll sentinel or a byte derived from the
    current screen count. This command owns that translation by snapshotting
    the previous byte, computing the new byte from the toggle at construction
    time, and replaying that parsed-byte swap through ``redo()`` and
    ``undo()``.

    Parameters
    ----------
    world_data : WorldMapData
        Parsed world-data record that stores the scroll byte.
    should_scroll : bool
        Whether the world should use scrolling.

    Attributes
    ----------
    world_data : WorldMapData
        Parsed world-data record mutated by the command.
    old_value : int
        Scroll byte restored during ``undo()``.
    new_value : int
        Scroll byte applied during ``redo()``.
    """

    def __init__(self, world_data: WorldMapData, should_scroll: bool):
        """Stage a new scroll mode for one world.

        The constructor converts a UI-level toggle into the exact parsed byte
        that ``write_back()`` will persist. Storing both forms up front lets
        ``undo()`` restore the old scroll policy without recomputing it from
        later world state. Construction therefore stages one reversible policy
        swap that ``redo()`` writes through ``write_back()`` and ``undo()``
        restores the same way.

        Parameters
        ----------
        world_data
            Parsed world-data record that stores the scroll flag.
        should_scroll
            ``True`` to derive a scrolling value from the screen count,
            ``False`` to write the no-scroll sentinel.
        """
        super(SetWorldScroll, self).__init__()

        self.world_data = world_data
        self.old_value = world_data.map_scroll
        self.new_value = world_data.screen_count << 4 if should_scroll else NO_MAP_SCROLLING

        if should_scroll:
            self.setText(tr(TR_CONTEXT, "activate_map_scroll", "Activate Map Scroll"))
        else:
            self.setText(tr(TR_CONTEXT, "deactivate_map_scroll", "Deactivate Map Scroll"))

    def undo(self):
        """Restore the previous scroll byte and flush it to the ROM record."""
        self.world_data.map_scroll = self.old_value
        self.world_data.write_back()

    def redo(self):
        """Apply the staged scroll byte and flush it to the ROM record."""
        self.world_data.map_scroll = self.new_value
        self.world_data.write_back()


class SetWorldIndex(DirtyAdditionalDataMixin, QUndoCommand):
    """Reassign a world and its sprites to a different world index.

    Moving a world to another index changes more than one parsed integer:
    dependent sprite records must recalculate their addresses against the new
    world slot. The command keeps those recalculations on the same undo
    boundary as the index change itself.

    Parameters
    ----------
    world_data : WorldMapData
        Parsed world-data record whose world index should change.
    sprites : list[SpriteData]
        Sprite records that must recalculate addresses after the move.
    new_index : int
        Replacement world index.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    world_data : WorldMapData
        Parsed world-data record mutated by the command.
    sprites : list[SpriteData]
        Dependent sprite records that are recalculated after each replay.
    old_index : int
        World index restored during ``undo()``.
    new_index : int
        World index applied during ``redo()``.
    """

    def __init__(
        self,
        world_data: WorldMapData,
        sprites: list[SpriteData],
        new_index: int,
        parent=None,
    ):
        """Stage a world-index remap for one overworld and its sprites.

        The constructor stores the original world slot and dependent sprite
        list before any recalculation happens. That gives the undo stack one
        stable payload for replaying the world migration and the address
        refreshes it forces.

        Parameters
        ----------
        world_data
            Parsed world-data record whose index should change.
        sprites
            Sprite records that must recalculate their addresses after the
            world index moves.
        new_index
            New world index to assign.
        parent
            Optional Qt undo-command parent.
        """
        super(SetWorldIndex, self).__init__(parent)

        self.world_data = world_data
        self.sprites = sprites

        self.old_index = world_data.index
        self.new_index = new_index

        self.setText(
            tr(
                TR_CONTEXT, "command.set_world_index", "Set World {old_world_number}'s index to {new_world_number}"
            ).format(
                old_world_number=self.old_index + 1,
                new_world_number=new_index + 1,
            )
        )

    def undo(self):
        """Restore the original world index and recalculate sprite addresses."""
        self._change_world_index(self.old_index)

        super().undo()

    def redo(self):
        """Apply the staged world index and recalculate sprite addresses."""
        self._change_world_index(self.new_index)

        super().redo()

    def _change_world_index(self, new_index: int):
        """Apply one world-index change and update dependent sprite records.

        Parameters
        ----------
        new_index
            World index to store on the world data.
        """
        self.world_data.change_index(new_index)

        for sprite in self.sprites:
            sprite.calculate_addresses()


class SetStructureBlockAddress(DirtyAdditionalDataMixin, QUndoCommand):
    """Change the ROM address used for structure block data.

    Structure-block edits retarget the byte stream used to decode larger world
    features such as paths and map structures. This command isolates that ROM
    pointer change from other world-info edits while still participating in the
    parse-dirty workflow.

    Parameters
    ----------
    world_data : WorldMapData
        Parsed world-data record whose structure-block address should change.
    new_address : int
        Replacement ROM address.

    Attributes
    ----------
    world_data : WorldMapData
        Parsed world-data record mutated by the command.
    old_address : int
        Structure-block address restored during ``undo()``.
    new_address : int
        Structure-block address applied during ``redo()``.
    """

    def __init__(self, world_data: WorldMapData, new_address: int):
        """Stage a structure-block address rewrite.

        The constructor freezes the previous ROM pointer before the edit so the
        undo stack can move cleanly between two structure sources and trigger a
        later reread through the dirty-additional-data path instead of leaving
        the parsed world midway between two structure sources. Construction
        therefore stages one reversible source-pointer swap for replay.

        Parameters
        ----------
        world_data
            Parsed world-data record whose structure-block address should
            change.
        new_address
            New ROM address for structure block data.
        """
        super(SetStructureBlockAddress, self).__init__()

        self.world_data = world_data
        self.old_address = world_data.structure_block_address
        self.new_address = new_address

    def undo(self):
        """Restore the previous structure-block address."""
        self.world_data.structure_block_address = self.old_address

        super().undo()

    def redo(self):
        """Apply the staged structure-block address."""
        self.world_data.structure_block_address = self.new_address

        super().redo()


class SetTileDataOffset(DirtyAdditionalDataMixin, QUndoCommand):
    """Change the ROM offset used to locate world tile data.

    This command retargets the tile-data stream that the world reader later
    interprets as visible map layout. Treating that offset as its own undoable
    edit makes tile-stream rebasing explicit and reversible. Construction
    snapshots the old source stream location and stores the rebased one so the
    undo stack can replay one complete source-stream swap through ``redo()``
    and ``undo()``.

    Parameters
    ----------
    world_data : WorldMapData
        Parsed world-data record whose tile-data offset should change.
    new_offset : int
        Replacement ROM offset.

    Attributes
    ----------
    world_data : WorldMapData
        Parsed world-data record mutated by the command.
    old_offset : int
        Tile-data offset restored during ``undo()``.
    new_offset : int
        Tile-data offset applied during ``redo()``.
    """

    def __init__(self, world_data: WorldMapData, new_offset: int):
        """Stage a tile-data offset rewrite.

        The constructor snapshots the previous source offset before any
        mutation so ``undo()`` can restore the original tile stream and
        ``redo()`` can reapply the rebased stream without consulting external
        editor state.

        Parameters
        ----------
        world_data
            Parsed world-data record whose tile-data offset should change.
        new_offset
            New ROM offset for world tile data.
        """
        super(SetTileDataOffset, self).__init__()

        self.world_data = world_data
        self.old_offset = world_data.tile_data_offset
        self.new_offset = new_offset

    def undo(self):
        """Restore the previous tile-data offset."""
        self.world_data.tile_data_offset = self.old_offset

        super().undo()

    def redo(self):
        """Apply the staged tile-data offset."""
        self.world_data.tile_data_offset = self.new_offset

        super().redo()


class ChangeSpriteIndex(QUndoCommand):
    """Reorder sprite records inside a world's sprite list.

    Sprite order is part of the parsed world contract because later save and
    reread paths preserve sequence, not just sprite payloads. This command
    therefore treats reordering as a first-class edit with explicit source and
    destination indexes.

    Parameters
    ----------
    world : WorldMap
        World model whose sprite order should change.
    old_index : int
        Sprite index before the move.
    new_index : int
        Sprite index after the move.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    old_index : int
        Sprite index restored during ``undo()``.
    new_index : int
        Sprite index applied during ``redo()``.
    """

    def __init__(self, world: WorldMap, old_index: int, new_index: int, parent=None):
        """Stage a sprite-list move for undoable replay.

        The constructor stores both list indexes up front because later
        selection changes in the world view should not change which parsed
        permutation ``redo()`` applies or which original order ``undo()``
        restores.

        Parameters
        ----------
        world
            World model whose sprite order should change.
        old_index
            Current sprite index.
        new_index
            Destination sprite index.
        parent
            Optional Qt undo-command parent.
        """
        super(ChangeSpriteIndex, self).__init__(parent)
        self.world = world

        self.old_index = old_index
        self.new_index = new_index

        self.setText(
            tr(
                TR_CONTEXT, "change_sprite_index_old_index_new_index", "Change Sprite Index {old_index} -> {new_index}"
            ).format(
                old_index=self.old_index,
                new_index=self.new_index,
            )
        )

    def undo(self):
        """Move the sprite back to its original list position."""
        self.world.move_sprites(self.new_index, self.old_index)

    def redo(self):
        """Move the sprite to its staged destination list position."""
        self.world.move_sprites(self.old_index, self.new_index)


class ChangeLevelPointerIndex(DirtyAdditionalDataMixin, QUndoCommand):
    """Reorder level-pointer records inside a world's pointer list.

    Pointer order is semantically meaningful because the parsed list is later
    serialized and mirrored into the rendered world-pointer collection. The
    command keeps that reorder and the dirty-cache signal together so both
    layers travel through the same undo seam.

    Parameters
    ----------
    world : WorldMap
        World model whose level-pointer order should change.
    old_index : int
        Level-pointer index before the move.
    new_index : int
        Level-pointer index after the move.
    parent : QUndoCommand, optional
        Optional Qt parent command.

    Attributes
    ----------
    world : WorldMap
        World model mutated by the command.
    old_index : int
        Level-pointer index restored during ``undo()``.
    new_index : int
        Level-pointer index applied during ``redo()``.
    """

    def __init__(self, world: WorldMap, old_index: int, new_index: int, parent=None):
        """Stage a level-pointer reorder for undoable replay.

        The constructor records the source and destination list indexes so the
        world model can replay the same permutation in both directions without
        recomputing selection-derived indexes later.

        Parameters
        ----------
        world
            World model whose level-pointer order should change.
        old_index
            Current level-pointer index.
        new_index
            Destination level-pointer index.
        parent
            Optional Qt undo-command parent.
        """
        super(ChangeLevelPointerIndex, self).__init__(parent)
        self.world = world

        self.old_index = old_index
        self.new_index = new_index

        self.setText(
            tr(
                TR_CONTEXT,
                "command.change_level_pointer_index",
                "Change Level Pointer Index {old_index} -> {new_index}",
            ).format(
                old_index=self.old_index,
                new_index=self.new_index,
            )
        )

    def undo(self):
        """Move the level pointer back to its original list position."""
        self.world.move_level_pointers(self.new_index, self.old_index)

        super().undo()

    def redo(self):
        """Move the level pointer to its staged destination list position."""
        self.world.move_level_pointers(self.old_index, self.new_index)

        super().redo()


class AddLevelPointer(DirtyAdditionalDataMixin, QUndoCommand):
    """Append a new level pointer and optional rendered object to a world.

    Adding a pointer is a creation workflow, not just a list append. The
    command owns the parsed record, safe default field seeding, and optional
    rendered object so later ``redo()`` calls can reinsert the same staged
    pointer identity without rebuilding it.

    Parameters
    ----------
    world_data : WorldMapData
        Parsed world-data record that owns the level-pointer list.
    world : WorldMap, optional
        Loaded world model that should mirror the insertion.

    Attributes
    ----------
    world : WorldMap or None
        Loaded world model to keep in sync when present.
    world_data : WorldMapData
        Parsed world-data record mutated by the command.
    level_pointer_data : LevelPointerData
        New parsed level-pointer record staged for insertion.
    level_pointer : LevelPointer
        Rendered level-pointer object staged for insertion into ``world``.
    """

    def __init__(self, world_data: WorldMapData, world: WorldMap | None = None):
        """Stage creation of a default level pointer.

        The command builds both the parsed data-point record and the optional
        rendered :class:`LevelPointer` immediately so the same staged objects
        can be inserted on ``redo()`` and reinserted after ``undo()`` without
        recalculating indexes or default field values. It also seeds a legal
        first position and zeroed ROM targets so the pointer enters the world
        in a parseable state before a later edit fills in its real addresses.

        Parameters
        ----------
        world_data
            Parsed world-data record that owns the level-pointer list.
        world
            Optional loaded world model that should mirror the data-point
            insertion with a rendered :class:`LevelPointer`.
        """
        super(AddLevelPointer, self).__init__()

        self.world = world
        self.world_data = world_data

        self.level_pointer_data = LevelPointerData(self.world_data, self.world_data.level_count)
        self.level_pointer_data.pos = Position(0, FIRST_VALID_ROW, 0)
        self.level_pointer_data.object_set = 1
        self.level_pointer_data.level_address = 0x0
        self.level_pointer_data.enemy_address = 0x0

        self.level_pointer = LevelPointer(self.level_pointer_data)

        self.setText(tr(TR_CONTEXT, "add_level_pointer", "Add Level Pointer"))

    def undo(self):
        """Remove the staged pointer from both parsed and rendered collections."""
        self.world_data.level_count_screen_1 -= 1
        self.world_data.level_pointers.remove(self.level_pointer_data)

        if self.world is not None:
            self.world.level_pointers.remove(self.level_pointer)

        super().undo()

    def redo(self):
        """Insert the staged pointer into both parsed and rendered collections."""
        self.world_data.level_count_screen_1 += 1

        self.world_data.level_pointers.append(self.level_pointer_data)

        if self.world is not None:
            self.world.level_pointers.append(self.level_pointer)

        super().redo()


class RemoveLevelPointer(DirtyAdditionalDataMixin, QUndoCommand):
    """Remove one level pointer and preserve enough state to restore it.

    Pointer removal has to preserve both parsed ordering and the per-screen
    counts that later serialization uses. When a live world view is loaded,
    the command also owns the rendered pointer object so undo can restore the
    same visual pointer identity in the same list slot.

    Parameters
    ----------
    world_data : WorldMapData
        Parsed world-data record that owns the level-pointer list.
    index : int, optional
        Index of the pointer to remove. ``-1`` removes the last pointer.
    world : WorldMap, optional
        Loaded world model whose rendered pointer list should stay aligned.

    Attributes
    ----------
    world : WorldMap or None
        Loaded world model to keep in sync when present.
    world_data : WorldMapData
        Parsed world-data record mutated by the command.
    index : int
        Pointer index removed during ``redo()``.
    removed_level_pointer_data : LevelPointerData
        Parsed pointer record reinserted during ``undo()``.
    removed_level_pointer : LevelPointer or None
        Rendered pointer object reinserted into ``world`` when present.
    """

    def __init__(self, world_data: WorldMapData, index=-1, world: WorldMap | None = None):
        """Stage removal of one level pointer.

        The constructor snapshots both the parsed pointer record and the
        optional rendered pointer object because ``undo()`` must restore list
        order and per-screen counts without depending on any later world state.

        Parameters
        ----------
        world_data
            Parsed world-data record that owns the level-pointer list.
        index
            Index of the level pointer to remove. ``-1`` removes the last
            pointer.
        world
            Optional loaded world model whose rendered pointer list should stay
            aligned with the parsed data.
        """
        super(RemoveLevelPointer, self).__init__()

        self.world = world
        self.world_data = world_data

        if index == -1:
            index = len(self.world_data.level_pointers) - 1

        self.index = index

        self.removed_level_pointer_data = self.world_data.level_pointers[index]

        if world is not None:
            self.removed_level_pointer = world.level_pointers[index]
        else:
            self.removed_level_pointer = None

        self.setText(
            tr(TR_CONTEXT, "remove_level_pointer_pointer_index", "Remove Level Pointer #{pointer_index}").format(
                pointer_index=index
            )
        )

    def _level_count_attr_name(self) -> str:
        """Resolve the level-count field that owns the staged pointer.

        This helper is the parser metadata boundary for pointer removal. It
        derives the ``WorldMapData`` counter from the preserved pointer screen
        so undo and redo replay against the original world state instead of any
        later table selection or reordered row.

        Returns
        -------
        str
            Name of the ``WorldMapData`` counter that owns the removed
            pointer's screen.

        Notes
        -----
        Level-pointer removal must update both list membership and the parsed
        per-screen count field. Deriving the field name from the staged pointer
        keeps undo and redo aligned with the pointer's original screen rather
        than whichever row happens to be selected later.
        """
        return f"level_count_screen_{self.removed_level_pointer_data.screen + 1}"

    def undo(self):
        """Reinsert the removed pointer and repair per-screen level counts.

        Undo restores both the parsed pointer record and, when available, the
        rendered pointer object at the original list index. The per-screen
        counter is incremented first so parsed metadata and list membership are
        consistent before any view refresh reads them.
        """
        attr_name = self._level_count_attr_name()

        lvls_on_screen = getattr(self.world_data, attr_name)

        setattr(self.world_data, attr_name, lvls_on_screen + 1)

        self.world_data.level_pointers.insert(self.index, self.removed_level_pointer_data)

        if self.world is not None:
            self.world.level_pointers.insert(self.index, self.removed_level_pointer)

        super().undo()

    def redo(self):
        """Drop the staged pointer and decrement its owning screen count.

        The command derives the counter name from the pointer's screen number
        so the parsed per-screen totals stay synchronized with the list removal
        rather than only shrinking the raw pointer list. That keeps later
        serialization and world rereads aligned with the edited pointer list,
        and it ensures the replayed removal updates both pointer membership and
        the screen-level metadata that describes that membership.
        """
        attr_name = self._level_count_attr_name()

        lvls_on_screen = getattr(self.world_data, attr_name)

        assert lvls_on_screen > 0

        setattr(self.world_data, attr_name, lvls_on_screen - 1)

        self.world_data.level_pointers.pop(self.index)

        if self.world is not None:
            self.world.level_pointers.pop(self.index)

        super().redo()


class WorldDataStandIn:
    """Capture world metadata edits before they are written back.

    The tool-window UI can stage world-level edits independently from the
    underlying parsed records. This stand-in stores original values and helper
    :class:`SpriteData` objects so save commands can detect whether a world
    actually changed before flushing it back to ROM-backed storage.

    Parameters
    ----------
    world_data : WorldMapData
        Parsed world-data record that will later receive staged changes.

    Attributes
    ----------
    level_count : int
        Editable staged level count.
    screen_count : int
        Editable staged screen count.
    index : int
        Editable staged world index.
    _orig_level_count : int
        Original level-pointer count captured for change detection.
    _orig_screen_count : int
        Original screen count captured for change detection.
    _orig_index : int
        Original world index captured for change detection.
    sprites : list[SpriteData]
        Sprite helper records staged alongside the world metadata.
    data : WorldMapData
        Parsed world-data record that receives the final write-back.
    """

    def __init__(self, world_data: WorldMapData):
        """Snapshot editable world values and sprite helpers.

        Parameters
        ----------
        world_data
            Parsed world-data record that will later receive staged changes.

        Notes
        -----
        The stand-in snapshots original counts and index values separately
        from the editable fields so the overview table can stage multiple
        changes before any command writes back to parsed data. Sprite helpers
        are materialized here as well because final save commands flush both
        world metadata and sprite records together.
        """
        self.level_count = self._orig_level_count = world_data.level_count
        self.screen_count = self._orig_screen_count = world_data.screen_count
        self.index = self._orig_index = world_data.index

        self.sprites = [SpriteData(world_data, index) for index in range(SPRITE_COUNT)]

        self.data = world_data

    @property
    def changed(self):
        """Report whether staged metadata diverged from the original snapshot.

        Save commands use this property to decide whether a stand-in still
        represents pending work. It compares the editable fields against the
        construction-time snapshot instead of against the live parsed record so
        multiple staged edits can be flushed together later.

        Returns
        -------
        bool
            ``True`` when the staged level count, screen count, or world index
            no longer matches the construction-time snapshot and a save command
            should flush the stand-in back into the parsed world data.
        """
        lc_changed = self.level_count != self._orig_level_count
        sc_changed = self.screen_count != self._orig_screen_count
        ind_changed = self.index != self._orig_index

        return lc_changed or sc_changed or ind_changed


class SaveWorldsOnUndo(QUndoCommand):
    """Flush staged world edits back to their parsed records during undo.

    Some Scribe workflows stage multiple world edits in stand-in objects before
    deciding whether a save boundary on the undo stack should persist them.
    This command marks the backward-traversal half of that boundary.

    Parameters
    ----------
    worlds : list[WorldDataStandIn]
        Stand-in world records that should be written back.

    Attributes
    ----------
    worlds : list[WorldDataStandIn]
        Staged world records persisted during ``undo()``.
    """

    def __init__(self, worlds: list[WorldDataStandIn]):
        """Store the staged worlds that should be written back on undo.

        Parameters
        ----------
        worlds
            Stand-in records whose world and sprite data should be persisted.
        """
        super(SaveWorldsOnUndo, self).__init__()

        self.worlds = worlds

    def undo(self):
        """Write back world and sprite records for every staged world.

        Crossing this undo boundary persists the stand-in values into their
        parsed ``WorldMapData`` records. The command does not decide which
        worlds changed; it trusts the finalized macro to pass the staged set
        that should be flushed during backward replay.
        """
        for world in self.worlds:
            world.data.write_back()

            for sprite in world.sprites:
                sprite.write_back()


class SaveWorldsOnRedo(QUndoCommand):
    """Flush staged world edits back to their parsed records during redo.

    This command mirrors :class:`SaveWorldsOnUndo` for forward traversal so
    redo persists the same stand-in world records instead of leaving the editor
    with preview-only state. Crossing the save boundary in either direction
    therefore flushes the staged world and sprite data back into parsed
    storage.

    Parameters
    ----------
    worlds : list[WorldDataStandIn]
        Stand-in world records that should be written back.

    Attributes
    ----------
    worlds : list[WorldDataStandIn]
        Staged world records persisted during ``redo()``.
    """

    def __init__(self, worlds: list[WorldDataStandIn]):
        """Store the staged worlds that should be written back on redo.

        Parameters
        ----------
        worlds
            Stand-in records whose world and sprite data should be persisted.
        """
        super(SaveWorldsOnRedo, self).__init__()

        self.worlds = worlds

    def redo(self):
        """Write back world and sprite records for every staged world.

        Crossing this redo boundary persists the stand-in values into their
        parsed ``WorldMapData`` records. Mirroring the undo-side save command
        keeps both directions of the macro replay synchronized with ROM-facing
        data structures.
        """
        for world in self.worlds:
            world.data.write_back()

            for sprite in world.sprites:
                sprite.write_back()
