"""Shared level-model constants and abstract geometry for ``smb3parse.levels``.

This module collects the ROM-derived constants that the level and world-map
parsers share, along with :class:`LevelBase`, the abstract parent for concrete
layout models. ``smb3parse.levels.level`` uses these values to decode playable
stage layouts and headers, while ``smb3parse.levels.world_map`` uses the same
base contract to expose overworld dimensions and tile lookups.

The data flow starts with a ROM-backed :class:`~smb3parse.objects.object_set.ObjectSet`
and a layout address. Concrete subclasses keep those two pieces of state in
sync with their own decoded structures so callers can reason about the origin
of a layout, its object-set-dependent interpretation, and its rectangular
bounds through one shared interface.

See Also
--------
smb3parse.levels.level : Concrete parser for stage layouts and headers.
smb3parse.levels.world_map : Concrete parser for overworld layouts and level pointers.
smb3parse.levels.level_header : Header decoder that derives level geometry from ROM bytes.
"""

from abc import ABC

from smb3parse.constants import BASE_OFFSET
from smb3parse.objects.object_set import ObjectSet

ENEMY_BASE_OFFSET = BASE_OFFSET  # + 1
"""
One additional byte, at the beginning of every enemy data, where I don't know what does
"""

WORLD_MAP_BASE_OFFSET = BASE_OFFSET + 0xE000
"""
Offset for a lot of world related parsing.
"""

WORLD_COUNT = 9  # includes warp zone

WORLD_MAP_PALETTE_COUNT = 8

WORLD_MAP_HEIGHT = 9  # blocks
WORLD_MAP_SCREEN_WIDTH = 16  # blocks

LEVEL_SCREEN_HEIGHT = 15  # blocks
LEVEL_SCREEN_WIDTH = 16  # blocks

WORLD_MAP_BORDER_TOP_TILE_ID = 0x4E
WORLD_MAP_BLANK_TILE_ID = 0xFE

MAX_SCREEN_COUNT = 4

FIRST_VALID_ROW = 2

NO_MAP_SCROLLING = 0x10

"""
Tiles in rows before this one are part of the border and not valid overworld tiles.
"""

LAST_VALID_ROW = FIRST_VALID_ROW + WORLD_MAP_HEIGHT - 1
"""
Position of last visible row of the overworld.
"""

VALID_ROWS = range(FIRST_VALID_ROW, LAST_VALID_ROW + 1)
"""
A range of row values, where Mario could possibly stand.
"""

VALID_COLUMNS = range(WORLD_MAP_SCREEN_WIDTH)
"""
A range of column values, where Mario could possibly stand.
"""

COMPLETABLE_LIST_END_MARKER = 0x00  # MCT_END
"""
A value, that specifies the end of the completable tiles, rather than a set address.
"""

SPECIAL_ENTERABLE_TILE_AMOUNT = 11  # the rom mistakenly uses 0x1A

WORLD_MAP_SCREEN_SIZE = WORLD_MAP_HEIGHT * WORLD_MAP_SCREEN_WIDTH  # bytes

WORLD_MAP_WARP_WORLD_INDEX = 8
"""The 0-based index of the warp world."""

# in bytes
HEADER_LENGTH = 9

# in blocks
LEVEL_MIN_LENGTH = 0x10
LEVEL_MAX_LENGTH = 0x100
LEVEL_LENGTH_INTERVAL = 0x10

DEFAULT_HORIZONTAL_HEIGHT = 27
DEFAULT_VERTICAL_WIDTH = 16

WORLD_MAP_LAYOUT_DELIMITER = b"\xff"


def is_valid_level_length(level_length: int) -> bool:
    """Return whether a level length matches the ROM's fixed screen increments.

    Parameters
    ----------
    level_length : int
        Candidate level length in blocks.

    Returns
    -------
    bool
        ``True`` when the length falls within the supported range and aligns to
        the 16-block screen interval used by SMB3 level headers.
    """
    return level_length in range(LEVEL_MIN_LENGTH, LEVEL_MAX_LENGTH + 1, LEVEL_LENGTH_INTERVAL)


