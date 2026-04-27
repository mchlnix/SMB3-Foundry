"""Undo commands for ROM-backed editor mutations.

This module is the command boundary between Qt widgets and mutable SMB3 level
data. The commands intentionally store levels, object indexes, serialized byte
data, and primitive values instead of long-lived object references where
possible. That design lets Foundry preserve and replay the undo stack after a
ROM hot swap or level reload, when the live ``LevelObject`` and ``EnemyItem``
instances may have been rebuilt from new ROM bytes.

Commands also provide ``to_data`` and ``from_data`` hooks used by the debug
macro exporter. Those hooks serialize editor intent rather than the entire
level, so replay can rebuild a sequence of user actions against the live
``Level`` or ``LevelRef``.

See Also
--------
foundry.gui.FoundryMainWindow
    Owns the undo stack that executes and replays these commands.
foundry.gui.visualization.level.LevelView
    Gesture-driven edits in the level view are translated into many of the
    commands defined here.
foundry.game.level.LevelRef
    Stable level reference used by commands that must survive reload and
    hot-swap workflows.
"""

from operator import itemgetter
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint
from PySide6.QtGui import QImage, QUndoCommand

from foundry.game.File import ROM
from foundry.game.gfx import GraphicsSet, change_color
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.Palette import PaletteGroup, load_palette_group
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.asm import load_asm_enemy
from smb3parse.constants import OBJECT_SET_NAMES, PIPE_PAIR_COUNT
from smb3parse.data_points import Position
from smb3parse.data_points.pipe_data import PipeData

if TYPE_CHECKING:
    from foundry.gui.visualization.level.LevelView import LevelView


class UndoCommand(QUndoCommand):
    """Base class for Foundry undo commands.

    Commands subclass Qt's ``QUndoCommand`` and add the serialization contract
    used by Foundry's debug macro export and replay tooling. Subclasses encode
    the smallest stable description of an editor action, such as a level marker,
    object index, ROM address, or byte payload, so undo history can survive
    level reloads that replace live model objects.

    Attributes
    ----------
    MAGIC_VALUE_LEVEL : str
        Marker used in serialized command data for the active ``Level``.
    MAGIC_VALUE_LEVEL_VIEW : str
        Marker used in serialized command data for the active ``LevelView``.
    """

    MAGIC_VALUE_LEVEL = "LEVEL"
    MAGIC_VALUE_LEVEL_VIEW = "LEVEL_VIEW"

    def to_data(self) -> list:
        """Serialize the command for debug macro replay.

        Subclasses return primitive values and marker constants that can be
        matched back to the active editor objects during replay.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        raise NotImplementedError("UndoCommand.export() is not implemented")

    @classmethod
    def from_data(cls, *args, **kwargs) -> "UndoCommand":
        """Rebuild a command from serialized macro data.

        Subclasses receive the active editor objects and the primitive payload
        returned by ``to_data``.

        Parameters
        ----------
        *args : object
            Additional positional arguments accepted by the operation.
        **kwargs : object
            Additional keyword arguments accepted by the operation.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        raise NotImplementedError("UndoCommand.import_data() is not implemented")


# TODO reference objects only by their index and don't keep references to them
# Only keep references to the level to be replaced?
class SetLevelAddressData(UndoCommand):
    """Change the ROM addresses attached to a level.

    Attached levels know where their object layout and enemy data live in the
    ROM. This command captures both old and new addresses so importing an M3L
    into ROM storage, detaching it, or changing its save target remains
    undoable.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose address metadata is changed.
    header_offset : int
        ROM offset for the level header.
    enemy_offset : int
        ROM enemy offset.

    Attributes
    ----------
    level : foundry.game.level.Level.Level
        Level whose address metadata is changed.
    new_enemy_offset : int
        Enemy data offset applied on redo.
    new_header_offset : int
        Level header/layout offset applied on redo.
    old_enemy_offset : int
        Enemy data offset restored on undo.
    old_header_offset : int
        Level header/layout offset restored on undo.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload
    [UndoCommand.MAGIC_VALUE_LEVEL, command.new_header_offset, command.new_enemy_offset]
    >>> payload[1:]
    [command.new_header_offset, command.new_enemy_offset]
    >>> replayed = SetLevelAddressData.from_data(level, *payload[1:])
    >>> replayed.to_data() == payload
    True
    """

    def __init__(self, level: Level, header_offset: int, enemy_offset: int):
        """Capture old and new ROM addresses for a level.

        The command snapshots the addresses currently attached to the level and
        stages the replacement pair that redo will apply. That keeps one undo
        record responsible for the full "this level now lives at these ROM
        offsets" transition used by attach, detach, and save workflows.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose address metadata is changed.
        header_offset : int
            ROM offset for the level header.
        enemy_offset : int
            ROM enemy offset.
        """
        super(SetLevelAddressData, self).__init__(None)

        self.level = level

        self.old_header_offset = self.level.header_offset
        self.old_enemy_offset = self.level.enemy_offset

        self.new_header_offset = header_offset
        self.new_enemy_offset = enemy_offset

        self.setText(f"Save Level to {self.new_header_offset:#x} and {self.new_enemy_offset:#x}")

    def undo(self):
        """Restore the previous level and enemy offsets."""
        self.level.set_addresses(self.old_header_offset, self.old_enemy_offset)

    def redo(self):
        """Apply the new level and enemy offsets."""
        self.level.set_addresses(self.new_header_offset, self.new_enemy_offset)

    def to_data(self) -> list:
        """Serialize the new address pair for macro replay.

        Replay resolves the active ``Level`` separately, so the payload only
        needs the destination addresses that should be re-applied to that live
        model.

        Returns
        -------
        list
            Serialized undo history data for this command.

        Examples
        --------
        >>> command.to_data()[1:]
        [command.new_header_offset, command.new_enemy_offset]
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.new_header_offset, self.new_enemy_offset]

    @classmethod
    def from_data(cls, level: Level, header_offset: int, enemy_offset: int) -> "UndoCommand":
        """Rebuild an address-change command from macro data.

        The replay path injects the live ``Level`` instance and restores the
        address pair captured by ``to_data`` so the same storage-target edit
        can be reproduced against the session being replayed.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Active level receiving the address change.
        header_offset : int
            ROM offset for the level header.
        enemy_offset : int
            ROM enemy offset.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.
        """
        return cls(level, header_offset, enemy_offset)


class AttachLevelToRom(SetLevelAddressData):
    """Attach a detached level to ROM object and enemy addresses.

    M3L import and attach workflows turn an in-memory level back into a ROM-
    backed level by assigning header and enemy addresses. This specialization
    keeps that state change undoable while exposing command text that matches
    the editor workflow more clearly than the generic address command.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Detached level being attached to ROM storage.
    header_offset : int
        ROM offset for the level header.
    enemy_offset : int
        ROM enemy offset.
    """

    def __init__(self, level: Level, header_offset: int, enemy_offset: int):
        """Capture the ROM addresses used to attach the level.

        This is the undoable boundary between detached in-memory level data and
        ROM-backed storage. Once pushed, the same level can move into a ROM
        slot without losing a reversible record of where it was attached.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Detached level being attached to ROM storage.
        header_offset : int
            ROM offset for the level header.
        enemy_offset : int
            ROM enemy offset.
        """
        super(AttachLevelToRom, self).__init__(level, header_offset, enemy_offset)

        self.setText(f"Attach Level to {self.new_header_offset:#x} and {self.new_enemy_offset:#x}")


class DetachLevelFromRom(SetLevelAddressData):
    """Clear the ROM addresses attached to a level.

    Detaching sets both address fields to zero through the same undoable address
    mechanism used for attachment. Foundry uses this when a level should remain
    editable as standalone data instead of writing back into a ROM slot. In
    practice that makes ROM-backed and detached M3L editing share the same undo
    boundary for attachment state.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose address metadata is cleared.
    """

    def __init__(self, level: Level):
        """Capture a detach operation for a level.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose address metadata is cleared.
        """
        super(DetachLevelFromRom, self).__init__(level, 0x0, 0x0)

        self.setText("Detach Level from Rom")


class SetLevelAttribute(UndoCommand):
    """Undo a single ``LevelRef`` attribute change.

    Header and level-setting dialogs can emit many small edits while a user
    cycles values. This command records the target attribute name and values,
    then allows Qt to merge repeated edits to the same attribute into one undo
    step. The value is applied through ``LevelRef.level`` so reloads that swap
    the underlying ``Level`` still target the active model. That merge behavior
    is what keeps spinner, combo-box, and staged-settings interactions from
    flooding the undo stack with one entry per intermediate value while still
    letting dialogs commit a meaningful final state change.

    Parameters
    ----------
    level : LevelRef
        Reference that owns the edited level instance.
    name : str
        Attribute name on the active level.
    new_value : Any
        Replacement setting value.
    display_name : str, optional
        Human-readable command label prefix.
    display_value : str, optional
        Display text shown in the UI.

    Attributes
    ----------
    level_ref : LevelRef
        Reference that owns the edited level instance.
    name : str
        Attribute name restored or applied by the command.
    new_value : Any
        Value applied on redo.
    old_value : Any
        Value restored on undo.

    Examples
    --------
    Replay stores the attribute name and replacement value, then rebuilds the
    command against the active ``LevelRef`` later.

    >>> payload = command.to_data()
    >>> payload[1]
    'music_index'

    Successive edits to the same attribute merge into one undo step.

    >>> command.id()
    121
    >>> command.to_data()[1:] == [command.name, command.new_value, command.text()]
    True
    """

    def __init__(self, level: LevelRef, name: str, new_value, display_name="", display_value=""):
        """Capture the level attribute edit.

        The old value is read from the active level when the command is
        created. Redo refreshes it before applying the new value because Qt
        calls ``redo`` immediately when a command is pushed, which keeps the
        command aligned with mergeable spinner and combo-box edits. That
        capture-and-refresh pattern is what lets one command safely represent a
        staged settings change even when the dialog emits several intermediate
        widget values before the user is done. In undo-stack terms the
        constructor snapshots the attribute boundary, the pre-edit value, and
        the user-facing label that later merge, replay, undo, and redo steps
        all reuse for one logical settings transaction.

        Parameters
        ----------
        level : LevelRef
            Reference that owns the edited level instance.
        name : str
            Attribute name on the active level.
        new_value : Any
            Replacement setting value.
        display_name : str, optional
            Human-readable command label prefix.
        display_value : str, optional
            Display text shown in the UI.
        """
        super(SetLevelAttribute, self).__init__(None)

        self.level_ref = level

        self.name = name
        self.old_value = getattr(level, name)
        self.new_value = new_value

        if not display_name:
            display_name = f"Level {' '.join(name.split('_')).capitalize()}"

        if not display_value:
            display_value = str(new_value)

        self.setText(f"{display_name} to {display_value}")

    def undo(self):
        """Restore the previous attribute value."""
        setattr(self.level_ref.level, self.name, self.old_value)

    def redo(self):
        """Apply the new attribute value to the edited level."""
        self.old_value = getattr(self.level_ref.level, self.name)
        setattr(self.level_ref.level, self.name, self.new_value)

    def id(self):
        """Qt merge identifier for mergeable level-attribute edits.

        Matching ids let Qt ask ``mergeWith`` whether successive spinner or
        combo-box edits belong to one undo step. All attribute edits share this
        id because ``mergeWith`` applies the real boundary: only edits to the
        same attribute may collapse into one command.

        Returns
        -------
        int
            Undo command identifier used by Qt.
        """
        return 121

    def mergeWith(self, other):
        """Merge another edit to the same level attribute.

        Only the final value and command label are kept, which makes repeated
        spinner or combo-box changes undo as one user action instead of a stack
        entry per intermediate value. This is what makes level-setting widgets
        feel staged instead of chatty even though Qt pushes a command for each
        intermediate widget change. In command-system terms, ``mergeWith``
        defines the user-visible transaction boundary for one attribute.

        Parameters
        ----------
        other : QUndoCommand
            Candidate command supplied by Qt.

        Returns
        -------
        bool
            True when the command merged with the other command.
        """
        if not isinstance(other, SetLevelAttribute):
            return False

        if self.name != other.name:
            return False

        self.new_value = other.new_value

        self.setText(other.text())

        return True

    def to_data(self) -> list:
        """Serialize the attribute edit for debug macro replay.

        The active ``LevelRef`` is represented by a marker because replay
        receives the active editor model separately and resolves it at replay
        time.

        Returns
        -------
        list
            Serialized undo history data for this command.

        Examples
        --------
        >>> command.to_data()[1:]
        ['music_index', 3, command.text()]
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.name, self.new_value, self.text()]

    @classmethod
    def from_data(cls, level: LevelRef, attr_name: str, new_value, text: str) -> "UndoCommand":
        """Rebuild a level attribute command from macro data.

        Replay restores the command text too, so the debug macro history reads
        the same way as the original undo stack.

        Parameters
        ----------
        level : LevelRef
            Edited level reference used during replay.
        attr_name : str
            Attribute name on the active level.
        new_value : Any
            Replacement setting value.
        text : str
            Command text restored into the undo stack.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.

        Examples
        --------
        >>> replayed = SetLevelAttribute.from_data(level_ref, 'music_index', 3, 'Level Music to 3')
        >>> replayed.name
        'music_index'
        """
        command = cls(level, attr_name, new_value)

        command.setText(text)

        return command


