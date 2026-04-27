"""Represent a ROM-backed SMB3 level selected from memory or a world map.

This module provides :class:`Level`, a small integration object that combines
the object-set-aware :class:`~smb3parse.levels.LevelBase` state with the
decoded :class:`~smb3parse.levels.level_header.LevelHeader` stored immediately
before a level layout in ROM. Callers either construct a level directly from
known ROM addresses or resolve one through a
:class:`~smb3parse.levels.world_map.WorldMapPosition` that already points at a
world-map level pointer.

The class does not decode the full object or enemy streams by itself. Instead,
it preserves the addresses, object set number, optional world-map origin, and
parsed header data that downstream level readers need.

See Also
--------
smb3parse.levels.level_header.LevelHeader
    Decodes the nine-byte header stored before the layout data.
smb3parse.levels.world_map.WorldMap
    Resolves enterable overworld tiles into level pointers.
"""

from smb3parse.levels import HEADER_LENGTH, LevelBase
from smb3parse.levels.level_header import LevelHeader
from smb3parse.levels.world_map import WorldMapPosition
from smb3parse.objects.object_set import ObjectSet, assert_valid_object_set_number
from smb3parse.util.rom import Rom


class Level(LevelBase):
    """Bind ROM addresses, object-set context, and a decoded SMB3 level header.

    A ``Level`` instance is the handoff object between overworld resolution and
    deeper level parsing. It keeps the ROM coordinates that identify the layout
    and enemy streams together with the object set and decoded header so later
    consumers can continue decoding without repeating pointer lookups.

    Parameters
    ----------
    rom : Rom
        ROM reader used to fetch the level header bytes.
    object_set_number : int
        Object set that defines how the layout and related objects should be
        interpreted.
    layout_address : int
        Absolute ROM address of the level layout stream. The header is expected
        to start :data:`~smb3parse.levels.HEADER_LENGTH` bytes before this
        address.
    enemy_address : int
        Absolute ROM address of the enemy data stream associated with the
        layout.

    Attributes
    ----------
    enemy_address : int
        Absolute ROM address of the level's enemy data.
    world_map_position : WorldMapPosition or None
        Overworld position that produced this level when constructed through
        :meth:`from_world_map`. Direct memory construction leaves this unset.
    header_address : int
        Absolute ROM address of the level header immediately before the layout.
    header_bytes : bytearray
        Raw header bytes read from ROM.
    header : LevelHeader
        Parsed level header derived from ``header_bytes``.

    Notes
    -----
    ``Level`` inherits ``layout_address``, ``object_set``, and
    ``object_set_number`` from :class:`~smb3parse.levels.LevelBase`. That base
    object is initialized first so the level keeps the same object-set
    bookkeeping as other parsed level-like structures.
    """

    def __init__(self, rom: Rom, object_set_number: int, layout_address: int, enemy_address: int):
        """Initialize a level view from decoded ROM addresses.

        This constructor is the bridge between pointer resolution and later
        level decoding. Callers arrive here after some other subsystem has
        already decided which object set, layout address, and enemy address
        belong together. The constructor first installs the shared
        :class:`LevelBase` state for the object set and layout address, then
        stores the enemy stream address, computes the header address that sits
        immediately before the layout stream, reads those bytes from ROM, and
        parses them into a :class:`LevelHeader`. After that sequence completes,
        downstream decoders can treat the instance as the canonical handoff
        object for this level and continue with layout or enemy parsing
        without re-deriving any ROM coordinates.

        Parameters
        ----------
        rom : Rom
            ROM reader used to retrieve header bytes.
        object_set_number : int
            Object set number for the level layout.
        layout_address : int
            Absolute address of the layout data in ROM.
        enemy_address : int
            Absolute address of the matching enemy data in ROM.

        Notes
        -----
        ``world_map_position`` starts as ``None`` because direct construction
        does not imply an overworld origin. :meth:`from_world_map` attaches
        that provenance after it resolves a level pointer from a world-map
        tile, while direct memory loaders usually stop at the header-parsed
        state produced here.
        """
        super(Level, self).__init__(ObjectSet(rom, object_set_number), layout_address)

        self.enemy_address = enemy_address

        self.world_map_position: WorldMapPosition | None = None

        self._rom = rom

        self.header_address = self.layout_address - HEADER_LENGTH

        self.header_bytes = self._rom.read(self.header_address, HEADER_LENGTH)

        self.header = LevelHeader(rom, self.header_bytes)

    def set_world_map_position(self, position: WorldMapPosition):
        """Record which overworld tile resolved to this level.

        Parameters
        ----------
        position : WorldMapPosition
            Overworld position whose level pointer was used to construct this
            level.
        """
        self.world_map_position = position

    def __eq__(self, other):
        """Compare levels by the ROM locations that define their contents.

        Equality intentionally ignores transient metadata such as the cached
        world-map origin and instead treats a level as the tuple of ROM inputs
        needed to decode it again.

        Parameters
        ----------
        other : object
            Candidate object to compare against this level.

        Returns
        -------
        bool
            ``True`` when ``other`` is a :class:`Level` with the same object
            set number, layout address, and enemy address.
        """
        if not isinstance(other, Level):
            return False

        return (
            self.object_set_number == other.object_set_number
            and self.layout_address == other.layout_address
            and self.enemy_address == other.enemy_address
        )

    @staticmethod
    def from_world_map(rom: Rom, world_map_position: WorldMapPosition) -> "Level | None":
        """Create a level from a resolved overworld position.

        This is the normal entry point when an overworld tile has already been
        decoded into a level pointer and the caller wants the corresponding
        level header plus provenance in one object.

        Parameters
        ----------
        rom : Rom
            ROM reader used to materialize the level header.
        world_map_position : WorldMapPosition
            World-map position whose ``level_pointer`` already captures the
            decoded object set, layout address, and enemy address.

        Returns
        -------
        Level or None
            A new level with ``world_map_position`` recorded when the tile has
            a level pointer, otherwise ``None``.

        Notes
        -----
        This constructor preserves the world-map origin so later code can keep
        the level associated with the tile that exposed it.
        """
        lp = world_map_position.level_pointer

        if lp is None:
            return None

        level = Level(rom, lp.object_set, lp.level_address, lp.enemy_address)

        level.set_world_map_position(world_map_position)

        return level

    @staticmethod
    def from_memory(rom: Rom, object_set_number: int, layout_address: int, enemy_address: int) -> "Level":
        """Create a level directly from already-known ROM addresses.

        Use this path when another subsystem already owns pointer resolution
        and only needs the shared level wrapper plus header decoding. The
        method first validates that the supplied object set can legally select
        SMB3 object definitions. It then forwards the stabilized address tuple
        into :class:`Level`, which installs the base object-set state, reads
        the header bytes that precede the layout stream, and caches the parsed
        header on the returned instance. The result is the same level handoff
        object used elsewhere in the parser, just without any overworld
        provenance attached.

        Parameters
        ----------
        rom : Rom
            ROM reader used to retrieve the header bytes.
        object_set_number : int
            Object set number for the layout stream.
        layout_address : int
            Absolute ROM address of the layout data.
        enemy_address : int
            Absolute ROM address of the enemy data.

        Returns
        -------
        Level
            A level initialized from the supplied addresses.

        Raises
        ------
        ValueError
            If ``object_set_number`` is outside the valid SMB3 object-set
            range enforced by :func:`assert_valid_object_set_number`.

        Notes
        -----
        Unlike :meth:`from_world_map`, this constructor path records no
        overworld origin. It is meant for tools that already have absolute ROM
        addresses and only need the shared level/header wrapper before
        continuing into layout or enemy decoding.
        """
        assert_valid_object_set_number(object_set_number)

        level = Level(rom, object_set_number, layout_address, enemy_address)

        return level