class LevelBase(ABC):
    """Abstract base for ROM-backed layouts with object-set-aware dimensions.

    Concrete subclasses represent either a playable level or an overworld map.
    They all carry the ROM address of the layout data and the
    :class:`~smb3parse.objects.object_set.ObjectSet` that determines how object
    bytes should be interpreted. Subclasses provide the actual geometry through
    :attr:`width` and :attr:`height`, letting shared helpers such as
    :meth:`point_in` answer bounds questions without caring whether the layout
    came from a stage parser or a world-map parser.

    Parameters
    ----------
    object_set : smb3parse.objects.object_set.ObjectSet
        Object-set metadata used to interpret objects that live in this layout.
    layout_address : int
        Absolute ROM address of the first byte of the layout payload.

    Attributes
    ----------
    layout_address : int
        Absolute ROM address of the layout bytes represented by the instance.
    object_set : smb3parse.objects.object_set.ObjectSet
        Object-set decoder shared by downstream object parsing.
    object_set_number : int
        Cached numeric identifier from ``object_set`` for comparisons and ROM
        pointer bookkeeping.

    Notes
    -----
    ``LevelBase`` intentionally does not decode headers, object streams, or
    world-map metadata itself. Those responsibilities stay in concrete models
    so this base class can remain the narrow contract that joins address
    provenance, object-set context, and rectangular bounds checks.
    """

    def __init__(self, object_set: ObjectSet, layout_address: int):
        """Store the shared ROM identity for a concrete layout model.

        Concrete level parsers call this once they know which ROM region owns
        the layout and which object set should decode its contents. Subclasses
        build richer state on top of these two fields, but downstream code
        compares and routes layouts through this shared identity.

        Parameters
        ----------
        object_set : smb3parse.objects.object_set.ObjectSet
            Object-set decoder that matches the layout's object encoding.
        layout_address : int
            Absolute ROM address of the layout bytes.
        """
        self.layout_address = layout_address

        self.object_set = object_set
        self.object_set_number = object_set.number

    @property
    def width(self) -> int:
        """Horizontal span of the layout in blocks.

        Concrete subclasses compute this value while decoding their ROM-backed
        source data, then expose it here as the horizontal dimension that the
        rest of the layout workflow trusts. :meth:`point_in`, block-grid
        iteration, and any caller that aligns coordinates to the decoded
        layout consume this one value instead of reaching back into header
        bytes, screen counts, or world-map metadata, so the geometry handoff
        stays uniform across every concrete parser.

        Raises
        ------
        NotImplementedError
            Raised by the abstract base when a subclass has not supplied its
            concrete geometry.
        """
        raise NotImplementedError()

    @property
    def height(self) -> int:
        """Vertical span of the layout in blocks.

        Concrete subclasses publish the decoded vertical extent through this
        property after they resolve their own ROM-derived geometry rules.
        Callers pair the result with :attr:`width` to validate coordinates,
        iterate visible block rows, and keep geometry-sensitive code working
        against one shared layout interface instead of parser-specific fields.

        Raises
        ------
        NotImplementedError
            Raised by the abstract base when a subclass has not supplied its
            concrete geometry.
        """
        raise NotImplementedError()

    def point_in(self, x: int, y: int) -> bool:
        """Check whether a block coordinate lies inside the layout bounds.

        This helper centralizes the half-open rectangle test used by concrete
        level models when they validate map positions against decoded
        dimensions.

        Parameters
        ----------
        x : int
            Horizontal block coordinate to test.
        y : int
            Vertical block coordinate to test.

        Returns
        -------
        bool
            ``True`` when ``x`` and ``y`` fall within the half-open rectangle
            defined by ``[0, width)`` and ``[0, height)``.
        """
        return 0 <= x < self.width and 0 <= y < self.height