class SetNextAreaObjectAddress(SetLevelAttribute):
    """Change the object data address for the next area.

    SMB3 level headers can point to another area. This command updates the
    object-layout address portion of that pointer through the mergeable level
    attribute command base, so repeated edits from the header UI still collapse
    into one undoable next-area change while preserving the cross-area pointer
    that SMB3 follows when the player exits the source room. In architectural
    terms this is the command-pattern wrapper around one field in the next-area
    header tuple: dialogs can stage repeated pointer edits, while the undo
    stack records one meaningful navigation change instead of every spinner
    tick. It also preserves the hot-swap-friendly command shape used
    throughout this module: the undo stack stores a value on ``LevelRef``
    rather than a fragile reference to a destination-area object that could be
    rebuilt after reload.

    Parameters
    ----------
    level_ref : LevelRef
        Reference to the edited level.
    new_address : int
        Object data address for the next area.
    """

    def __init__(self, level_ref: LevelRef, new_address: int):
        """Capture a next-area object address edit.

        The constructor records the replacement object-stream address that will
        become part of the destination-area pointer. That keeps the header
        editor's pointer staging inside the same mergeable undo flow as other
        level attribute edits.

        Parameters
        ----------
        level_ref : LevelRef
            Reference to the edited level.
        new_address : int
            Object data address for the next area.
        """
        super(SetNextAreaObjectAddress, self).__init__(level_ref, "next_area_objects", new_address)

        self.setText(f"Object Address of Next Area to {new_address:#x}")


class SetNextAreaEnemyAddress(SetLevelAttribute):
    """Change the enemy data address for the next area.

    SMB3 level headers can point to another area. This command updates the
    enemy-data address portion of that pointer through the mergeable level
    attribute command base, so repeated edits from the header UI still collapse
    into one undoable next-area change while preserving the enemy stream paired
    with the destination area. The command exists separately from the object
    address edit because SMB3 stores the two streams independently, and editor
    workflows sometimes need to correct one side of the destination pointer
    without rebuilding the entire next-area configuration.

    Parameters
    ----------
    level_ref : LevelRef
        Reference to the edited level.
    new_address : int
        Enemy data address for the next area.
    """

    def __init__(self, level_ref: LevelRef, new_address: int):
        """Capture a next-area enemy address edit.

        The constructor records the replacement enemy-stream address that pairs
        with the destination area. This preserves the enemy half of the
        next-area pointer as its own reversible edit while still sharing the
        mergeable header-setting workflow of the base command.

        Parameters
        ----------
        level_ref : LevelRef
            Reference to the edited level.
        new_address : int
            Enemy data address for the next area.
        """
        super(SetNextAreaEnemyAddress, self).__init__(level_ref, "next_area_enemies", new_address)

        self.setText(f"Enemy Address of Next Area to {new_address:#x}")


class SetNextAreaObjectSet(SetLevelAttribute):
    """Change the object set used by the next area.

    The next-area object set controls how the target area's object bytes are
    interpreted and rendered. Routing the edit through ``SetLevelAttribute``
    keeps rapid cycling in the header UI merged into one undo step while
    documenting that the pointer change also changes how the destination bytes
    should be decoded. This makes the command part of the same next-area
    navigation story as the address fields: the destination pointer is not
    complete unless the editor also knows which SMB3 object set should decode
    the referenced bytes. In other words, this command updates the schema for
    the destination area, not just a display preference, which is why it lives
    beside the pointer-address commands in the undo layer.

    Parameters
    ----------
    level_ref : LevelRef
        Reference to the edited level.
    new_object_set : int
        Object set index for the next area.

    Notes
    -----
    Foundry keeps this separate from the destination addresses because the next
    area's object set is effectively part of that area's decoding contract. A
    wrong value changes how the referenced bytes expand into objects, geometry,
    and graphics expectations.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload[1]
    'next_area_object_set_no'
    >>> payload[2] == command.new_value
    True
    """

    def __init__(self, level_ref: LevelRef, new_object_set: int):
        """Capture a next-area object-set edit.

        The constructor stores the object-set number that will control how the
        destination area's bytes are decoded after the pointer is followed, so
        the undo stack records both navigation metadata and decoding metadata
        as part of the same next-area editing workflow.

        Parameters
        ----------
        level_ref : LevelRef
            Reference to the edited level.
        new_object_set : int
            Object set index for the next area.
        """
        super(SetNextAreaObjectSet, self).__init__(level_ref, "next_area_object_set_no", new_object_set)

        self.setText(f"Object Set of Next Area to {OBJECT_SET_NAMES[new_object_set]}")


class ChangeLockIndex(UndoCommand):
    """Change which lock an enemy-triggered lock event breaks.

    Some SMB3 enemy entries carry a lock index used by boom-boom/lock-style
    level settings. The command stores the enemy list index so the edit can be
    replayed after level objects are rebuilt from ROM data.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level containing the enemy to update.
    enemy_index : int
        Index of the enemy in ``level.enemies``.
    new_lock_index : int
        Lock index to apply on redo.

    Attributes
    ----------
    enemy_index : int
        Index of the enemy in ``level.enemies``.
    level : foundry.game.level.Level.Level
        Level containing the enemy to update.
    new_lock_index : int
        Lock index applied on redo.
    old_index : int
        Lock index restored on undo.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload
    [UndoCommand.MAGIC_VALUE_LEVEL, command.enemy_index, command.new_lock_index]
    >>> payload[1:]
    [command.enemy_index, command.new_lock_index]
    >>> replayed = ChangeLockIndex.from_data(level, *payload[1:])
    >>> replayed.to_data() == payload
    True
    """

    def __init__(self, level: Level, enemy_index: int, new_lock_index: int):
        """Capture the target enemy and replacement lock index.

        The command snapshots which enemy entry is being edited and the lock
        index that should replace the existing one. That keeps the level
        settings workflow reversible even though the actual lock behavior lives
        on an enemy record embedded in the level data.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level containing the enemy to update.
        enemy_index : int
            Index of the enemy in ``level.enemies``.
        new_lock_index : int
            Lock index to apply on redo.
        """
        super(ChangeLockIndex, self).__init__(None)

        self.level = level
        self.enemy_index = enemy_index
        self.old_index = 0

        self.new_lock_index = new_lock_index

        enemy = self.level.enemies[self.enemy_index]
        self.setText(f"Set {enemy.name} to break Lock #{new_lock_index}")

    def undo(self):
        """Restore the enemy's previous lock index."""
        enemy = self.level.enemies[self.enemy_index]
        enemy.lock_index = self.old_index

    def redo(self):
        """Apply the new lock index to the target enemy."""
        enemy = self.level.enemies[self.enemy_index]
        self.old_index = enemy.lock_index

        enemy.lock_index = self.new_lock_index

    def to_data(self) -> list:
        """Serialize the enemy index and new lock index.

        Replay resolves the enemy from the level's enemy list and reapplies the
        lock index change, so the payload only needs the target index and the
        replacement value.

        Returns
        -------
        list
            Serialized undo history data for this command.

        Examples
        --------
        >>> command.to_data()[1:]
        [command.enemy_index, command.new_lock_index]
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.enemy_index, self.new_lock_index]

    @classmethod
    def from_data(cls, level: Level, enemy_index: int, new_lock_index: int) -> "UndoCommand":
        """Rebuild a lock-index command from macro data.

        The replay path injects the live level and reuses the constructor so
        the command rebuilds the same enemy-targeted edit that originally
        entered the undo stack.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level containing the enemy to update.
        enemy_index : int
            Index of the enemy in ``level.enemies``.
        new_lock_index : int
            Lock index to apply on redo.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.
        """
        return cls(level, enemy_index, new_lock_index)


class UpdatePalette(UndoCommand):
    """Change one color entry in the active object palette group.

    Palette edits are global ROM data, but the active level determines which
    object palette group is loaded. The command captures the palette indexes,
    reloads level graphics after each change, and restores the previous global
    dirty flag on undo.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose object set and palette index select the palette group.
    index_in_group : int
        Palette index inside the group.
    index_in_palette : int
        Color index inside the selected palette.
    new_color_index : int
        Index of the new color.

    Attributes
    ----------
    index_in_group : int
        Palette index inside the group.
    index_in_palette : int
        Color index inside the selected palette.
    level : foundry.game.level.Level.Level
        Level whose graphics are reloaded after palette changes.
    new_color_index : int
        NES palette color index applied on redo.
    old_color_index : int
        NES palette color index restored on undo.
    palette_group : PaletteGroup
        Palette group selected from the active level.
    palette_was_changed : bool
        Previous global palette dirty state restored on undo.

    Examples
    --------
    Palette edits serialize the palette slot and replacement color so macro
    replay can rebuild the command against the active level.

    >>> payload = command.to_data()
    >>> payload
    [
    ...     UndoCommand.MAGIC_VALUE_LEVEL,
    ...     command.index_in_group,
    ...     command.index_in_palette,
    ...     command.new_color_index,
    ... ]
    >>> replayed = UpdatePalette.from_data(level, *payload[1:])
    >>> replayed.to_data() == payload
    True
    """

    def __init__(
        self,
        level,
        index_in_group: int,
        index_in_palette: int,
        new_color_index: int,
    ):
        """Capture a palette color edit.

        The command snapshots which palette entry should change and preserves
        the pre-edit global dirty flag so undo can restore both the ROM-backed
        color value and the editor's palette-changed bookkeeping. That staged
        state is what lets the palette viewer push one reversible command while
        level graphics are reloaded around each redo or undo.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object set and palette index select the palette group.
        index_in_group : int
            Palette index inside the group.
        index_in_palette : int
            Color index inside the selected palette.
        new_color_index : int
            Index of the new color.
        """
        super(UpdatePalette, self).__init__("Change Palette Color", None)

        self.level = level

        self.palette_group = load_palette_group(level.object_set_number, level.object_palette_index)
        self.index_in_group = index_in_group

        self.palette_was_changed = PaletteGroup.changed

        self.index_in_palette = index_in_palette

        self.old_color_index = 0
        self.new_color_index = new_color_index

    def undo(self):
        """Restore the previous palette color and dirty flag."""
        change_color(
            self.palette_group,
            self.index_in_group,
            self.index_in_palette,
            self.old_color_index,
        )

        self.level.reload()
        PaletteGroup.changed = self.palette_was_changed

    def redo(self):
        """Apply the new palette color and reload level graphics."""
        self.palette_group = load_palette_group(self.level.object_set_number, self.level.object_palette_index)
        self.old_color_index = self.palette_group[self.index_in_group][self.index_in_palette]

        change_color(
            self.palette_group,
            self.index_in_group,
            self.index_in_palette,
            self.new_color_index,
        )

        self.level.reload()
        PaletteGroup.changed = True

    def to_data(self) -> list:
        """Serialize the palette edit for debug macro replay.

        Replay does not persist the loaded ``PaletteGroup`` instance. Instead
        it rebuilds the command from the active level plus the palette-group
        index, the in-palette color index, and the replacement color, which is
        enough to reproduce the same ROM-backed color edit later.

        Returns
        -------
        list
            Serialized undo history data for this command.

        Examples
        --------
        >>> command.to_data()[1:]
        [command.index_in_group, command.index_in_palette, command.new_color_index]
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.index_in_group, self.index_in_palette, self.new_color_index]

    @classmethod
    def from_data(cls, level: Level, index_in_group: int, index_in_palette: int, new_color_index: int) -> "UndoCommand":
        """Rebuild a palette update command from replay data.

        Macro replay injects the active level and restores the palette slot
        coordinates plus the replacement color. The command then re-resolves
        the live palette group from that level so replay follows the same
        reload-aware palette-edit path as the original undo-stack entry.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object set and palette index select the palette group.
        index_in_group : int
            Palette index inside the group.
        index_in_palette : int
            Color index inside the selected palette.
        new_color_index : int
            Index of the new color.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.

        Examples
        --------
        >>> replayed = UpdatePalette.from_data(level, 0, 2, 15)
        >>> replayed.index_in_group, replayed.index_in_palette
        (0, 2)
        """
        return cls(level, index_in_group, index_in_palette, new_color_index)


