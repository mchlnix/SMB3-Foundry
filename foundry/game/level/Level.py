"""Editable SMB3 in-level model and serialization workflow.

This module centers the editor-facing :class:`Level` aggregate that ties
together header decoding, object and jump streams, enemy data, and ROM or
import/export serialization paths. It is the main bridge between SMB3's
encoded in-level data and the editor workflows that inspect, mutate, reload,
and persist that data.

Notes
-----
This file sits on a low-level boundary where ROM layout, SMB3 header fields,
and editor-driven save or reload behavior meet. For nuanced explanations, use
Git history, NESdev references, and SMB3 disassembly context only where the
implementation clearly depends on them.

See Also
--------
foundry.game.level.WorldMap
    Overworld model that provides the sibling
    :class:`~foundry.game.level.LevelLike.LevelLike` editing surface.
foundry.game.additional_data
    Tracks editor-only metadata and managed level placement beside ROM data.
foundry.gui.visualization.level.LevelView
    Main interactive canvas that consumes and mutates this model.
"""

from typing import cast

from PySide6.QtCore import QObject, Signal, SignalInstance

from foundry.game.additional_data import LEVEL_DATA_DELIMITER_COUNT, LevelOrganizer
from foundry.game.File import ROM
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.enemy_item_factory import EnemyItemFactory
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.in_level.level_object_factory import LevelObjectFactory
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.level import (
    EnemyItemData,
    LevelByteData,
    ObjectData,
    _load_level_offsets,
)
from foundry.game.level.LevelLike import LevelLike
from foundry.game.ObjectSet import ObjectSet
from foundry.gui.asm import bytes_to_asm
from smb3parse.constants import BASE_OFFSET, ENEMY_SIZE, OFFSET_SIZE, Constants
from smb3parse.data_points import Position
from smb3parse.levels import ENEMY_BASE_OFFSET, HEADER_LENGTH
from smb3parse.levels.level_header import LevelHeader
from smb3parse.util.rect import Rect

TIME_INF = -1

LEVEL_DEFAULT_HEIGHT = 27
LEVEL_DEFAULT_WIDTH = 16


def world_and_level_for_level_address(level_address: int):
    """Return the world and level numbers for a level address.

    Parameters
    ----------
    level_address : int
        ROM address of the level layout data.

    Returns
    -------
    tuple[int, int]
        SMB3 world number and level number for the address, or ``(-1, -1)`` if
        the address is not present in the loaded level-offset table.
    """
    for level in Level.offsets[1:]:
        if level.rom_level_offset == level_address:
            return level.game_world, level.level_in_world
    else:
        return -1, -1


class LevelSignaller(QObject):
    """Expose Qt signals emitted by a loaded level.

    :class:`Level` owns one signaller so non-Qt model code can notify views
    when parsed header data, object lists, jumps, or redraw state changes. It
    gives the ROM-facing level aggregate one stable Qt-facing event vocabulary
    while letting decode, mutation, and serialization stay out of direct
    widget code.

    Attributes
    ----------
    data_changed : SignalInstance
        Emitted when serialized level data or object lists change.
    jumps_changed : SignalInstance
        Emitted when jump pointer objects change.
    level_changed : SignalInstance
        Emitted after a different level payload is loaded.
    needs_redraw : SignalInstance
        Emitted when views should repaint the level.

    Notes
    -----
    The signaller keeps Qt wiring out of the ROM-facing level model while still
    giving views, commands, and dialogs a stable notification surface. That
    separation is what lets the same :class:`Level` aggregate participate in
    reload, undo, redraw, and serialization workflows without each subsystem
    reaching into another one's UI state directly. It is the long-lived event
    boundary that lets editor surfaces subscribe to level change without
    depending on how the level stores or mutates its decoded data internally.
    Future maintainers should preserve that narrow role: this object carries
    level lifecycle events, but it intentionally does not own level logic,
    reload policy, or command behavior itself.

    See Also
    --------
    Level
        Owns this signal bridge and emits these notifications as its decoded
        state changes.
    foundry.gui.visualization.level.LevelView
        Consumes redraw and data-change notifications from the active level.

    Examples
    --------
    Views and tool panels treat the signaller as the Qt-facing event surface
    for the ROM-backed level model::

        level = Level.from_bytes("Demo", object_set_number, layout_bytes, enemy_bytes)
        level.data_changed.connect(view.update)
        level.needs_redraw.connect(canvas.repaint)

    Narrower subscriptions let editor surfaces refresh only the state they
    own::

        level.level_changed.connect(header_panel.reload)
        level.jumps_changed.connect(jump_editor.refresh)

    The signaller also acts as the seam between command-driven edits and view
    updates::

        level.data_changed.connect(history_panel.sync)
        level.needs_redraw.connect(selection_overlay.repaint)
    """

    needs_redraw: SignalInstance = Signal()
    data_changed: SignalInstance = Signal()
    jumps_changed: SignalInstance = Signal()
    level_changed: SignalInstance = Signal()