class MoveObjects(UndoCommand):
    """Commit a visual drag as an undoable position change.

    ``LevelView`` moves objects interactively before this command is pushed, so
    the command cannot discover the original positions from the live level.
    Callers provide snapshots from before and after the drag; the command stores
    indexes into the level object and enemy lists plus tile coordinates. That
    keeps movement undoable after ROM hot swap rebuilds the object instances, as
    long as the object ordering still matches the reloaded level.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose object and enemy lists receive the position updates.
    objects_before : list[InLevelObject]
        Moved objects captured before the visual drag was committed.
    objects_after : list[InLevelObject]
        Moved objects captured at their final drag positions.

    Attributes
    ----------
    level : foundry.game.level.Level.Level
        Level whose object and enemy lists receive the position updates.
    """

    def __init__(
        self,
        level: Level,
        objects_before: list[InLevelObject],
        objects_after: list[InLevelObject],
    ):
        """Capture before-and-after positions for moved objects.

        The constructor immediately calls ``undo`` because the view has already
        applied the visual move by the time the command is pushed.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object and enemy lists receive the position updates.
        objects_before : list[InLevelObject]
            Moved objects captured before the visual drag was committed.
        objects_after : list[InLevelObject]
            Moved objects captured at their final drag positions.
        """
        super(MoveObjects, self).__init__(None)

        self.level = level

        indexed_lo_before, indexed_lo_after, indexed_en_before, indexed_en_after = separate_and_index_objects(
            level, objects_before, objects_after
        )

        # !!! remember old positions for each, this data does not exist in the current level, so we cannot get this
        # !!! information in undo(), but it should not be affected by a level change
        self.level_object_before_positions, self.enemy_item_before_positions = self._get_separate_indexed_positions(
            indexed_lo_before, indexed_en_before
        )

        # remember new positions for each, index in level to old position
        self.level_object_after_positions, self.enemy_item_after_positions = self._get_separate_indexed_positions(
            indexed_lo_after, indexed_en_after
        )

        self.setText(f"Move {object_names(objects_after)}")

        # undo once, because we visually already moved them
        self.undo()

    @staticmethod
    def _get_separate_indexed_positions(
        indexed_level_objects: list[tuple[int, InLevelObject]],
        indexed_enemy_items: list[tuple[int, InLevelObject]],
    ):
        # make a dictionary of the indexes and positions of the given objects
        """Build replay-ready position maps for level objects and enemies.

        ``MoveObjects`` snapshots positions before and after a drag, then
        serializes those snapshots by list index instead of by Python object
        identity. Splitting the dictionaries here preserves SMB3's separate
        object and enemy streams while giving undo, redo, and macro replay a
        stable way to target the live lists after the view has already moved
        the objects on screen.

        Parameters
        ----------
        indexed_level_objects : list[tuple[int, InLevelObject]]
            Indexed level objects consumed by the operation.
        indexed_enemy_items : list[tuple[int, InLevelObject]]
            Indexed enemy items consumed by the operation.

        Returns
        -------
        tuple[dict[int, tuple[int, int]], dict[int, tuple[int, int]]]
            Level-object positions and enemy positions keyed by list index.
        """
        indexed_level_object_positions: dict[int, tuple[int, int]] = {
            index: old_level_object.get_position() for index, old_level_object in indexed_level_objects
        }
        indexed_enemy_item_positions: dict[int, tuple[int, int]] = {
            index: old_enemy_item.get_position() for index, old_enemy_item in indexed_enemy_items
        }

        return indexed_level_object_positions, indexed_enemy_item_positions

    def undo(self):
        """Restore all moved objects to their pre-drag positions."""
        self._apply_positions(self.level_object_before_positions, self.enemy_item_before_positions)

        self.level.data_changed.emit()

    def redo(self):
        """Apply all moved objects to their committed drag positions."""
        self._apply_positions(self.level_object_after_positions, self.enemy_item_after_positions)

        self.level.data_changed.emit()

    def to_data(self):
        """Serialize indexed before-and-after positions.

        Macro replay restores positions by index instead of requiring the
        original Python object identities.

        Returns
        -------
        list
            Serialized command payload.
        """
        return [
            UndoCommand.MAGIC_VALUE_LEVEL,
            self.level_object_before_positions,
            self.level_object_after_positions,
            self.enemy_item_before_positions,
            self.enemy_item_after_positions,
        ]

    @classmethod
    def from_data(cls, level, objects_before, objects_after, enemies_before, enemies_after):
        """Rebuild a movement command from indexed position data.

        Macro replay injects the live ``Level`` and restores the four index
        maps that were captured when the drag was first committed. The command
        creates an empty shell, then replaces its temporary snapshots with the
        serialized payload so redo and undo can drive the same index-based move
        path without needing the original object instances.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object and enemy lists receive the position updates.
        objects_before : dict[int, tuple[int, int]]
            Pre-drag level-object positions keyed by object index.
        objects_after : dict[int, tuple[int, int]]
            Final level-object positions keyed by object index.
        enemies_before : dict[int, tuple[int, int]]
            Pre-drag enemy positions keyed by enemy index.
        enemies_after : dict[int, tuple[int, int]]
            Final enemy positions keyed by enemy index.

        Returns
        -------
        MoveObjects
            Command restored from serialized undo history data.

        Examples
        --------
        >>> payload = command.to_data()
        >>> replayed = MoveObjects.from_data(level, *payload[1:])
        >>> replayed.level_object_after_positions == command.level_object_after_positions
        True
        """
        command = cls(level, [], [])

        command.level_object_before_positions = objects_before
        command.level_object_after_positions = objects_after

        command.enemy_item_before_positions = enemies_before
        command.enemy_item_after_positions = enemies_after

        return command

    def _apply_positions(self, level_positions, enemy_positions):
        # get level object in level by index
        """Apply indexed positions to the live level objects.

        Undo, redo, and macro replay all converge here. The command resolves
        each stored index back into the level's current object or enemy list,
        then writes the captured tile coordinate into that live instance. Using
        the shared helper keeps the before/after replay path consistent and
        makes the hot-reload assumption explicit: object ordering must still
        match the serialized indexes.

        Parameters
        ----------
        level_positions : dict[int, tuple[int, int]]
            Level-object positions keyed by object index.
        enemy_positions : dict[int, tuple[int, int]]
            Enemy positions keyed by enemy index.
        """
        for index, position in level_positions.items():
            level_object = self.level.objects[index]
            level_object.set_position(*position)

        for index, position in enemy_positions.items():
            enemy_item = self.level.enemies[index]
            enemy_item.set_position(*position)


class MoveObject(MoveObjects):
    """Move one in-level object through the bulk movement command path.

    The single-object variant exists for call sites that already have one
    object snapshot before and after a drag or nudge. Reusing
    ``MoveObjects`` keeps index-based replay and hot-reload resilience
    consistent with multi-object moves.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose object and enemy lists receive the position updates.
    object_before : InLevelObject
        Snapshot of the object before the move.
    object_after : InLevelObject
        Snapshot of the object after the move.
    """

    def __init__(self, level: Level, object_before: InLevelObject, object_after: InLevelObject):
        """Capture one object's movement snapshots.

        This thin wrapper exists for callers that already have one object pair
        and still need the same undo-stack staging as bulk moves. It forwards
        the snapshots through ``MoveObjects`` so the command is recorded,
        reverted once, and later replayed with the same index-based movement
        path as a multi-selection drag.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object and enemy lists receive the position updates.
        object_before : InLevelObject
            Snapshot of the object before the move.
        object_after : InLevelObject
            Snapshot of the object after the move.
        """
        super().__init__(level, [object_before], [object_after])


class ResizeObjects(UndoCommand):
    """Undo and redo SMB3 object-byte changes caused by resizing.

    Resizing changes the encoded bytes for level objects rather than just their
    coordinates. The command stores object indexes plus serialized object data
    from before and after the edit, then rebuilds each live object with
    ``_setup`` when replaying the change. Enemies are excluded because SMB3
    enemy/item records do not share the same resize path.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose object list is mutated.
    objects_before : list[InLevelObject]
        Object snapshots captured before resizing.
    objects_after : list[InLevelObject]
        Object snapshots captured after resizing.

    Attributes
    ----------
    level : foundry.game.level.Level.Level
        Level whose object list is mutated.
    object_data_after : list[tuple[int, bytes]]
        Serialized object bytes applied on redo, keyed by object index.
    object_data_before : list[tuple[int, bytes]]
        Serialized object bytes restored on undo, keyed by object index.

    Examples
    --------
    >>> payload = command.to_data()
    >>> replayed = ResizeObjects.from_data(level, *payload[1:])
    >>> replayed.object_data_after == command.object_data_after
    True
    """

    def __init__(
        self,
        level: Level,
        objects_before: list[InLevelObject],
        objects_after: list[InLevelObject],
    ):
        """Capture object bytes before and after a resize operation.

        The editor has already applied the resize visually before the command
        is pushed. The constructor therefore snapshots the encoded object bytes,
        stores them by list index, and immediately calls ``undo`` so the undo
        stack owns the transition between pre-resize and post-resize object
        layouts. Later redo and macro replay rebuild object state from these
        bytes instead of trying to infer size changes from the live objects.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object list is mutated.
        objects_before : list[InLevelObject]
            Objects before consumed by the operation.
        objects_after : list[InLevelObject]
            Objects after consumed by the operation.
        """
        super(ResizeObjects, self).__init__(None)

        self.level = level

        # ignore enemies/items because they can't be resized
        indexed_lo_before, indexed_lo_after, *_ = separate_and_index_objects(level, objects_before, objects_after)

        self.object_data_before: list[tuple[int, bytes]] = [
            (index, bytes(obj.to_bytes())) for index, obj in indexed_lo_before
        ]
        self.object_data_after: list[tuple[int, bytes]] = [
            (index, bytes(obj.to_bytes())) for index, obj in indexed_lo_after
        ]

        self.setText(f"Resize {object_names(objects_after)}")

        # objects are already resized; undo so the undo stack can redo it, when pushed
        self.undo()

    def undo(self):
        """Restore each resized object's previous encoded byte data."""
        for index, data in self.object_data_before:
            obj = self.level.objects[index]
            obj.data = bytearray(data)  # copy to not pass by reference

            obj._setup()

        self.level.data_changed.emit()

    def redo(self):
        """Apply each object's resized encoded byte data."""
        for index, data in self.object_data_after:
            obj = self.level.objects[index]
            obj.data = bytearray(data)  # copy to not pass by reference

            obj._setup()

        self.level.data_changed.emit()

    def to_data(self):
        """Serialize indexed object bytes for macro replay.

        Replay needs the exact before-and-after encoded object payloads because
        resizing changes SMB3 object bytes, not just the rectangle drawn in the
        editor. The serialized list therefore preserves the same byte snapshots
        that ``undo`` and ``redo`` feed back through ``_setup``.

        Returns
        -------
        list
            Marker plus before-and-after object-byte snapshots.
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.object_data_before, self.object_data_after]

    @classmethod
    def from_data(cls, level, objects_before, objects_after):
        """Rebuild a resize command from serialized object bytes.

        Macro replay injects the live ``Level`` and restores the previously
        captured byte snapshots. The command shell created here discards its
        temporary empty payloads and reuses the serialized before/after byte
        lists so replay rebuilds object state through the same ``_setup`` path
        as the original resize command.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object list is mutated.
        objects_before : list[tuple[int, bytes]]
            Serialized object bytes restored on undo.
        objects_after : list[tuple[int, bytes]]
            Serialized object bytes applied on redo.

        Returns
        -------
        ResizeObjects
            Command restored from serialized undo history data.

        Examples
        --------
        >>> payload = command.to_data()
        >>> replayed = ResizeObjects.from_data(level, *payload[1:])
        >>> replayed.object_data_before == command.object_data_before
        True
        """
        new_command = cls(level, [], [])

        new_command.object_data_before = objects_before
        new_command.object_data_after = objects_after

        return new_command


def objects_to_indexed_objects(level: Level, objects: list[InLevelObject]) -> list[tuple[int, InLevelObject]]:
    """Handle objects to indexed objects.

    It participates in the undo/redo command stream that keeps GUI edits reversible. The lookup centralizes coordinate or identifier handling for callers.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose ordering is mutated.
    objects : list[InLevelObject]
        Objects that should move later in draw order.

    Returns
    -------
    list[tuple[int, InLevelObject]]
        Objects paired with their original indexes.
    """
    indexes: list[tuple[int, InLevelObject]] = []

    for obj in objects:
        if isinstance(obj, LevelObject):
            index = level.objects.index(obj)

        else:
            assert isinstance(obj, EnemyItem), type(obj)
            index = level.enemies.index(obj)

        indexes.append((index, obj))

    indexes.sort(key=itemgetter(0))

    return indexes


def separate_and_index_objects(level: Level, objects_before: list[InLevelObject], objects_after: list[InLevelObject]):
    """Separate and index objects.

    It participates in the undo/redo command stream that keeps GUI edits reversible. The return value keeps undo serialization and command merging explicit for the command stack.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level model or level reference used by the operation.
    objects_before : list[InLevelObject]
        Objects before consumed by the operation.
    objects_after : list[InLevelObject]
        Objects after consumed by the operation.

    Returns
    -------
    Any
        Objects separated by domain and paired with indexes.
    """
    indexed_lo_before = []
    indexed_lo_after = []

    indexed_en_before = []
    indexed_en_after = []

    for obj_before, obj_after in zip(objects_before, objects_after):
        if isinstance(obj_before, LevelObject):
            assert isinstance(obj_after, LevelObject)
            index = level.objects.index(obj_after)

            indexed_lo_before.append((index, obj_before))
            indexed_lo_after.append((index, obj_after))
        else:
            assert isinstance(obj_after, EnemyItem)
            index = level.enemies.index(obj_after)

            indexed_en_before.append((index, obj_before))
            indexed_en_after.append((index, obj_after))

    return indexed_lo_before, indexed_lo_after, indexed_en_before, indexed_en_after


def move_objects(level: Level, indexed_objects: list[tuple[int, InLevelObject]], restore_only=False):
    """Move objects.

    It participates in the undo/redo command stream that keeps GUI edits reversible. The mutating operation keeps model state and dependent editor views in sync.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level model or level reference used by the operation.
    indexed_objects : list[tuple[int, InLevelObject]]
        Indexed objects consumed by the operation.
    restore_only : Any, optional
        Restore only used by the operation.
    """
    for index, obj in indexed_objects:
        if isinstance(obj, LevelObject):
            if not restore_only:
                level.objects.remove(obj)

            level.objects.insert(index, obj)

        else:
            assert isinstance(obj, EnemyItem)
            if not restore_only:
                level.enemies.remove(obj)

            level.enemies.insert(index, obj)


def object_names(objects: list[InLevelObject]) -> str:
    """Return names.

    It participates in the undo/redo command stream that keeps GUI edits reversible. The lookup centralizes coordinate or identifier handling for callers.

    Parameters
    ----------
    objects : list[InLevelObject]
        Objects being inspected or modified.

    Returns
    -------
    str
        Display names for the objects in the command.
    """
    amount = len(objects)

    if amount == 1:
        return f"'{objects[0].name}'"

    if objects and all(isinstance(obj, EnemyItem) for obj in objects):
        return f"{amount} enemies"
    else:
        return f"{amount} objects"


class ToForeground(UndoCommand):
    """Move selected objects later in draw order.

    SMB3 stores level objects and enemies/items in ordered lists, and Foundry
    uses that order to decide which objects draw in front of others. The
    command records the original list indexes so a foreground move can be
    undone even after the command refreshes object references from the live
    level.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose ordering is mutated.
    objects : list[InLevelObject]
        Objects that should move later in draw order.

    Attributes
    ----------
    indexes_before : list[tuple[int, InLevelObject]]
        Original level/enemy indexes for the moved objects.
    level : foundry.game.level.Level.Level
        Level whose ordering is mutated.
    objects : list[InLevelObject]
        Live object references refreshed from recorded indexes before redo.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload[0]
    UndoCommand.MAGIC_VALUE_LEVEL
    >>> replayed = ToForeground.from_data(level, payload[1])
    >>> replayed.indexes_before == command.indexes_before
    True
    """

    def __init__(self, level: Level, objects: list[InLevelObject]):
        """Capture the objects that should move to the foreground.

        The constructor records list indexes immediately because later undo,
        redo, or ROM reload may rebuild the live object instances that the
        selection originally pointed at.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose ordering is mutated.
        objects : list[InLevelObject]
            Objects that should move later in draw order.
        """
        super(ToForeground, self).__init__(None)

        self.level = level
        self.objects = objects

        self.indexes_before: list[tuple[int, InLevelObject]] = objects_to_indexed_objects(level, objects)

        self.setText(f"Bring {object_names(objects)} to the foreground")

    def undo(self):
        """Restore the original ordering for the moved objects."""
        move_objects(self.level, self.indexes_before)

        self.level.data_changed.emit()

    def redo(self):
        """Move the recorded objects to the front of their draw order."""
        self._update_object_refs()

        self.level.bring_to_foreground(self.objects)

        self.level.data_changed.emit()

    def _update_object_refs(self):
        # update object references with indexes
        """Refresh live object references from the stored indexes.

        Undo/redo and ROM reload can rebuild the underlying object instances,
        so redo resolves the live objects by index before it mutates order and
        refreshes the stored index snapshot.
        """
        self.objects.clear()

        for index, obj in self.indexes_before:
            if isinstance(obj, LevelObject):
                self.objects.append(self.level.objects[index])
            else:
                self.objects.append(self.level.enemies[index])

        self.indexes_before = objects_to_indexed_objects(self.level, self.objects)

    def to_data(self):
        """Serialize the original object ordering.

        Macro replay uses the stored list indexes rather than object instances,
        so the replayed command can resolve the affected objects inside the
        reloaded level before changing draw order.

        Returns
        -------
        list
            Marker plus the original object/enemy indexes.

        Examples
        --------
        >>> command.to_data()[0]
        UndoCommand.MAGIC_VALUE_LEVEL
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.indexes_before]

    @classmethod
    def from_data(cls, level, objects_before):
        """Rebuild a foreground-order command from stored indexes.

        The command starts with an empty live-object list and rehydrates it from
        the recorded indexes before redo mutates the level ordering.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose ordering is mutated.
        objects_before : list[tuple[int, InLevelObject]]
            Original level/enemy indexes for the moved objects.

        Returns
        -------
        ToForeground
            Command restored from serialized undo history data.
        """
        command = cls(level, [])

        command.indexes_before = objects_before

        return command


class ToBackground(ToForeground):
    """Move selected objects earlier in draw order.

    This reuses the same index-capture strategy as ``ToForeground`` but applies
    the inverse ordering change so selected objects render behind their former
    neighbors. Keeping it as a dedicated command gives menus and shortcuts a
    distinct undo label while preserving the same reload-safe bookkeeping.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose ordering is mutated.
    objects : list[InLevelObject]
        Objects that should move earlier in draw order.
    """

    def __init__(self, level: Level, objects: list[InLevelObject]):
        """Capture the objects that should move toward the background.

        The menu action fires after the selection already identifies the live
        objects to reorder. This constructor preserves those object references
        and the original indexes through the shared ``ToForeground`` staging
        path, then flips the stored order so redo can replay the inverse draw-
        order mutation while keeping undo-stack bookkeeping and reload-safe
        index capture identical to the foreground variant.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose ordering is mutated.
        objects : list[InLevelObject]
            Objects that should move earlier in draw order.
        """
        super(ToBackground, self).__init__(level, objects)

        self.indexes_before.reverse()

        self.setText(f"Put {object_names(objects)} in the background")

    def redo(self):
        """Move the recorded objects toward the back of their draw order."""
        self._update_object_refs()

        self.level.bring_to_background(self.objects)

        self.level.data_changed.emit()