class Level(LevelLike):
    """Model one editable SMB3 level payload.

    A level combines the nine-byte SMB3 level header, the object stream,
    optional jump pointers, and a separate enemy/item stream. The model keeps
    those byte-oriented structures synchronized with editor objects so the same
    instance can be loaded from ROM, imported from M3L/assembly data, edited,
    and serialized back out.

    Parameters
    ----------
    level_name : str, optional
        Display name for the level.
    layout_address : int, optional
        ROM address of the level or world map layout data.
    enemy_data_offset : int, optional
        ROM offset for enemy data.
    object_set_number : int, optional
        Object set number that selects graphics and object definitions.
    world_number : int, optional
        One-based SMB3 world number being processed.

    Attributes
    ----------
    MIN_LENGTH : int
        Smallest encoded level length accepted by the editor.
    WORLDS : int
        Number of world indexes loaded from the ROM offset table.
    _signal_emitter : LevelSignaller
        Qt signal owner used to notify views and dialogs.
    enemies : list[EnemyItem]
        Parsed enemy and item entries for the level.
    enemy_factory : EnemyItemFactory | None
        Enemy factory for the selected object set and enemy palette.
    enemy_item_factory : EnemyItemFactory | None
        Cached enemy factory used while parsing the enemy stream.
    enemy_offset : int
        ROM offset for the enemy/item data stream.
    enemy_size_on_disk : int
        Serialized enemy-stream length excluding the leading preserved byte.
    first_enemy_byte : int
        Leading enemy-stream byte preserved during serialization.
    header : LevelHeader
        Parsed view of the nine-byte SMB3 level header.
    header_bytes : bytearray
        Mutable raw header bytes edited by property setters.
    header_offset : int
        ROM offset for the level header and object stream.
    jumps : list[Jump]
        Parsed jump pointer objects embedded in the object stream.
    name : str
        Display name used by the editor.
    object_factory : LevelObjectFactory | None
        Level object factory for the selected object set, graphics set, and palette.
    object_offset : int
        ROM offset where object data starts after the header.
    object_set : foundry.game.ObjectSet.ObjectSet
        Object-set metadata used to decode terrain objects.
    object_set_number : int
        Numeric object-set id stored in the header and lookup tables.
    object_size_on_disk : int
        Serialized object-stream length excluding the header bytes.
    objects : list[foundry.game.gfx.objects.in_level.level_object.LevelObject]
        Parsed terrain/object entries from the level object stream.
    size : tuple[int, int]
        Level dimensions in blocks.
    sorted_offsets : list[Mario3Level]
        Loaded level-offset entries sorted by ROM layout address.
    world : int
        One-based world number when the source level is known.

    Notes
    -----
    ``Level`` is the editor's main aggregate for in-level data. It keeps the
    SMB3 header, object stream, jump stream, and enemy stream synchronized so a
    single model can move between ROM loading, interactive editing, ASM or M3L
    import, and serialization back to disk.
    """

    MIN_LENGTH = 0x10

    offsets, world_indexes = _load_level_offsets()
    sorted_offsets = sorted(offsets, key=lambda level: level.rom_level_offset)

    WORLDS = len(world_indexes)

    def __init__(
        self,
        level_name: str = "",
        layout_address: int = 0,
        enemy_data_offset: int = 0,
        object_set_number: int = 1,
        world_number: int = -1,
    ):
        """Load or prepare an SMB3 level model.

        Nonzero layout and enemy offsets load header, object, jump, and enemy
        data directly from the active ROM. A zero layout/enemy pair creates a
        placeholder instance that can later be populated from M3L, assembly, or
        explicit byte data. Construction also establishes the factories and
        bookkeeping that later tie header edits, decode reloads, save-safety
        checks, and serialization back to the same in-memory aggregate.

        Parameters
        ----------
        level_name : str, optional
            Display name for the level.
        layout_address : int, optional
            ROM address of the level or world map layout data.
        enemy_data_offset : int, optional
            ROM offset for enemy data.
        object_set_number : int, optional
            Object set number that selects graphics and object definitions.
        world_number : int, optional
            One-based SMB3 world number being processed.
        """
        object_set = ObjectSet.from_number(object_set_number)

        super(Level, self).__init__(object_set, layout_address)

        self._signal_emitter = LevelSignaller()

        self.name = level_name
        self.world = world_number
        """
        In which world map this level is situated. 0 means don't know. Might not always be known or level might be
        accessible from multiple worlds, so we only set it, if we know.
        """

        self.header_offset = layout_address
        self.object_offset = self.header_offset + HEADER_LENGTH
        self.enemy_offset = enemy_data_offset

        self.objects: list[LevelObject] = []
        self.header_bytes: bytearray = bytearray()
        self.jumps: list[Jump] = []
        self.enemies: list[EnemyItem] = []
        self.first_enemy_byte = 0x00

        if self.layout_address == self.enemy_offset == 0:
            # probably loaded to become an m3l
            self.size = (0, 0)
            self.header_bytes = bytearray(HEADER_LENGTH)
            self.header = LevelHeader(ROM(), self.header_bytes)
            self.object_factory: LevelObjectFactory | None = None
            self.enemy_factory: EnemyItemFactory | None = None
            return

        rom = ROM()

        self.header_bytes = rom.read(self.header_offset, HEADER_LENGTH)
        self._parse_header()

        object_data = ROM.rom_data[self.object_offset :]

        if self.enemy_offset == 0x0:
            enemy_data = bytearray()
        else:
            enemy_data = ROM.rom_data[self.enemy_offset :]

        self._load_level_data(object_data, enemy_data)

    def _load_level_data(self, object_data: bytearray, enemy_data: bytearray, new_level: bool = True):
        """Parse object and enemy streams into editor objects.

        This is the common decode path used by ROM loading, reloads, M3L
        imports, and byte-level restores. It repopulates the object, jump, and
        enemy lists before optionally refreshing the saved-size baseline.

        Parameters
        ----------
        object_data : bytearray
            Raw object stream beginning after the level header.
        enemy_data : bytearray
            Raw enemy/item stream.
        new_level : bool, optional
            Whether to update saved-size bookkeeping and emit ``data_changed``.
        """
        self._load_objects(object_data)
        self._load_enemies(enemy_data)

        if new_level:
            self._update_level_size()

            self.data_changed.emit()

    @property
    def fully_loaded(self):
        """Indicate that this instance already owns a decoded SMB3 payload.

        ``Level`` can start life as a detached placeholder for M3L import,
        byte-stream restore, or later ROM attachment. The editor uses this gate
        before enabling view, save, and header workflows that expect parsed
        header bytes and factories to exist.

        Returns
        -------
        bool
            ``True`` when header bytes have been loaded.
        """
        # objects, enemies and jumps could be empty, but there are always 9 header bytes, when a level is loaded
        return bool(self.header_bytes)

    @property
    def attached_to_rom(self):
        """Whether the level still points at ROM-backed object and enemy data.

        Detached levels behave like imported M3L data until a save or attach
        command assigns fresh ROM addresses.

        Returns
        -------
        bool
            ``True`` when both header and enemy streams have ROM offsets.
        """
        return not (self.header_offset == self.enemy_offset == 0)

    def detach_from_rom(self):
        """Mark the level as detached from ROM storage.

        Detached levels serialize like imported M3L data until new ROM addresses
        are assigned.
        """
        self.header_offset = self.enemy_offset = 0

    @property
    def width(self):
        """Expose the decoded horizontal block span of the level.

        Views and geometry helpers read this cached dimension instead of
        unpacking header state directly.

        Returns
        -------
        int
            Width decoded from the level header.
        """
        return self.size[0]

    @property
    def height(self):
        """Expose the decoded vertical block span of the level.

        This cached dimension keeps painting, hit testing, and save warnings in
        sync with the most recently parsed header.

        Returns
        -------
        int
            Height decoded from the level header.
        """
        return self.size[1]

    @property
    def needs_redraw(self):
        """Expose the signal that asks views to repaint this level.

        Editor widgets connect to this instead of polling for visual changes in
        the decoded level state.

        Returns
        -------
        SignalInstance
            Signal emitted when views should repaint.
        """
        return self._signal_emitter.needs_redraw

    @property
    def data_changed(self):
        """Expose the signal emitted when editable level data changes.

        Lists, size bars, viewers, and autosave logic all use this shared
        notification instead of tracking individual mutation sites.

        Returns
        -------
        SignalInstance
            Signal emitted when editable level data changes.
        """
        return self._signal_emitter.data_changed

    @property
    def jumps_changed(self):
        """Expose the signal emitted after jump metadata changes.

        Jump editors, jump lists, and jump-overlay rendering use this narrower
        signal so they can refresh jump-specific state without rebuilding every
        widget that listens to the broader level-data stream.

        Returns
        -------
        SignalInstance
            Signal emitted when jump pointers change.
        """
        return self._signal_emitter.jumps_changed

    @property
    def level_changed(self):
        """Expose the signal emitted after a different level payload is loaded.

        GUI shells use this boundary when the active level identity changes and
        widgets need to rebuild around new addresses, factories, header state,
        and cached metadata instead of treating the change like an in-place edit.

        Returns
        -------
        SignalInstance
            Signal emitted after a different level payload is loaded.
        """
        return self._signal_emitter.level_changed

    def reload(self):
        """Reparse the level from its serialized in-memory streams.

        Header edits such as graphics-set, palette, or orientation changes can
        invalidate already-decoded objects and enemies. This helper
        reserializes the live in-memory state, reparses the header, rebuilds
        factories, and decodes fresh editor objects without changing ROM
        addresses or saved-size bookkeeping.
        """
        (_, header_and_object_data), (_, enemy_data) = self.to_bytes()

        self.header_bytes = header_and_object_data[:HEADER_LENGTH]

        object_data = header_and_object_data[HEADER_LENGTH:]

        self._parse_header()
        self._load_level_data(object_data, enemy_data, new_level=False)

        self.data_changed.emit()

    def current_object_size(self):
        """Compute the serialized byte size of objects and jumps.

        Save validation compares this live value against the last saved object
        budget to decide whether the level still fits in its ROM allocation.

        Returns
        -------
        int
            Number of bytes needed for the object stream, excluding the terminator.
        """
        size = 0

        for obj in self.objects:
            if obj.is_4byte:
                size += 4
            else:
                size += 3

        size += Jump.SIZE * len(self.jumps)

        return size

    def current_enemies_size(self):
        """Compute the serialized byte size of enemies and items.

        Save validation compares this live value against the last saved enemy
        budget to decide whether the level still fits in its ROM allocation.

        Returns
        -------
        int
            Number of bytes needed for enemy/item entries, excluding stream markers.
        """
        return len(self.enemies) * ENEMY_SIZE

    def _parse_header(self, should_emit=True):
        """Refresh header-derived factories and dimensions.

        Parameters
        ----------
        should_emit : bool, optional
            Whether to emit ``data_changed`` after parsing.
        """
        self.header = LevelHeader(ROM(), self.header_bytes)

        self.object_factory = LevelObjectFactory(
            self.object_set_number,
            self.header.graphic_set_index,
            self.header.object_palette_index,
            self.objects,
            self.header.is_vertical,
        )
        self.enemy_item_factory = EnemyItemFactory(self.object_set_number, self.header.enemy_palette_index)

        self.size = self.header.width, self.header.height

        if should_emit:
            self.data_changed.emit()

    def _load_enemies(self, data: bytearray):
        """Parse SMB3 enemy and item data.

        The first byte is preserved as stream metadata, then fixed-width enemy
        records are decoded until the stream terminator is reached.

        Parameters
        ----------
        data : bytearray
            Enemy stream whose first byte is preserved and whose entries are
            fixed-width ``ENEMY_SIZE`` chunks terminated by ``0xFF``.

        Returns
        -------
        None
            This method repopulates ``self.enemies`` in place.
        """
        if not data:
            return

        self.enemies.clear()

        def data_left(_data: bytearray):
            """Return whether enemy data remains to be parsed.

            Parameters
            ----------
            _data : bytearray
                Enemy data chunk being checked for an end marker.

            Returns
            -------
            bool
                ``True`` when the chunk contains data and does not start with
                the enemy data terminator.
            """
            # the commented out code seems to hold for the stock ROM, but if the ROM was already edited with another
            # editor, it might not, since they only wrote the 0xFF to end the enemy data

            return _data and not _data[0] == 0xFF  # and _data[1] in [0x00, 0x01]

        self.first_enemy_byte = data[0]
        data = data[1:]

        enemy_data, data = data[0:ENEMY_SIZE], data[ENEMY_SIZE:]

        while data_left(enemy_data):
            enemy = self.enemy_item_factory.from_data(enemy_data, 0)

            self.enemies.append(enemy)

            enemy_data, data = data[0:ENEMY_SIZE], data[ENEMY_SIZE:]

    def _load_objects(self, data: bytearray):
        """Parse SMB3 level objects and jump pointers.

        Parameters
        ----------
        data : bytearray
            Object stream made of three- or four-byte entries terminated by
            ``0xFF``.
        """
        if self.object_factory is None:
            return

        self.objects.clear()
        self.jumps.clear()

        if not data or data[0] == 0xFF:
            return

        while True:
            potential_obj_data = data[0:4]

            level_object = self.object_factory.from_data(potential_obj_data, -1)

            data = data[3:]

            if level_object.is_4byte:
                data.pop(0)

            if isinstance(level_object, LevelObject):
                self.objects.append(level_object)
            elif isinstance(level_object, Jump):
                self.jumps.append(level_object)

            if data[0] == 0xFF:
                break

    def _update_level_size(self):
        """Record current serialized stream sizes as the saved baseline.

        The editor compares against these values to detect whether edited data
        no longer fits in the original ROM allocation.
        """
        self.object_size_on_disk = self.current_object_size()
        self.enemy_size_on_disk = self.current_enemies_size()

    def get_rect(self, block_length: int = 1):
        """Translate decoded level bounds into rectangle math.

        The editor uses this rectangle as the common geometry bridge between
        SMB3 header-derived dimensions and Qt-independent hit-testing, warning,
        and rendering helpers. Views, overlay drawers, and save-warning checks
        all derive their shared panel bounds from this one decoded rectangle.

        Parameters
        ----------
        block_length : int, optional
            Scale factor applied to the block dimensions.

        Returns
        -------
        Rect
            Rectangle covering the level from origin to scaled width and height.
        """
        width, height = self.size

        return Rect(0, 0, width * block_length, height * block_length)

    def set_addresses(self, header_offset: int, enemy_item_offset: int):
        """Store the ROM addresses for the level and enemy streams.

        Attach commands and managed-level workflows call this when a detached
        level is assigned concrete ROM storage again.

        Parameters
        ----------
        header_offset : int
            ROM offset for the level header.
        enemy_item_offset : int
            ROM offset for enemy and item data.
        """
        self.header_offset = header_offset
        self.object_offset = self.header_offset + HEADER_LENGTH
        self.enemy_offset = enemy_item_offset

    def was_saved(self):
        """Update saved-size bookkeeping after a successful save.

        Subsequent capacity checks compare edits against the newly saved byte
        counts.
        """
        self._update_level_size()

    @property
    def objects_end(self):
        """Expose the ROM address immediately after the object stream.

        This includes the header, serialized objects and jumps, and the object
        delimiter byte used by the SMB3 level format.

        Returns
        -------
        int
            End offset for header, objects, jumps, and object terminator.
        """
        return (
            self.header_offset + HEADER_LENGTH + self.current_object_size() + LEVEL_DATA_DELIMITER_COUNT
        )  # the delimiter

    @property
    def enemies_end(self):
        """Expose the ROM address immediately after the enemy stream.

        The result includes all serialized enemy records and the terminator
        bytes used by SMB3 enemy data.

        Returns
        -------
        int
            End offset for enemy entries and their terminator bytes.
        """
        return self.enemy_offset + self.current_enemies_size() + len(b"\xff\x00")  # the delimiter

    @property
    def next_area_objects(self):
        """Expose the ROM layout address targeted by the next-area pointer.

        This is the object-data side of SMB3's "jump to another area" header
        state, and UI editors use it when following or editing level
        destinations.

        Returns
        -------
        int
            Absolute ROM address for the next area's layout data.
        """
        return self.header.jump_level_address

    # TODO: Rename to from Next Area to Jump (Destination)
    @next_area_objects.setter
    def next_area_objects(self, value):
        """Store the layout address reached by the next-area pointer.

        Parameters
        ----------
        value : int
            Absolute ROM address for the next area's layout data.
        """
        if value == self.header.jump_level_address:
            return

        value -= self.header.jump_object_set.level_offset

        self.header_bytes[0] = 0x00FF & value
        self.header_bytes[1] = value >> 8

        self._parse_header()

    @property
    def has_next_area(self):
        """Indicate that the header currently points at another SMB3 area.

        Foundry treats the first two header bytes as the high-level gate for
        next-area workflows. If they are zero, jump editing and destination
        navigation stay disabled even if jump objects are present elsewhere in
        the level data.

        Returns
        -------
        bool
            ``True`` when the first two header bytes contain a nonzero pointer.
        """
        return self.header_bytes[0] + self.header_bytes[1] != 0

    @property
    def next_area_enemies(self):
        """Expose the enemy-stream address paired with the next-area header.

        SMB3 stores the destination layout stream and destination enemy stream
        separately. Foundry keeps both values visible so level navigation and
        save workflows can preserve a coherent destination pair.

        Returns
        -------
        int
            Absolute ROM address for the next area's enemy/item data.
        """
        return self.header.jump_enemy_address

    @next_area_enemies.setter
    def next_area_enemies(self, value):
        """Store the enemy-data address reached by the next-area pointer.

        Parameters
        ----------
        value : int
            Absolute ROM address for the next area's enemy/item data.
        """
        if value == self.header.jump_enemy_address:
            return

        value -= ENEMY_BASE_OFFSET

        self.header_bytes[2] = 0x00FF & value
        self.header_bytes[3] = value >> 8

        self._parse_header()

    @property
    def start_y_index(self):
        """Expose the header bits that choose Mario's start row.

        The raw index is later combined with start-action state to derive the
        visible candidate positions previewed by ``LevelDrawer`` and edited
        through ``LevelView``.

        Returns
        -------
        int
            Header value selecting the player start row.
        """
        return self.header.start_y_index

    @start_y_index.setter
    def start_y_index(self, index):
        """Store the encoded vertical player start index.

        Parameters
        ----------
        index : int
            Header value selecting the player start row.
        """
        if index == self.header.start_y_index:
            return

        self.header_bytes[4] &= 0b0001_1111
        self.header_bytes[4] |= index << 5

        self._parse_header()

    # bit 4 unused

    @property
    def length(self):
        """Expose the decoded horizontal span described by the header bits.

        Foundry exposes the already-decoded length rather than the packed nibble
        stored in byte four so views, size bars, and save checks can work in
        screen/block units instead of raw header math.

        Returns
        -------
        int
            Length decoded from the level-size bits of the header.
        """
        return self.header.length

    @length.setter
    def length(self, length):
        """Store the level length in screens.

        This updates the encoded header byte that controls how many screens the level spans.

        Parameters
        ----------
        length : int
            Number of screens the level should have.
        """

        if length == self.header.length:
            return

        # screens are 0 indexed, minimum is 1
        self.header_bytes[4] &= 0b1111_0000
        self.header_bytes[4] |= (length // 0x10) - 1

        self._parse_header()

    # bit 1 unused

    @property
    def start_x_index(self):
        """Expose the header bits that choose Mario's start column.

        Together with ``start_y_index`` and ``start_action`` this value drives
        the Mario-position previews and undoable start-position edits in the
        canvas. The getter keeps that shared header state visible to both the
        view preview path and the command layer that later rewrites header
        bytes.

        Returns
        -------
        int
            Header value selecting the player start column.
        """
        return self.header.start_x_index

    @start_x_index.setter
    def start_x_index(self, index):
        """Store the encoded horizontal player start index.

        Parameters
        ----------
        index : int
            Header value selecting the player start column.
        """
        if index == self.header.start_x_index:
            return

        self.header_bytes[5] &= 0b1001_1111
        self.header_bytes[5] |= index << 5

        self._parse_header()

    @property
    def enemy_palette_index(self):
        """Expose the enemy palette bits stored in the SMB3 header.

        Enemy/item decoding and preview rendering both depend on this field, so
        the value is exposed in decoded form rather than as a masked header
        nibble. Header editors read it, and setter-driven header edits feed it
        back into enemy decoding through ``_parse_header`` before canvases and
        viewers repaint enemy graphics. In practice this property is the read
        boundary between raw SMB3 header bits and the higher-level editor code
        that needs one stable palette-group value for enemy factories,
        previews, and header widgets.

        Returns
        -------
        int
            Palette index used by enemy and item rendering.
        """
        return self.header.enemy_palette_index

    @enemy_palette_index.setter
    def enemy_palette_index(self, index):
        """Store the enemy palette group index.

        Parameters
        ----------
        index : int
            Palette index used by enemy and item rendering.
        """
        if index == self.header.enemy_palette_index:
            return

        self.header_bytes[5] &= 0b1110_0111
        self.header_bytes[5] |= index << 3

        self._parse_header()

    @property
    def object_palette_index(self):
        """Expose the object palette bits stored in the SMB3 header.

        This field affects how terrain objects are rendered and, for some
        definitions, how object graphics are interpreted. Foundry therefore
        reloads decoded objects after edits to keep rendered tiles and object
        factories aligned.

        Returns
        -------
        int
            Palette index used by terrain and level-object rendering.
        """
        return self.header.object_palette_index

    @object_palette_index.setter
    def object_palette_index(self, index):
        """Store the object palette group index and reload decoded objects.

        Parameters
        ----------
        index : int
            Palette index used by terrain and level-object rendering.
        """
        if index == self.header.object_palette_index:
            return

        self.header_bytes[5] &= 0b1111_1000
        self.header_bytes[5] |= index

        self._parse_header()

        self.reload()

    @property
    def pipe_ends_level(self):
        """Indicate that pipe entry is encoded as a level-ending transition.

        This bit is part of the broader level-entry/exit behavior encoded in
        the header rather than a standalone pipe object property, so the editor
        exposes it through the level model and rewrites it through the same
        header-edit workflow as the other decode-affecting level flags.

        Returns
        -------
        bool
            ``True`` when pipe entry is encoded as a level-ending action.
        """
        return self.header.pipe_ends_level

    @pipe_ends_level.setter
    def pipe_ends_level(self, truth_value):
        """Store whether entering a pipe ends the level.

        Parameters
        ----------
        truth_value : bool
            Whether pipe entry should end the level.
        """
        if truth_value == self.header.pipe_ends_level:
            return

        self.header_bytes[6] &= 0b0111_1111
        self.header_bytes[6] |= int(not truth_value) << 7

        self._parse_header()

    @property
    def scroll_type(self):
        """Expose the SMB3 scroll-mode bits stored in the header.

        The raw index is shared by header editors, save workflows, and any
        logic that needs to preserve the level's intended scrolling behavior
        without re-deriving it from bytes.

        Returns
        -------
        int
            Header index controlling level scrolling behavior.
        """
        return self.header.scroll_type_index

    @scroll_type.setter
    def scroll_type(self, index):
        """Store the encoded scroll-type index.

        Parameters
        ----------
        index : int
            Header index controlling level scrolling behavior.
        """
        if index == self.header.scroll_type_index:
            return

        self.header_bytes[6] &= 0b1001_1111
        self.header_bytes[6] |= index << 5

        self._parse_header()

    @property
    def is_vertical(self):
        """Indicate that the header marks this layout as vertical.

        The flag changes object decoding, enemy ordering, jump geometry, and
        screen-grid interpretation, so the editor treats it as a structural
        decode setting rather than a cosmetic property. Views, object
        factories, and save/export paths all branch on this one decoded flag.

        Returns
        -------
        bool
            ``True`` when the vertical-level header flag is set.
        """
        return self.header.is_vertical

    @is_vertical.setter
    def is_vertical(self, truth_value):
        """Store whether the level is vertically oriented.

        Parameters
        ----------
        truth_value : bool
            Whether to set the vertical-level header flag.
        """
        if truth_value == self.header.is_vertical:
            return

        self.header_bytes[6] &= 0b1110_1111
        self.header_bytes[6] |= int(truth_value) << 4

        self._parse_header()

    @property
    def next_area_object_set_no(self):
        """Expose the destination-area object set stored in the header.

        SMB3 decodes the next area's object stream with this object set, so
        Foundry surfaces it alongside the next-area addresses to keep jump
        navigation and save workflows aligned with the destination decode
        contract.

        Returns
        -------
        int
            Header value selecting the object set for the jump destination.
        """
        return self.header.jump_object_set_number

    @next_area_object_set_no.setter
    def next_area_object_set_no(self, index):
        """Store the object set used by the next area.

        Parameters
        ----------
        index : int
            Header value selecting the object set for the jump destination.
        """
        if index == self.header.jump_object_set_number:
            return

        self.header_bytes[6] &= 0b1111_0000
        self.header_bytes[6] |= index

        self._parse_header()

    @property
    def start_action(self):
        """Expose the SMB3 start-action bits stored in the header.

        These bits choose which Mario entry animation/path is used and which
        candidate start positions are valid for drag-preview workflows.

        Returns
        -------
        int
            Header value controlling how the player enters the level.
        """
        return self.header.start_action

    @start_action.setter
    def start_action(self, index):
        """Store the encoded player entry action.

        Parameters
        ----------
        index : int
            Header value controlling how the player enters the level.
        """
        if index == self.header.start_action:
            return

        self.header_bytes[7] &= 0b0001_1111
        self.header_bytes[7] |= index << 5

        self._parse_header()

    @property
    def graphic_set(self):
        """Expose the graphics-set bits stored in the header.

        Object factories and rendered previews both depend on this value, so
        edits trigger a reload of decoded objects after the header is updated.

        Returns
        -------
        int
            Header value selecting CHR/TSA graphics for level objects.
        """
        return self.header.graphic_set_index

    @graphic_set.setter
    def graphic_set(self, index):
        """Store the graphics set index and reload decoded objects.

        Parameters
        ----------
        index : int
            Header value selecting CHR/TSA graphics for level objects.
        """
        if index == self.header.graphic_set_index:
            return

        self.header_bytes[7] &= 0b1110_0000
        self.header_bytes[7] |= index

        self._parse_header()

        self.reload()

    @property
    def time_index(self):
        """Expose the timer-selection bits stored in the level header.

        The decoded value is what dialogs and serialization code care about;
        callers should not need to unpack the shared header byte themselves.
        The value stays on the level model so header editors, save code, and
        assembly export all read the same decoded timer selection.

        Returns
        -------
        int
            Header value selecting the level timer.
        """
        return self.header.time_index

    @time_index.setter
    def time_index(self, index):
        """Store the encoded timer index.

        Parameters
        ----------
        index : int
            Header value selecting the level timer.
        """
        if index == self.header.time_index:
            return

        self.header_bytes[8] &= 0b0011_1111
        self.header_bytes[8] |= index << 6

        self._parse_header()

    # bit 3 and 4 unused

    @property
    def music_index(self):
        """Expose the music-selection bits stored in the level header.

        Foundry keeps the decoded value exposed so header editors and exports
        can preserve the level's music choice without byte masking logic.

        Returns
        -------
        int
            Header value selecting level music.
        """
        return self.header.music_index

    @music_index.setter
    def music_index(self, index):
        """Store the encoded music index.

        Parameters
        ----------
        index : int
            Header value selecting level music.
        """
        if index == self.header.music_index:
            return

        self.header_bytes[8] &= 0b1111_0000
        self.header_bytes[8] |= index

        self._parse_header()

    def is_too_big(self):
        """Flag edited data that no longer fits the last saved allocation.

        Foundry tracks object/jump bytes and enemy/item bytes separately
        because SMB3 stores them in different ROM regions. This helper is the
        high-level save-safety gate used by warnings and save prompts.

        Returns
        -------
        bool
            ``True`` when object/jump data or enemy/item data exceeds its saved baseline.
        """
        return self.too_many_level_objects() or self.too_many_enemies_or_items()

    def too_many_level_objects(self):
        """Flag object and jump bytes that exceed their saved allocation.

        The comparison is against the last persisted size baseline, not against
        an abstract global limit, because unmanaged ROM levels can only grow
        until they collide with neighboring data.

        Returns
        -------
        bool
            ``True`` when serialized object data exceeds the saved object-stream size.
        """
        return self.current_object_size() > self.object_size_on_disk

    def too_many_enemies_or_items(self):
        """Flag enemy/item bytes that exceed their saved allocation.

        Enemy data is stored separately from layout data in SMB3, so this check
        runs independently from the object-stream capacity check.

        Returns
        -------
        bool
            ``True`` when serialized enemy/item data exceeds the saved enemy-stream size.
        """
        return self.current_enemies_size() > self.enemy_size_on_disk

    def get_all_objects(self) -> list[InLevelObject]:
        """Build the flat selection list for the level editor.

        The combined list is the shared selection surface used by views, object
        lists, clipboard operations, warning highlighting, and undo commands
        that need one flat index space across the separate object and enemy
        streams. This method is therefore the normalization point between
        SMB3's split serialization model and the editor's interaction model:
        the ROM keeps terrain objects and enemies in separate streams, but
        selection, hit testing, and clipboard workflows consume one merged
        sequence.

        Returns
        -------
        list[InLevelObject]
            Combined terrain-object and enemy/item list used by selection code.

        Examples
        --------
        View and clipboard code can iterate one merged editor surface instead
        of coordinating two backing lists::

            for obj in level.get_all_objects():
                handle(obj)
        """
        return cast("list[InLevelObject]", self.objects) + cast("list[InLevelObject]", self.enemies)

    def object_at(self, x: int, y: int) -> InLevelObject | None:
        """Resolve block-space hit testing against the flat selection surface.

        The search walks the combined selection list in reverse so hit testing
        matches the visual draw order humans see in the editor across both the
        terrain-object stream and the separate enemy/item stream.

        Parameters
        ----------
        x : int
            Block x coordinate.
        y : int
            Block y coordinate.

        Returns
        -------
        InLevelObject | None
            Frontmost object at that block coordinate, if one exists.
        """
        for obj in reversed(self.get_all_objects()):
            if obj.point_in(x, y):
                return obj
        else:
            return None

    def bring_to_foreground(self, objects: list[InLevelObject]):
        """Move objects forward within their own serialized draw domain.

        Level objects and enemies are stored in separate lists, so reordering
        only happens against overlapping objects of the same kind. The helper
        preserves each list's serialized order while matching the foreground
        move the user expects from the editor.

        Parameters
        ----------
        objects : list[InLevelObject]
            Level objects or enemy/items to reorder.

        Raises
        ------
        TypeError
            If any object is neither a level object nor an enemy/item.
        """
        for obj in objects:
            intersecting_objects = self.get_intersecting_objects(obj)

            object_currently_in_the_foreground: InLevelObject = intersecting_objects[-1]

            if obj is object_currently_in_the_foreground:
                continue

            if isinstance(obj, LevelObject):
                other_objects = cast("list[InLevelObject]", self.objects)
            elif isinstance(obj, EnemyItem):
                other_objects = cast("list[InLevelObject]", self.enemies)
            else:
                raise TypeError(f"How did you select an object of type: {type(obj)}")

            other_objects.remove(obj)

            index = other_objects.index(object_currently_in_the_foreground) + 1

            other_objects.insert(index, obj)

        self.data_changed.emit()

    def bring_to_background(self, level_objects: list[InLevelObject]):
        """Move objects backward within their own serialized draw domain.

        Like ``bring_to_foreground``, this only reorders against overlapping
        objects in the same backing list so the level-object stream and
        enemy-item stream stay internally coherent.

        Parameters
        ----------
        level_objects : list[InLevelObject]
            Level objects or enemy/items to reorder.

        Raises
        ------
        TypeError
            If any object is neither a level object nor an enemy/item.
        """
        for obj in level_objects:
            intersecting_objects = self.get_intersecting_objects(obj)

            object_currently_in_the_background: InLevelObject = intersecting_objects[0]

            if obj is object_currently_in_the_background:
                continue

            # TODO make into method to save on cast calls
            if isinstance(obj, LevelObject):
                objects = cast("list[InLevelObject]", self.objects)
            elif isinstance(obj, EnemyItem):
                objects = cast("list[InLevelObject]", self.enemies)
            else:
                raise TypeError()

            objects.remove(obj)

            index = objects.index(object_currently_in_the_background)

            objects.insert(index, obj)

    def get_intersecting_objects(self, obj: InLevelObject) -> list[InLevelObject]:
        """Resolve same-stream overlap for ordering and collision workflows.

        This centralizes overlap checks for selection, movement, and validation
        while preserving memory order from back to front. Level objects are only
        compared with level objects, and enemy/items are only compared with
        enemy/items. That keeps overlap results aligned with the stream that
        later ordering operations mutate, so foreground/background commands and
        movement validation never mix unrelated serialization domains.

        Parameters
        ----------
        obj : InLevelObject
            Object whose rectangle is used for the overlap check.

        Returns
        -------
        list[InLevelObject]
            Overlapping objects in their current draw/order list.

        Raises
        ------
        TypeError
            If ``obj`` is neither a level object nor an enemy/item.
        """
        if isinstance(obj, LevelObject):
            objects_to_check = cast("list[InLevelObject]", self.objects)
        elif isinstance(obj, EnemyItem):
            objects_to_check = cast("list[InLevelObject]", self.enemies)
        else:
            raise TypeError()

        intersecting_objects: list[InLevelObject] = [
            other_object for other_object in objects_to_check if obj.get_rect().intersects(other_object.get_rect())
        ]

        return intersecting_objects

    def draw(self, *_):
        """Satisfy the ``LevelLike`` drawing interface.

        Concrete level drawing is handled by view/drawer classes, so the model
        implementation intentionally does nothing.

        Parameters
        ----------
        *_ : object
            Ignored drawing arguments.
        """
        pass

    def paste_object_at(self, pos: Position, obj: ObjectLike) -> ObjectLike | None:
        """Create a pasted copy of an editor object at a new level position.

        Clipboard paste preserves the source object's identifying SMB3 fields
        while letting the level decide how that kind of object should be added
        to the terrain or enemy stream at the destination coordinate.

        Parameters
        ----------
        pos : Position
            Destination position for the pasted object.
        obj : ObjectLike
            Source object whose type and identifying fields should be copied.

        Returns
        -------
        ObjectLike | None
            New object or enemy/item, or ``None`` for unsupported object types.
        """
        if isinstance(obj, EnemyItem):
            return self.add_enemy(obj.obj_index, pos)

        elif isinstance(obj, LevelObject):
            if obj.is_4byte:
                length: int | None = obj.length
            else:
                length = None

            return self.add_object(obj.domain, obj.obj_index, pos, length)

        return None

    def add_object(
        self, domain: int, object_index: int, pos: Position, length: int | None, index: int = -1
    ) -> LevelObject | None:
        """Add a terrain object to the decoded object stream.

        The helper routes creation through the active ``LevelObjectFactory`` so
        the new editor object uses the loaded object set, graphics set,
        palette, and vertical-level interpretation. The object is inserted into
        the live decoded list immediately; higher-level commands decide whether
        that mutation is part of an undo step, a paste macro, or a direct load
        path. This makes the method the object-stream insertion boundary for
        live editor state: once the factory has decoded the new object
        shape, the method places it into the in-memory terrain list in the same
        order later redraw, selection, and serialization code will observe.

        Parameters
        ----------
        domain : int
            Object domain that determines how the object is interpreted.
        object_index : int
            Object type index within the domain.
        pos : Position
            Block position for the new object.
        length : int | None
            Encoded length for four-byte objects, or ``None`` for three-byte objects.
        index : int, optional
            Insertion index in the object list, or ``-1`` to append.

        Returns
        -------
        foundry.game.gfx.objects.in_level.level_object.LevelObject | None
            Created object, or ``None`` if no object factory is available.

        Examples
        --------
        Paste and command workflows use this helper once they have chosen a
        destination position and object identity::

            new_obj = level.add_object(domain, object_index, pos, length)
        """
        if index == -1:
            index = len(self.objects)

        if self.object_factory:
            x, y = pos.xy
            obj = self.object_factory.from_properties(domain, object_index, x, y, length, index)
            self.objects.insert(index, obj)

            return obj

        return None

    def add_enemy(self, enemy_type: int, pos: Position, index: int = -1) -> EnemyItem:
        """Add an enemy or item to the decoded enemy stream.

        When no insertion index is supplied, Foundry chooses a stable order
        that mirrors SMB3's axis-sensitive enemy serialization: vertical levels
        sort primarily by Y, horizontal levels by X. That keeps redraw order,
        later serialization, and save-size accounting aligned with the stream
        layout the game expects.

        Parameters
        ----------
        enemy_type : int
            Enemy type identifier to place.
        pos : Position
            Block position for the new enemy or item.
        index : int, optional
            Insertion index, or ``-1`` to choose an order based on level orientation.

        Returns
        -------
        EnemyItem
            Enemy or item added to the level.
        """
        new_enemy = self.enemy_item_factory.from_data(bytearray([enemy_type, *pos.xy]), -1)

        if index == -1:
            index = 0

            # find an index based on the position
            if self.is_vertical:
                for idx, other_enemy in enumerate(self.enemies):
                    index = idx

                    if other_enemy.y_position > new_enemy.y_position:
                        break

            else:
                for idx, other_enemy in enumerate(self.enemies):
                    index = idx

                    if other_enemy.x_position > new_enemy.x_position:
                        break

        self.enemies.insert(index, new_enemy)

        return new_enemy

    def index_of(self, obj: InLevelObject) -> int:
        """Map an in-level object to the flat selection index space.

        ``ObjectList`` and other shared selection tools treat objects and
        enemies as one combined list even though they live in different backing
        streams, so this method provides the shared index mapping between those
        UI surfaces and the two serialized SMB3 data lists.

        Parameters
        ----------
        obj : InLevelObject
            Level object or enemy/item to locate.

        Returns
        -------
        int
            Index of the object in the collection.

        Raises
        ------
        TypeError
            If ``obj`` is neither a level object nor an enemy/item.
        """
        if isinstance(obj, LevelObject):
            return self.objects.index(obj)
        elif isinstance(obj, EnemyItem):
            return len(self.objects) + self.enemies.index(obj)
        else:
            raise TypeError("Given Object was not EnemyObject or LevelObject.")

    def get_object(self, index: int):
        """Map a flat selection index back to a decoded level object.

        The first segment of the index space addresses level objects; the
        second segment addresses the separate enemy/item stream. Object lists,
        warning panels, and undo replay use this mapping to move from a flat UI
        index back to the correct decoded backing object.

        Parameters
        ----------
        index : int
            Index into objects first, then enemies/items.

        Returns
        -------
        InLevelObject
            Level object or enemy/item at that combined-list index.
        """
        if index < len(self.objects):
            return self.objects[index]
        else:
            return self.enemies[index % len(self.objects)]

    def clear_selection(self):
        """Clear selection state on every level object and enemy/item.

        Emits ``data_changed`` so views refresh their selection overlays.
        """
        for obj in self.get_all_objects():
            obj.selected = False

        self.data_changed.emit()

    def remove_object(self, obj: InLevelObject):
        """Remove an object or enemy/item from the level.

        Parameters
        ----------
        obj : InLevelObject
            Object to remove from its backing list.
        """
        if obj is None:
            return

        if isinstance(obj, LevelObject):
            self.objects.remove(obj)
        elif isinstance(obj, EnemyItem):
            self.enemies.remove(obj)

    def to_m3l(self) -> bytearray:
        """Serialize the level to Foundry's detached M3L container.

        M3L packages world/object-set metadata, the raw SMB3 header and object
        stream, jump data, and the separate enemy stream so a level can be
        edited outside the ROM and later reattached.

        Returns
        -------
        bytearray
            M3L payload containing metadata, header, objects, jumps, and enemies.
        """
        m3l_bytes = bytearray()

        m3l_bytes.append(self.world)
        m3l_bytes.append(0)  # Level number based on vanilla level list of SMB3 Workshop
        m3l_bytes.append(self.object_set_number)

        m3l_bytes.extend(self.header_bytes)

        for obj in self.objects:
            m3l_bytes.extend(obj.to_bytes())

        for jump in self.jumps:
            m3l_bytes.extend(jump.to_bytes())

        # level data delimiter
        m3l_bytes.append(0xFF)

        # at the start of enemy data; no idea what for
        m3l_bytes.append(self.first_enemy_byte)

        for enemy in sorted(self.enemies, key=lambda _enemy: _enemy.x_position):
            m3l_bytes.extend(enemy.to_bytes())

        # enemy data delimiter
        m3l_bytes.append(0xFF)

        return m3l_bytes

    def to_asm(self) -> tuple[str, str]:
        """Serialize the level as assembly-ready object and enemy sources.

        Foundry exports the layout/jump stream and the enemy stream as separate
        assembly blobs because SMB3 stores and assembles them independently.

        Returns
        -------
        tuple[str, str]
            Level/object assembly source and enemy/item assembly source.
        """
        return self._level_asm(), self._enemy_asm()

    def _enemy_asm(self):
        """Serialize the active enemy/item stream as assembly source.

        The output preserves Foundry's current enemy ordering and includes the
        leading preserved byte plus the SMB3 terminator expected by enemy data
        imports.

        Returns
        -------
        str
            ``.byte`` lines for enemy/item data and its terminator.
        """
        ret_lines: list[str] = []

        ret_lines.append(f"\t.byte {bytes_to_asm(0x01)}\t\t\t; Unused byte, set to $01")

        for enemy in self.enemies:
            ret_lines.append(f"\t.byte {bytes_to_asm(enemy.to_bytes())}\t; {enemy.name} @ {enemy.get_position()}")

        ret_lines.append(f"\t.byte {bytes_to_asm(0xFF)}\t; Terminator")

        return "\n".join(ret_lines)

    def _level_asm(self):
        """Serialize the layout-side level stream as assembly source.

        The header comments keep the packed SMB3 byte layout visible so the
        export remains understandable to humans comparing editor state with
        disassembly or hand-written assembly files.

        Returns
        -------
        str
            ``.byte`` lines for header bytes, objects, jumps, and terminator.
        """
        ret_lines: list[str] = []

        object_set_offset = (
            ROM().int(Constants.OFFSET_BY_OBJECT_SET_A000 + self.object_set.number) * OFFSET_SIZE - 10
        ) * 0x1000

        level_offset = (self.layout_address - BASE_OFFSET - object_set_offset) & 0xFFFF

        ret_lines.append(f"; Original address was ${level_offset:04X}")
        ret_lines.append(f"; {self.name}'s layout data")

        ret_lines.append(f"\t.byte {bytes_to_asm(self.header_bytes[0:2])}\t\t\t ; Next Area Layout Offset")
        ret_lines.append(f"\t.byte {bytes_to_asm(self.header_bytes[2:4])}\t\t\t ; Next Area Enemy & Item Offset")
        ret_lines.append(f"\t.byte {bytes_to_asm(self.header_bytes[4])}\t\t\t\t ; Level Size Index | Y-Start Index")
        ret_lines.append(
            f"\t.byte {bytes_to_asm(self.header_bytes[5])}\t\t\t\t ; BG Pal | Enemy Pal | X-Start Index | Unused"
        )
        ret_lines.append(
            f"\t.byte {bytes_to_asm(self.header_bytes[6])}"
            "\t\t\t\t ; Pipe Ends Level | VScroll Index | Vertical Flag | Next Area Object Set"
        )
        ret_lines.append(f"\t.byte {bytes_to_asm(self.header_bytes[7])}\t\t\t\t ; Level Entry Action | Graphic Set")
        ret_lines.append(f"\t.byte {bytes_to_asm(self.header_bytes[8])}\t\t\t\t ; Time Index | Unused | Music Index")
        ret_lines.append("")

        for obj in self.objects + self.jumps:
            if obj.is_4byte:
                indent = ""
            else:
                indent = "\t\t"

            ret_lines.append(f"\t.byte {bytes_to_asm(obj.to_bytes())}{indent} ; {obj.name} @ {obj.get_position()}")

        ret_lines.append("\t.byte $FF\t\t\t\t ; Terminator")

        return "\n".join(ret_lines)

    def from_m3l(self, m3l_bytes: bytearray):
        """Load a detached level from Foundry's M3L container.

        The method rebuilds object-set state first, then replays the M3L header,
        object stream, jump stream, and enemy stream through the same decode
        helpers used by ROM and byte-level loading so the editor ends in the
        same fully parsed state.

        Parameters
        ----------
        m3l_bytes : bytearray
            M3L payload containing world metadata, object set, header, objects,
            jumps, and enemy/item data.
        """
        self.world, level_number, object_set_number = m3l_bytes[:3]
        self.object_set = ObjectSet.from_number(object_set_number)
        self.object_set_number = object_set_number

        self.name = f"Level {self.world}-{level_number} - M3L"

        self.header_offset = self.enemy_offset = 0

        # block signals, so it will only be emitted, once we are fully set up
        self._signal_emitter.blockSignals(True)

        # update the level_object_factory
        self._load_level_data(bytearray(), bytearray(), new_level=False)

        m3l_bytes = m3l_bytes[3:]

        self.header_bytes = m3l_bytes[:HEADER_LENGTH]
        self._parse_header()

        m3l_bytes = m3l_bytes[HEADER_LENGTH:]

        # figure out how many bytes are the objects
        self._load_objects(m3l_bytes)
        object_size = self.current_object_size() + LEVEL_DATA_DELIMITER_COUNT  # delimiter

        object_bytes = m3l_bytes[:object_size]
        enemy_bytes = m3l_bytes[object_size:]

        self._signal_emitter.blockSignals(False)

        self._load_level_data(object_bytes, enemy_bytes)

        self.level_changed.emit()

    def from_asm(self, object_set_number: int, object_bytes: bytearray):
        """Load a header/object stream imported from assembly bytes.

        Assembly import provides only layout-side bytes, so this helper rebuilds
        the active object set and then delegates to ``from_bytes`` with an empty
        enemy stream. The follow-up ``level_changed`` emission tells the rest of
        the editor to rebuild around a new detached level payload even though
        the import skipped ROM-backed enemy data. In lifecycle terms, this is
        the assembly-import entry point: raw layout bytes become a detached
        in-memory level model first, and only after that model is rebuilt does
        the method notify views and tools that the level surface changed.

        Parameters
        ----------
        object_set_number : int
            Object set number that selects graphics and object definitions.
        object_bytes : bytearray
            Header and object bytes decoded from assembly.
        """
        self.object_set_number = object_set_number
        self.object_set = ObjectSet.from_number(object_set_number)

        self.from_bytes((0, object_bytes), (0, bytearray()), new_level=True)

        self.level_changed.emit()

    def save_to_rom(self) -> None:
        """Write the level and enemy streams to the active ROM.

        Managed-level metadata is updated before writing when the ROM has
        additional Foundry level-position data.
        """
        if ROM().additional_data.managed_level_positions:
            lo = LevelOrganizer(ROM(), ROM().additional_data.found_levels)
            lo.update_level_info(self)

        self._write_to_rom()

    def _write_to_rom(self):
        """Write serialized level bytes to their configured ROM offsets.

        The header/object stream and enemy/item stream are written separately
        because SMB3 stores them at independent addresses.
        """
        (level_address, level_data), (enemy_address, enemy_data) = self.to_bytes()
        ROM().write(level_address, level_data)
        ROM().write(enemy_address, enemy_data)

    def to_bytes(self) -> LevelByteData:
        """Serialize the level into the two SMB3 ROM streams it occupies.

        SMB3 stores header/object/jump bytes separately from enemy/item bytes.
        The enemy stream is re-sorted on export to match the game's
        orientation-specific ordering rules.

        Returns
        -------
        LevelByteData
            ``(address, bytes)`` pairs for header/object data and enemy/item data.
        """
        data = bytearray()

        data.extend(self.header_bytes)

        for obj in self.objects:
            data.extend(obj.to_bytes())

        for jump in self.jumps:
            data.extend(jump.to_bytes())

        data.append(0xFF)

        enemies = bytearray()
        enemies.append(self.first_enemy_byte)

        if self.is_vertical:
            enemies_objects = sorted(self.enemies, key=lambda _enemy: _enemy.y_position)
        else:
            enemies_objects = sorted(self.enemies, key=lambda _enemy: _enemy.x_position)

        for enemy in enemies_objects:
            enemies.extend(enemy.to_bytes())

        enemies.append(0xFF)

        return (self.header_offset, data), (self.enemy_offset, enemies)

    def from_bytes(self, object_data: ObjectData, enemy_data: EnemyItemData, new_level=True):
        """Load a level from explicit header/object and enemy stream pairs.

        This is the lowest-level restore path used by ROM loading, autosave
        recovery, M3L attachment, and undo-friendly reload flows. It updates
        ROM addresses, reparses the header, and decodes both streams through the
        normal factories.

        Parameters
        ----------
        object_data : ObjectData
            Header/object address and bytes.
        enemy_data : EnemyItemData
            Enemy/item address and bytes.
        new_level : bool, optional
            Whether to update saved-size bookkeeping and emit ``data_changed``.
        """
        self.header_offset, object_bytes = object_data
        self.enemy_offset, enemies = enemy_data

        self.header_bytes = object_bytes[0:HEADER_LENGTH]
        objects = object_bytes[HEADER_LENGTH:]

        self._parse_header(should_emit=False)
        self._load_level_data(objects, enemies, new_level)