class ImportASMEnemies(UndoCommand):
    """Import enemy data from an ASM file as one undoable operation.

    Foundry can rebuild a level's enemy stream from ASM output. The command
    snapshots the enemy bytes before import, lazily records the imported bytes
    on first redo, and then replays the change by reloading raw enemy data.
    That keeps the undo stack focused on the imported result instead of the
    parser's intermediate objects.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose enemy stream is replaced.
    path : PathLike
        ASM file read to produce replacement enemy data.

    Attributes
    ----------
    enemy_data_after : bytearray
        Imported enemy bytes applied on redo.
    enemy_data_before : bytearray
        Original enemy bytes restored on undo.
    level : foundry.game.level.Level.Level
        Level whose enemy stream is replaced.
    path : PathLike
        Source ASM file used to produce enemy data.

    Examples
    --------
    >>> replayed = ImportASMEnemies.from_data(level, "enemy_script.asm")
    >>> replayed.to_data()
    [UndoCommand.MAGIC_VALUE_LEVEL, 'enemy_script.asm']
    """

    def __init__(self, level: Level, path: PathLike):
        """Capture the source file and initialize byte snapshots.

        The command is created before any ASM import work mutates the level.
        It therefore records the import source, leaves both byte snapshots
        empty, and defers reading the existing and imported enemy streams until
        ``redo`` runs. That staging keeps the undo stack responsible for the
        import transition instead of the caller that opened the file chooser.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose enemy stream is replaced.
        path : PathLike
            ASM file read to produce replacement enemy data.
        """
        super(ImportASMEnemies, self).__init__(None)

        self.level = level

        self.path = path

        self.enemy_data_before = bytearray()
        self.enemy_data_after = bytearray()

        self.setText(f"Importing Enemies from {Path(path).name}")

    def undo(self):
        """Restore the enemy bytes that were present before import."""
        self.level._load_enemies(self.enemy_data_before)

        self.level.data_changed.emit()

    def redo(self):
        """Import or reapply the ASM-derived enemy bytes."""
        _, (_, self.enemy_data_before) = self.level.to_bytes()

        if not self.enemy_data_after:
            load_asm_enemy(self.path, self.level)

            _, (_, self.enemy_data_after) = self.level.to_bytes()

        self.level._load_enemies(self.enemy_data_after)

        self.level.data_changed.emit()

    def to_data(self):
        """Serialize the ASM source path for macro replay.

        Replay re-runs the import from the source file instead of embedding the
        imported enemy bytes in the undo payload. Persisting only the path keeps
        the serialized command small while still preserving the information
        needed to repeat the same import workflow later.

        Returns
        -------
        list
            Marker plus the ASM file path.
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, str(self.path)]

    @classmethod
    def from_data(cls, level, path_str):
        """Rebuild an ASM import command from a stored file path.

        Macro replay injects the live ``Level`` and reuses the serialized ASM
        path so ``redo`` can reload the enemy stream through the same import
        boundary as the original command. The byte snapshots are intentionally
        left to redo-time because they depend on the level state that exists
        when replay reaches this command.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose enemy stream is replaced.
        path_str : str
            Serialized ASM path captured by ``to_data``.

        Returns
        -------
        ImportASMEnemies
            Command restored from serialized undo history data.

        Examples
        --------
        >>> command = ImportASMEnemies.from_data(level, "enemy_script.asm")
        >>> command.path.name
        'enemy_script.asm'
        """
        command = cls(level, Path(path_str))

        return command


class AddLevelObjectAt(UndoCommand):
    """Add a level object at a view position.

    The command converts the Qt pixel position to a level coordinate at
    creation time. Storing the level coordinate keeps replay and undo stable if
    the user changes zoom before the command is undone or redone.

    Parameters
    ----------
    level_view : 'LevelView'
        Level view controlled by the menu action.
    pos : QPoint
        View-space position where the object was placed.
    domain : int, optional
        Object domain that determines how the object is interpreted.
    obj_type : int, optional
        Object type identifier to place.
    length : int | None, optional
        Object length value.
    index : int, optional
        Zero-based index of the item to access.
    selected : bool, optional
        Whether the object should be drawn as selected.

    Attributes
    ----------
    domain : int
        SMB3 object domain passed to ``Level.add_object``.
    index : int
        Index where the object is inserted or later removed.
    length : int | None
        Optional object length passed to the level factory.
    level : LevelRef
        Active level reference reached through the view.
    level_point : Position
        Level-space coordinate captured from the original view position.
    obj_type : int
        SMB3 object type passed to ``Level.add_object``.
    view : LevelView
        View used to convert from Qt coordinates to level coordinates.
    was_selected : bool
        Selection state applied to the new object.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload
    [
    ...     UndoCommand.MAGIC_VALUE_LEVEL_VIEW,
    ...     command.level_point.xy,
    ...     command.domain,
    ...     command.obj_type,
    ...     command.length,
    ...     command.index,
    ...     command.was_selected,
    ... ]
    >>> replayed = AddLevelObjectAt.from_data(level_view, *payload[1:])
    >>> replayed.level_point == command.level_point
    True
    >>> replayed.to_data() == payload
    True
    """

    def __init__(
        self,
        level_view: "LevelView",
        pos: QPoint,
        domain=0,
        obj_type=0,
        length: int | None = None,
        index=-1,
        selected=False,
    ):
        """Capture the placement request.

        The placement point is converted immediately so the command is not
        coupled to the view zoom when it later replays.

        Parameters
        ----------
        level_view : 'LevelView'
            Level view controlled by the menu action.
        pos : QPoint
            View-space position where the object was placed.
        domain : int, optional
            Object domain that determines how the object is interpreted.
        obj_type : int, optional
            Object type identifier to place.
        length : int | None, optional
            Object length value.
        index : int, optional
            Zero-based index of the item to access.
        selected : bool, optional
            Whether the object should be drawn as selected.
        """
        super(AddLevelObjectAt, self).__init__(None)

        self.view = level_view
        self.level = level_view.level_ref

        # convert here, in case there's a zoom change happening between undo and redo
        # TODO why not just take the level point as an argument?
        self.level_point = level_view.to_level_point(pos)

        self.domain = domain
        self.obj_type = obj_type
        self.length = length

        self.index = index

        self.was_selected = selected

    def undo(self):
        """Remove the object inserted by ``redo``."""
        self.level.objects.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        """Insert the object and remember its resolved index."""
        added_object = self.level.add_object(self.domain, self.obj_type, self.level_point, self.length, self.index)

        added_object.selected = self.was_selected

        # in case the index was just -1
        self.index = self.level.objects.index(added_object)

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {added_object.name} at {added_object.x_position}, {added_object.y_position}")

        self.level.data_changed.emit()

    def to_data(self) -> list:
        """Serialize the placement in level coordinates.

        The view marker lets debug replay convert the stored level point back
        into a command bound to the active ``LevelView``.

        Returns
        -------
        list
            Serialized undo history data for this command.

        Examples
        --------
        >>> command.to_data()[1:]
        [
        ...     command.level_point.xy,
        ...     command.domain,
        ...     command.obj_type,
        ...     command.length,
        ...     command.index,
        ...     command.was_selected,
        ... ]
        """
        return [
            UndoCommand.MAGIC_VALUE_LEVEL_VIEW,
            self.level_point.xy,
            self.domain,
            self.obj_type,
            self.length,
            self.index,
            self.was_selected,
        ]

    @classmethod
    def from_data(
        cls,
        level_view: "LevelView",
        xy: tuple[int, int],
        domain: int,
        obj_type: int,
        length: int | None,
        index: int,
        was_selected: bool,
    ):
        """Rebuild an object placement command from macro data.

        Replay injects the active ``LevelView`` and reconstructs the command
        from the serialized level-space placement data. The command starts with
        a placeholder Qt point, then restores the captured level coordinate so
        redo re-enters the normal view-driven insertion path without depending
        on the original mouse event.

        Parameters
        ----------
        level_view : 'LevelView'
            Level view controlled by the menu action.
        xy : tuple[int, int]
            Level-space coordinate captured from the original placement.
        domain : int
            Object domain that determines how the object is interpreted.
        obj_type : int
            Object type identifier to place.
        length : int | None
            Object length value.
        index : int
            Zero-based index of the item to access.
        was_selected : bool
            Whether was selected is enabled.

        Returns
        -------
        AddLevelObjectAt
            Command restored from serialized undo history data.
        """
        command = cls(level_view, QPoint(0, 0), domain, obj_type, length, index, selected=was_selected)
        command.level_point = Position.from_tuple(xy)

        return command


class AddEnemyAt(UndoCommand):
    # TODO doesn't need to be a QPoint, I think?
    """Add an enemy or item at a view position.

    Like object placement, this stores a level coordinate instead of a raw Qt
    point so zoom changes do not affect undo, redo, or macro replay. Enemy
    placement also preserves the optional autoscroll marker used by SMB3 enemy
    data.

    Parameters
    ----------
    level_view : 'LevelView'
        Level view controlled by the menu action.
    pos : QPoint
        View-space position where the enemy was placed.
    enemy_type : int, optional
        Enemy type identifier to place.
    index : int, optional
        Zero-based index of the item to access.
    selected : bool, optional
        Whether the object should be drawn as selected.
    auto_scroll_type : int, optional
        Autoscroll marker stored on the inserted enemy item.

    Attributes
    ----------
    auto_scroll_type : int
        Autoscroll marker restored on redo.
    enemy_type : int
        SMB3 enemy/item type passed to ``Level.add_enemy``.
    index : int
        Index where the enemy is inserted or later removed.
    level : LevelRef
        Active level reference reached through the view.
    level_point : Position
        Level-space coordinate captured from the original view position.
    view : LevelView
        View used to convert from Qt coordinates to level coordinates.
    was_selected : bool
        Selection state applied to the new enemy.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload
    [
    ...     UndoCommand.MAGIC_VALUE_LEVEL_VIEW,
    ...     command.level_point.xy,
    ...     command.enemy_type,
    ...     command.index,
    ...     command.was_selected,
    ...     command.auto_scroll_type,
    ... ]
    >>> replayed = AddEnemyAt.from_data(level_view, *payload[1:])
    >>> replayed.to_data() == payload
    True
    """

    def __init__(
        self, level_view: "LevelView", pos: QPoint, enemy_type=0, index=-1, /, selected=False, auto_scroll_type=0
    ):
        """Capture the enemy placement request.

        The placement point is converted immediately so the command is not
        coupled to the view zoom when it later replays.

        Parameters
        ----------
        level_view : 'LevelView'
            Level view controlled by the menu action.
        pos : QPoint
            View-space position where the enemy was placed.
        enemy_type : int, optional
            Enemy type identifier to place.
        index : int, optional
            Zero-based index of the item to access.
        selected : bool, optional
            Whether the object should be drawn as selected.
        auto_scroll_type : int, optional
            Autoscroll marker stored on the inserted enemy item.
        """
        super(AddEnemyAt, self).__init__(None)

        self.view = level_view
        self.level = level_view.level_ref

        self.auto_scroll_type = auto_scroll_type

        # convert here, in case there's a zoom change happening between undo and redo
        self.level_point = level_view.to_level_point(pos)

        self.enemy_type = enemy_type

        self.index = index
        self.was_selected = selected

    def undo(self):
        """Remove the enemy inserted by ``redo``."""
        self.level.enemies.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        """Insert the enemy and remember its resolved index."""
        added_enemy = self.level.add_enemy(self.enemy_type, self.level_point, self.index)
        added_enemy.auto_scroll_type = self.auto_scroll_type
        added_enemy.selected = self.was_selected

        # in case the index was just -1
        self.index = self.level.enemies.index(added_enemy)

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {added_enemy.name} at {added_enemy.x_position}, {added_enemy.y_position}")

        self.level.data_changed.emit()

    def to_data(self) -> list:
        """Serialize enemy placement for macro replay.

        The payload keeps the level-space coordinate, resolved insertion index,
        and autoscroll marker so replay can rebuild the same enemy insertion
        without depending on transient Qt event objects.

        Returns
        -------
        list
            Serialized undo history data for this command.

        Examples
        --------
        >>> command.to_data()[1:]
        [
        ...     command.level_point.xy,
        ...     command.enemy_type,
        ...     command.index,
        ...     command.was_selected,
        ...     command.auto_scroll_type,
        ... ]
        """
        return [
            UndoCommand.MAGIC_VALUE_LEVEL_VIEW,
            self.level_point.xy,
            self.enemy_type,
            self.index,
            self.was_selected,
            self.auto_scroll_type,
        ]

    @classmethod
    def from_data(
        cls,
        level_view: "LevelView",
        xy: tuple[int, int],
        enemy_type: int,
        index: int,
        was_selected: bool,
        auto_scroll_type: int,
    ) -> "UndoCommand":
        """Rebuild an enemy-placement command from serialized data.

        Replay reconstructs the command with a placeholder Qt point, then
        restores the captured level coordinate so the command stays independent
        of view zoom and mouse events.

        Parameters
        ----------
        level_view : 'LevelView'
            Level view controlled by the menu action.
        xy : tuple[int, int]
            Stored level-space coordinate for the inserted enemy.
        enemy_type : int
            Enemy type identifier to place.
        index : int
            Zero-based index where the enemy should be inserted.
        was_selected : bool
            Whether the inserted enemy should be marked selected.
        auto_scroll_type : int
            Autoscroll marker restored on the inserted enemy.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.
        """
        command = cls(
            level_view, QPoint(0, 0), enemy_type, index, selected=was_selected, auto_scroll_type=auto_scroll_type
        )
        command.level_point = Position.from_tuple(xy)

        return command


class PasteObjectsAt(UndoCommand):
    """Paste copied objects and enemies at a new level position.

    The copied payload contains cloned objects plus the original anchor
    position from the copy operation. This command captures the destination
    level coordinate, then replays the paste through ``LevelView`` so redraw,
    selection, and object construction follow the same path as an interactive
    paste. Undo removes the appended objects by count because paste inserts
    them at the end of the level and enemy streams.

    Parameters
    ----------
    level_view : 'LevelView'
        Level view controlled by the menu action.
    paste_data : tuple[list[InLevelObject], Position]
        Copied objects plus the original copy anchor.
    pos : QPoint
        View-space destination for the paste.

    Attributes
    ----------
    enemy_count : int
        Number of enemy/item entries appended by the paste.
    level_point : Position
        Destination level coordinate captured from the view position.
    object_count : int
        Number of level-object entries appended by the paste.
    paste_data : tuple[list[InLevelObject], Position]
        Copied objects plus the original copy anchor.
    view : LevelView
        View used to convert coordinates and perform the paste.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload[1]
    [(obj.domain, obj.obj_index, obj.length, obj.is_4byte, obj.get_data_position()), ...]
    >>> replayed = PasteObjectsAt.from_data(level_view, *payload[1:])
    >>> replayed.level_point == command.level_point
    True
    >>> replayed.to_data()[2:] == payload[2:]
    True
    """

    def __init__(
        self,
        level_view: "LevelView",
        paste_data: tuple[list[InLevelObject], Position],
        pos: QPoint,
    ):
        """Capture copied objects and the destination paste point.

        The copied payload already contains cloned objects plus the original
        copy anchor, but the destination still comes from the active editor
        interaction. The constructor converts that destination to a level
        coordinate immediately and counts the object and enemy entries the
        paste will append so undo can later remove exactly the appended tail
        entries after redo pastes through ``LevelView``.

        Parameters
        ----------
        level_view : 'LevelView'
            Level view controlled by the menu action.
        paste_data : tuple[list[InLevelObject], Position]
            Copied objects plus the original copy anchor.
        pos : QPoint
            View-space destination for the paste.
        """
        super(PasteObjectsAt, self).__init__(None)

        self.view = level_view
        self.paste_data = paste_data

        objects, _ = paste_data

        self.object_count = len(list(filter(lambda obj: isinstance(obj, LevelObject), objects)))
        self.enemy_count = len(objects) - self.object_count

        self.level_point = self.view.to_level_point(pos)

        self.setText(f"Paste {object_names(objects)}")

    def undo(self):
        """Remove the objects and enemies appended by the paste."""
        for _ in range(self.object_count):
            self.view.level_ref.level.objects.pop()

        for _ in range(self.enemy_count):
            self.view.level_ref.level.enemies.pop()

        self.view.level_ref.level.data_changed.emit()

    def redo(self):
        # this will create clones of the cached objects, not paste them with their old graphics (in case of ROM reload)
        """Replay the paste through ``LevelView`` at the stored level point."""
        self.view.paste_objects_at(self.paste_data, self.level_point)

        self.view.level_ref.level.data_changed.emit()

    def to_data(self) -> list:
        """Serialize copied objects into replay-friendly primitive data.

        Replay cannot reuse the in-memory copied objects directly, so the
        command converts them into primitive tuples that preserve either a
        ``LevelObject`` definition or an enemy definition plus the original
        copy anchor and the destination level coordinate. ``from_data`` uses
        that payload to rebuild paste input and rerun the same view-driven
        paste workflow later.

        Returns
        -------
        list
            Marker, serialized copied objects, copy anchor, and paste target.

        Examples
        --------
        >>> payload = command.to_data()
        >>> payload[2], payload[3]
        (command.paste_data[1].xy, command.level_point.xy)
        """
        in_between_data: list[tuple] = []

        for obj in self.paste_data[0]:
            if isinstance(obj, LevelObject):
                in_between_data.append((obj.domain, obj.obj_index, obj.length, obj.is_4byte, obj.get_data_position()))
            else:
                in_between_data.append((obj.obj_index, obj.get_position()))

        return [UndoCommand.MAGIC_VALUE_LEVEL_VIEW, in_between_data, self.paste_data[1].xy, self.level_point.xy]

    @classmethod
    def from_data(
        cls,
        level_view: "LevelView",
        in_between_data: list,
        paste_position: tuple[int, int],
        level_point: tuple[int, int],
    ) -> "UndoCommand":
        """Rebuild a paste command from serialized object payloads.

        Macro replay reconstructs lightweight object records from the
        serialized tuples, restores the original copy anchor, and then reuses
        the normal ``PasteObjectsAt`` command path so redo pastes through
        ``LevelView`` instead of inventing a separate insertion workflow.

        Parameters
        ----------
        level_view : 'LevelView'
            Level view controlled by the menu action.
        in_between_data : list
            Serialized copied objects produced by ``to_data``.
        paste_position : tuple[int, int]
            Original copy anchor position.
        level_point : tuple[int, int]
            Destination level coordinate for the paste.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        object_count = 0
        enemy_count = 0

        objects: list[InLevelObject] = []

        dummy_data = bytearray([0, 0, 0])
        dummy_palette_group = PaletteGroup(0, 0, 0, [])
        dummy_graphics_set = GraphicsSet.from_number(1)

        for obj_data in in_between_data:
            if len(obj_data) == 2:
                obj_type, (x, y) = obj_data

                enemy = EnemyItem(dummy_data, QImage(), dummy_palette_group)
                enemy.obj_index = obj_type
                enemy.x_position = x
                enemy.y_position = y

                objects.append(enemy)

                enemy_count += 1

            elif len(obj_data) == 5:
                domain, obj_index, length, is_4_byte, (x, y) = obj_data

                level_object = LevelObject(dummy_data, 1, dummy_palette_group, dummy_graphics_set, [], False, -1)
                level_object.domain = domain
                level_object.obj_index = obj_index
                level_object.length = length
                level_object.is_4byte = is_4_byte
                level_object.rendered_base_x = x
                level_object.rendered_base_y = y

                objects.append(level_object)

                object_count += 1

            else:
                raise ValueError(f"Invalid data length: {len(obj_data)}, '{obj_data}'")

        paste_data = (objects, Position.from_tuple(paste_position))

        command = cls(level_view, paste_data, QPoint(0, 0))

        command.level_point = Position.from_tuple(level_point)

        return command


class RemoveObjects(UndoCommand):
    """Remove selected objects or enemies while preserving their reinsertion points.

    The command records the original indexes for each selected entry, then
    removes from the live level in reverse order so later indexes stay valid.
    Undo uses ``move_objects(..., restore_only=True)`` to rebuild the original
    ordering without depending on stale Python object identities.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose object and enemy streams are mutated.
    objects : list[InLevelObject]
        Objects chosen for removal.

    Attributes
    ----------
    indexes_before_removal : list[tuple[int, InLevelObject]]
        Original level/enemy indexes paired with the removed objects.
    level : foundry.game.level.Level.Level
        Level whose object and enemy streams are mutated.
    objects : list[InLevelObject]
        Objects chosen for removal when the command was created.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload
    [UndoCommand.MAGIC_VALUE_LEVEL, [0, 3], [1]]
    >>> replayed = RemoveObjects.from_data(level, *payload[1:])
    >>> len(replayed.indexes_before_removal) == len(command.indexes_before_removal)
    True
    >>> replayed.to_data() == payload
    True
    """

    def __init__(self, level: Level, objects: list[InLevelObject]):
        """Capture the objects that should be removed.

        The command records live object references plus their original indexes
        before anything is deleted. That staging lets redo remove from the end
        of each stream without shifting earlier indexes out from under the
        command, and it gives undo enough information to rebuild the original
        order through ``move_objects(..., restore_only=True)``.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object and enemy streams are mutated.
        objects : list[InLevelObject]
            Objects chosen for removal.
        """
        super(RemoveObjects, self).__init__(None)

        self.level = level
        self.objects = objects

        self.indexes_before_removal = objects_to_indexed_objects(self.level, self.objects)

        self.setText(f"Remove {object_names(self.objects)}")

    def undo(self):
        """Reinsert removed objects at their original indexes."""
        self.level.clear_selection()

        move_objects(self.level, self.indexes_before_removal, restore_only=True)

        self.level.data_changed.emit()

    def redo(self):
        """Remove the recorded objects from the live level."""
        for index, obj in reversed(self.indexes_before_removal):
            if isinstance(obj, LevelObject):
                self.level.objects.pop(index)
            else:
                assert isinstance(obj, EnemyItem)
                self.level.enemies.pop(index)

        self.level.data_changed.emit()

    def to_data(self):
        """Serialize object and enemy indexes for replay.

        Replay only needs the original indexes because the live level still
        contains the target objects when the command is reconstructed. The
        payload therefore separates level-object and enemy indexes so
        ``from_data`` can rebuild the same mixed removal command from the
        current level streams.

        Returns
        -------
        list
            Marker, level-object indexes, and enemy indexes.

        Examples
        --------
        >>> command.to_data()[1:]
        [[index for index, obj in command.indexes_before_removal if isinstance(obj, LevelObject)], ...]
        """
        level_object_indexes = [index for index, obj in self.indexes_before_removal if isinstance(obj, LevelObject)]
        enemy_indexes = [index for index, obj in self.indexes_before_removal if isinstance(obj, EnemyItem)]

        return [UndoCommand.MAGIC_VALUE_LEVEL, level_object_indexes, enemy_indexes]

    @classmethod
    def from_data(cls, level: Level, level_object_indexes: list[int], enemy_indexes):
        """Rebuild a removal command from stored object indexes.

        Macro replay resolves the stored indexes against the active level
        streams, recreates the mixed object list, and then constructs a normal
        ``RemoveObjects`` command so undo and redo keep using the same reverse-
        removal and restore-only reinsertion paths as the original command.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object and enemy streams are mutated.
        level_object_indexes : list[int]
            Indexes of level objects removed by the command.
        enemy_indexes : list[int]
            Indexes of enemies/items removed by the command.

        Returns
        -------
        RemoveObjects
            Command restored from serialized undo history data.
        """
        level_objects = [level.objects[index] for index in level_object_indexes]
        enemy_items = [level.enemies[index] for index in enemy_indexes]

        # explicitly use RemoveObjects here, so inheriting classes don't crash
        command = RemoveObjects(level, level_objects + enemy_items)

        return command


class RemoveObject(RemoveObjects):
    """Remove one object or enemy through the multi-remove command path.

    The single-item wrapper keeps menus and focused actions aligned with the
    same index-based undo behavior used for bulk deletion, so context-menu and
    keyboard deletes do not need a separate removal implementation or replay
    format.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose object or enemy stream is mutated.
    in_level_object : InLevelObject
        Object or enemy chosen for removal.
    """

    def __init__(self, level: Level, in_level_object: InLevelObject):
        """Capture the single object or enemy to remove.

        This wrapper exists for focused delete actions that already know which
        one entry should be removed. It forwards that one object into the bulk
        removal path so context-menu and keyboard deletes preserve the same
        index-tracking, undo, and replay behavior as multi-selection removal.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object or enemy stream is mutated.
        in_level_object : InLevelObject
            Object or enemy chosen for removal.
        """
        super().__init__(level, [in_level_object])


# Could maybe be replaced by a macro of remove and add object?
class ReplaceLevelObject(UndoCommand):
    """Replace one level object with another object definition.

    This command powers type cycling and object replacement from the UI. It
    stores the target object index and replacement definition, then refreshes
    the original object from the live level during ``redo``. That index-based
    boundary is what lets replacement commands continue to work after a ROM
    reload rebuilds object instances.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose object list contains the object to replace.
    to_replace : foundry.game.gfx.objects.in_level.level_object.LevelObject
        Existing object being replaced.
    domain : int
        Object domain that determines how the object is interpreted.
    obj_type : int
        Object type identifier to place.
    length : int | None
        Object length value.

    Attributes
    ----------
    domain : int
        Replacement object domain.
    length : int | None
        Replacement object length.
    level : foundry.game.level.Level.Level
        Level whose object list is mutated.
    obj_type : int
        Replacement object type.
    to_replace : foundry.game.gfx.objects.in_level.level_object.LevelObject
        Object restored on undo.
    to_replace_index : int
        Index of the replaced object in ``level.objects``.

    Examples
    --------
    >>> replacement = ReplaceLevelObject(level, level.objects[0], 0, 3, None)
    >>> replacement.id()
    123

    Repeated replacements for the same slot merge into one undo step.

    >>> replacement.to_data()
    [
    ...     UndoCommand.MAGIC_VALUE_LEVEL,
    ...     replacement.to_replace_index,
    ...     replacement.domain,
    ...     replacement.obj_type,
    ...     replacement.length,
    ... ]
    >>> replayed = ReplaceLevelObject.from_data(level, *replacement.to_data()[1:])
    >>> replayed.to_data() == replacement.to_data()
    True
    """

    def __init__(
        self,
        level: Level,
        to_replace: LevelObject,
        domain: int,
        obj_type: int,
        length: int | None,
    ):
        """Capture the object replacement request.

        The initial object reference is used to find the index. Serialized and
        merged commands keep the index plus replacement fields.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose object list contains the object to replace.
        to_replace : foundry.game.gfx.objects.in_level.level_object.LevelObject
            Existing object being replaced.
        domain : int
            Object domain that determines how the object is interpreted.
        obj_type : int
            Object type identifier to place.
        length : int | None
            Object length value.
        """
        super(ReplaceLevelObject, self).__init__(None)

        self.level = level
        self.domain = domain
        self.obj_type = obj_type
        self.length = length

        self.to_replace = to_replace
        self.to_replace_index = self.level.objects.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        """Restore the original object at its recorded index."""
        self.level.objects[self.to_replace_index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        """Replace the live object at the recorded index.

        The object is looked up again from ``level.objects`` so repeated redo or
        replay after ROM reload uses the rebuilt level model instead of a stale
        object reference.
        """
        self.to_replace = self.level.objects.pop(self.to_replace_index)

        x, y = self.to_replace.get_position()

        created_object = self.level.add_object(
            self.domain,
            self.obj_type,
            Position.from_xy(x, y),
            self.length,
            self.to_replace_index,
        )

        assert created_object is not None

        created_object.selected = self.to_replace.selected

        self.level.data_changed.emit()

    def id(self):
        """Expose the Qt merge identifier for object replacement.

        Qt uses this identifier when deciding whether repeated type-cycling
        commands may collapse into one undo step. Returning a stable identifier
        is what places this command family into Qt's command-compression flow;
        it does not mutate level state by itself, but it determines whether
        later wheel-driven replacements are offered as one undo boundary or
        many.

        Returns
        -------
        int
            Undo command identifier used by Qt.
        """
        return 123

    def mergeWith(self, other):
        """Merge another replacement for the same object index.

        Type cycling should undo as one action, so only the final replacement
        definition is kept when Qt merges compatible commands for the same live
        object slot. A successful merge updates the staged replacement fields
        in-place while preserving the original pre-change object captured by the
        first command, which is what lets undo return to the true starting
        object after a long type-cycling gesture. In practice this is the
        command-compression boundary for wheel-driven type changes: the method
        verifies that both commands still target the same object slot, then
        swaps in the newer replacement definition so the merged command redoes
        the last selected type while undo still restores the original object
        from before the cycling began.

        Parameters
        ----------
        other : QUndoCommand
            Candidate command supplied by Qt.

        Returns
        -------
        bool
            True when the command merged with the other command.
        """
        if not isinstance(other, ReplaceLevelObject):
            return False

        if self.to_replace_index != other.to_replace_index:
            return False

        self.domain = other.domain
        self.obj_type = other.obj_type
        self.length = other.length

        return True

    def to_data(self) -> list:
        """Serialize object replacement for macro replay.

        Replay keeps only the object index and replacement definition, then
        resolves the live object from the active level before applying the
        replacement.

        Returns
        -------
        list
            Serialized undo history data for this command.

        Examples
        --------
        >>> replacement.to_data()[1:]
        [replacement.to_replace_index, replacement.domain, replacement.obj_type, replacement.length]
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.to_replace_index, self.domain, self.obj_type, self.length]

    @classmethod
    def from_data(cls, level, object_index: int, domain: int, obj_type: int, length: int) -> "UndoCommand":
        """Rebuild an object-replacement command from serialized data.

        The object index is resolved against the active level at replay time so
        the command follows the same index-based contract as normal redo.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Active level whose object list contains the replacement target.
        object_index : int
            Index of the object.
        domain : int
            Object domain that determines how the object is interpreted.
        obj_type : int
            Object type identifier to place.
        length : int
            Object length value.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.
        """
        level_object = level.objects[object_index]

        return cls(level, level_object, domain, obj_type, length)


class ReplaceEnemy(UndoCommand):
    """Replace one enemy or item with another enemy type.

    Enemy cycling mirrors object cycling but targets SMB3's separate enemy/item
    stream. The command keeps the enemy index and replacement type so it can be
    replayed against the active level after ROM reload.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose enemy list contains the enemy to replace.
    to_replace : EnemyItem
        Existing enemy or item being replaced.
    new_enemy_type : int
        Replacement enemy/item type.

    Attributes
    ----------
    level : foundry.game.level.Level.Level
        Level whose enemy list is mutated.
    new_enemy_type : int
        Replacement enemy/item type.
    to_replace : EnemyItem
        Enemy restored on undo.
    to_replace_index : int
        Index of the replaced enemy in ``level.enemies``.

    Examples
    --------
    >>> replacement = ReplaceEnemy(level, level.enemies[0], 2)
    >>> replacement.to_data()
    [UndoCommand.MAGIC_VALUE_LEVEL, replacement.to_replace_index, replacement.new_enemy_type]
    >>> replayed = ReplaceEnemy.from_data(level, *replacement.to_data()[1:])
    >>> replayed.to_data() == replacement.to_data()
    True
    """

    def __init__(self, level: Level, to_replace: EnemyItem, new_enemy_type: int):
        """Capture the enemy replacement request.

        The initial enemy reference is used to find the index. Serialized and
        merged commands keep the index plus replacement type.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose enemy list contains the enemy to replace.
        to_replace : EnemyItem
            Existing enemy or item being replaced.
        new_enemy_type : int
            Replacement enemy/item type.
        """
        super(ReplaceEnemy, self).__init__(None)

        self.level = level
        self.new_enemy_type = new_enemy_type

        self.to_replace = to_replace
        self.to_replace_index = self.level.enemies.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        """Restore the original enemy at its recorded index."""
        self.level.enemies[self.to_replace_index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        """Replace the live enemy at the recorded index.

        The enemy is looked up again from ``level.enemies`` so repeated redo or
        replay after ROM reload uses the rebuilt enemy stream instead of a stale
        object reference.
        """
        self.to_replace = self.level.enemies.pop(self.to_replace_index)

        x, y = self.to_replace.get_position()

        created_enemy = self.level.add_enemy(self.new_enemy_type, Position.from_xy(x, y), self.to_replace_index)

        created_enemy.selected = self.to_replace.selected

        self.level.data_changed.emit()

    def id(self):
        """Expose the Qt merge identifier for enemy replacement.

        Qt uses this identifier when deciding whether repeated enemy type
        cycling may collapse into one undo step while the editor wheel-cycles
        the same enemy slot. The identifier therefore participates in Qt's
        command-compression flow rather than changing level data directly, and
        it keeps repeated replacements for one enemy slot eligible to merge
        into the same undo boundary.

        Returns
        -------
        int
            Undo command identifier used by Qt.
        """
        return 122

    def mergeWith(self, other):
        """Merge another replacement for the same enemy index.

        Repeated enemy type cycling keeps only the final type in the undo stack
        for the same live enemy slot, mirroring the editor interaction where
        scrolling through enemy types should undo as one change. Returning
        ``True`` here updates the staged replacement type without inserting
        another undo entry. That preserves the first command's snapshot of the
        original enemy while still letting redo apply the last wheel-selected
        type when the merged command runs.

        Parameters
        ----------
        other : QUndoCommand
            Candidate command supplied by Qt.

        Returns
        -------
        bool
            True when the command merged with the other command.
        """
        if not isinstance(other, ReplaceEnemy):
            return False

        if self.to_replace_index != other.to_replace_index:
            return False

        self.new_enemy_type = other.new_enemy_type

        return True

    def to_data(self) -> list:
        """Serialize enemy replacement for macro replay.

        Replay keeps only the enemy index and replacement type, then resolves
        the live enemy from the active level before applying the change.

        Returns
        -------
        list
            Serialized undo history data for this command.

        Examples
        --------
        >>> replacement.to_data()[1:]
        [replacement.to_replace_index, replacement.new_enemy_type]
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.to_replace_index, self.new_enemy_type]

    @classmethod
    def from_data(cls, level, enemy_index: int, new_enemy_type: int) -> "UndoCommand":
        """Rebuild an enemy-replacement command from serialized data.

        The enemy index is resolved against the active level at replay time so
        the command follows the same index-based contract as normal redo.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Active level whose enemy list contains the replacement target.
        enemy_index : int
            Index of the enemy in the active enemy stream.
        new_enemy_type : int
            Replacement enemy or item type to apply at replay time.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.
        """
        enemy = level.enemies[enemy_index]

        return cls(level, enemy, new_enemy_type)


class AddJump(UndoCommand):
    """Insert a jump record into a level's jump table.

    SMB3 treats jumps as their own encoded structure, separate from the level
    object and enemy streams. The command stores the jump bytes plus the target
    insertion index so jump editing remains undoable and replayable without
    depending on a live ``Jump`` instance.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose jump list is mutated.
    jump : Jump | None, optional
        Jump inserted on redo. A default jump is created when omitted.
    index : int, optional
        Zero-based index of the item to access.

    Attributes
    ----------
    index : int
        Position where the jump is inserted or removed.
    jump : Jump
        Jump inserted on redo and restored on undo.
    level : foundry.game.level.Level.Level
        Level whose jump list is mutated.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload
    [UndoCommand.MAGIC_VALUE_LEVEL, command.index, command.jump.data]
    >>> replayed = AddJump.from_data(level, *payload[1:])
    >>> replayed.index == command.index
    True
    >>> replayed.to_data() == payload
    True
    """

    def __init__(self, level: Level, jump: Jump | None = None, index: int = -1):
        """Capture a jump insertion, creating a default jump when needed.

        Jump edits do not flow through the object or enemy insertion helpers, so
        the command snapshots the ``Jump`` instance and insertion slot itself.
        That staging gives the jump editor the same undo-stack ownership as the
        rest of Foundry's level-edit operations while keeping replay tied to raw
        jump bytes instead of a transient editor widget.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose jump list is mutated.
        jump : Jump | None, optional
            Jump inserted on redo. A default jump is created when omitted.
        index : int, optional
            Zero-based index of the item to access.
        """
        super(AddJump, self).__init__(None)

        self.level = level

        if jump is None:
            self.jump = Jump.from_properties(0, 0, 0, 0)
        else:
            self.jump = jump

        if index == -1:
            self.index = len(level.jumps)
        else:
            self.index = index

        self.setText("Add Jump")

    def undo(self):
        """Remove the inserted jump from the recorded index."""
        self.level.jumps.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        """Insert the jump at the recorded index."""
        self.level.jumps.insert(self.index, self.jump)

        self.level.data_changed.emit()

    def to_data(self) -> list:
        """Serialize the jump insertion for replay.

        Replay stores the insertion slot plus the raw jump bytes so the command
        can rebuild the same jump record later without depending on the
        original ``Jump`` instance surviving undo-stack export.

        Returns
        -------
        list
            Marker, insertion index, and raw jump bytes.

        Examples
        --------
        >>> command.to_data()[1:]
        [command.index, command.jump.data]
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.index, self.jump.data]

    @classmethod
    def from_data(cls, level, index: int, jump_data: bytes) -> "UndoCommand":
        """Rebuild a jump-insert command from serialized jump bytes.

        Macro replay reconstructs the ``Jump`` from its raw bytes and then
        reuses the normal constructor so redo inserts through the same jump-list
        boundary as an interactive add action.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose jump list is mutated.
        index : int
            Position where the jump should be inserted.
        jump_data : bytes
            Raw jump bytes captured by ``to_data``.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.
        """
        jump = Jump(jump_data)

        return cls(level, jump, index=index)


class RemoveJump(UndoCommand):
    """Remove one jump from a level while retaining its serialized bytes.

    The command snapshots the ``Jump`` object at the selected index so undo can
    reinsert it at the same position in the jump table. This gives the jump
    editor the same reversible editing model as object and enemy lists even
    though jumps live in a separate SMB3 data structure.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level whose jump list is mutated.
    index : int
        Zero-based index of the item to access.

    Attributes
    ----------
    index : int
        Position of the removed jump in ``level.jumps``.
    jump : Jump
        Jump restored on undo.
    level : foundry.game.level.Level.Level
        Level whose jump list is mutated.

    Examples
    --------
    >>> payload = command.to_data()
    >>> payload
    [UndoCommand.MAGIC_VALUE_LEVEL, command.index]
    >>> replayed = RemoveJump.from_data(level, *payload[1:])
    >>> replayed.index == command.index
    True
    >>> replayed.to_data() == payload
    True
    """

    def __init__(self, level: Level, index: int):
        """Capture the jump removed from the given index.

        The constructor snapshots the jump object immediately so later jump-list
        mutations or undo can still restore the same encoded jump at the same
        slot. That keeps jump deletion aligned with the same staged-before-
        mutation contract the object and enemy commands use. The method is also
        the handoff point between the jump editor UI and the undo stack: once
        the constructor captures the jump bytes and index, redo can remove the
        slot and undo can restore it without consulting the widget that issued
        the delete action. In command-lifecycle terms this is where the jump
        editor's transient selection is converted into a stable undo record
        containing both the active slot and the exact ``Jump`` instance that
        later undo will reinsert into the live jump table.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level whose jump list is mutated.
        index : int
            Zero-based index of the item to access.
        """
        super(RemoveJump, self).__init__(None)

        self.level = level

        self.jump = self.level.jumps[index]
        self.index = index

        self.setText(f"Remove {self.jump}")

    def undo(self):
        """Reinsert the removed jump at its original index."""
        self.level.jumps.insert(self.index, self.jump)

        self.level.data_changed.emit()

    def redo(self):
        """Remove the jump at the recorded index."""
        self.level.jumps.pop(self.index)

        self.level.data_changed.emit()

    def to_data(self) -> list:
        """Serialize the jump index for replay.

        Replay only needs the jump-table index because the active level still
        contains the jump until the reconstructed command is first redone.

        Returns
        -------
        list
            Marker plus the removed jump index.

        Examples
        --------
        >>> command.to_data()[1:]
        [command.index]
        """
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.index]

    @classmethod
    def from_data(cls, level: Level, index: int) -> "UndoCommand":
        """Rebuild a jump-removal command from a stored index.

        Replay resolves the jump from the active level's jump table using the
        stored index, matching the normal constructor contract.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Active level whose jump list contains the removal target.
        index : int
            Zero-based index of the jump to remove.

        Returns
        -------
        'UndoCommand'
            Command restored from serialized undo history data.
        """
        return cls(level, index=index)


class UpdatePipeData(UndoCommand):
    """Replace the ROM-wide pipe exit pair table.

    Pipe pairing is global SMB3 data rather than level-local state. The command
    snapshots every pipe entry from ROM, then writes either the old
    or new ``PipeData`` records back to ROM during undo and redo. That makes
    the level-settings dialog's staged pipe edits reversible as one operation.

    Parameters
    ----------
    pipe_data : list[PipeData]
        Replacement pipe records collected from the settings dialog.

    Attributes
    ----------
    pipe_data_after : list[PipeData]
        Pipe records written on redo.
    pipe_data_before : list[PipeData]
        Pipe records restored on undo.

    Examples
    --------
    >>> payload = command.to_data()
    >>> isinstance(payload[0][0], dict)
    True
    >>> replayed = UpdatePipeData.from_data(*payload)
    >>> replayed.to_data() == payload
    True
    """

    def __init__(self, pipe_data: list[PipeData]):
        """Capture the existing ROM pipe data and the replacement records.

        The command snapshots the full global table before applying any dialog
        edits because pipe exits are ROM-wide data. Undo restores the pre-edit
        table, while redo reapplies the staged replacement table as one editor
        action.

        Parameters
        ----------
        pipe_data : list[PipeData]
            Replacement pipe records collected from the settings dialog.
        """
        super(UpdatePipeData, self).__init__(None)

        self.pipe_data_before = [PipeData(ROM(), index) for index in range(PIPE_PAIR_COUNT)]
        self.pipe_data_after = pipe_data

        self.setText("Updating Pipe Exit Pair Data")

    def undo(self) -> None:
        """Write the original pipe records back to ROM."""
        for pipe_data in self.pipe_data_before:
            pipe_data.write_back()

    def redo(self) -> None:
        """Write the replacement pipe records back to ROM."""
        for pipe_data in self.pipe_data_after:
            pipe_data.write_back()

    def to_data(self):
        """Serialize replacement pipe records as plain dictionaries.

        Macro replay stores only the replacement table because redo can rebuild
        the command against the ROM visible at replay time and still rewrite
        the same staged pipe configuration.

        Returns
        -------
        list
            Serialized replacement pipe records.

        Examples
        --------
        >>> isinstance(command.to_data()[0][0], dict)
        True
        """
        return [[_pipe_data_to_dict(pipe_data) for pipe_data in self.pipe_data_after]]

    @classmethod
    def from_data(cls, pipe_data_list) -> "UndoCommand":
        """Rebuild pipe records from serialized dictionaries.

        Replay reconstructs ``PipeData`` objects against the live ROM, fills
        them from the serialized dictionaries, and then reuses the normal
        command constructor so undo and redo behavior matches a live edit.
        That reconstruction step matters because the command must target the
        ROM loaded for replay, not stale ``PipeData`` instances captured in a
        previous editing session.

        Parameters
        ----------
        pipe_data_list : list[dict]
            Serialized pipe records produced by ``to_data``.

        Returns
        -------
        UpdatePipeData
            Command restored from serialized undo history data.
        """
        current_pipe_data = [PipeData(ROM(), index) for index in range(PIPE_PAIR_COUNT)]

        for pipe_data, pipe_data_dict in zip(current_pipe_data, pipe_data_list):
            for attr, value in pipe_data_dict.items():
                setattr(pipe_data, attr, value)

        return cls(current_pipe_data)


def _pipe_data_to_dict(pipe_data: PipeData) -> dict:
    """Return data to dict.

    It participates in the undo/redo command stream that keeps GUI edits reversible. The return value keeps undo serialization and command merging explicit for the command stack.

    Parameters
    ----------
    pipe_data : PipeData
        Data for the pipe value.

    Returns
    -------
    dict
        Pipe pair data keyed for serialization.
    """
    pipe_dict = {}

    for attr in dir(pipe_data):
        if attr.startswith("_"):
            continue

        if attr == "rom":
            continue

        if callable(getattr(pipe_data, attr)):
            continue

        pipe_dict[attr] = getattr(pipe_data, attr)

    return pipe_dict
