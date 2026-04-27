"""Parse level-object records from SMB3 object streams.

This module turns the raw 3-byte and 4-byte records used by SMB3 level data
into :class:`LevelObject` instances and exposes helpers that answer whether an
object identifier is one of the jump or exit shapes that transfers Mario to the
next level. The parser consumes these helpers while it walks the object stream:
first this module decodes the packed bytes into coordinates and ids, then the
level model uses those fields to classify geometry and transitions. New
maintainers usually read this file together with ``smb3parse.objects`` for the
shared in-level-object base type and ``smb3parse.levels.level`` for the
higher-level container that consumes parsed objects.

See Also
--------
smb3parse.objects.InLevelObject
    Base class that stores the raw bytes shared by parsed level objects.
smb3parse.levels.level.Level
    Level model that aggregates :class:`LevelObject` instances during parsing.
"""

from smb3parse.constants import (
    ENEMY_ITEM_OBJECT_SET,
    PLAINS_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)
from smb3parse.levels import DEFAULT_HORIZONTAL_HEIGHT
from smb3parse.objects import InLevelObject
from smb3parse.util import lrange

Domain = int
ObjectId = int
ObjectSetNo = int


def _obj_range(object_set: ObjectSetNo, start: ObjectId) -> list[ObjectId]:
    """Expand an encoded object identifier to the ids it can represent.

    Some SMB3 object sets treat ids above ``0x0F`` as the first value in a
    16-entry block instead of a single concrete id. World-map and enemy-item
    object sets do not use that expansion, so they keep the original id.

    Parameters
    ----------
    object_set : ObjectSetNo
        Object-set number that determines whether the id is expanded.
    start : ObjectId
        Raw object identifier or the first id in an encoded range.

    Returns
    -------
    list[ObjectId]
        Concrete ids that should be considered equivalent for exit-detection
        checks.

    >>> _obj_range(PLAINS_OBJECT_SET, 0x0A)
    [0x0A]

    >>> _obj_range(WORLD_MAP_OBJECT_SET, 0xA0)
    [0xA0]

    >>> _obj_range(PLAINS_OBJECT_SET, 0xA0)
    [0xA0, 0xA1, ..., 0xAE, 0xAF]

    """
    if object_set in [WORLD_MAP_OBJECT_SET, ENEMY_ITEM_OBJECT_SET]:
        return [start]

    if start < 0x10:
        return [start]

    return lrange(start, start + 0x10)


def goes_to_next_level(object_set_num: ObjectSetNo, domain: Domain, obj_id: ObjectId):
    """Return whether a parsed level object behaves like a level transition.

    The parser uses this table-driven check to recognize doors, pipes, and
    other SMB3 level objects that jump to another area or level. Domain ``0``
    carries object-set-specific exits, while domains ``1`` and ``2`` contribute
    the shared jump object ids that appear across most level definitions.

    Parameters
    ----------
    object_set_num : ObjectSetNo
        Object-set number from the level header.
    domain : Domain
        Encoded domain from the first byte of the level-object record.
    obj_id : ObjectId
        Raw object identifier from the record's second byte.

    Returns
    -------
    bool
        ``True`` when the record should be treated as an object that advances to
        another level or area.
    """
    # there are special level objects, like doors, that will take the player to the jump destination
    object_id_ranges_by_domain_and_definition: dict[ObjectSetNo, dict[Domain, list[ObjectId]]] = {
        PLAINS_OBJECT_SET: {
            0: [0x04],
        },
        2: {
            0: [0x00, 0x06],
        },
        3: {
            0: [0x0F],
        },
        4: {
            0: [0x05],
        },
        5: {},
        6: {
            0: [0x0A],
        },
        7: {
            0: [0x04],
        },
        8: {
            0: [0x0A],
        },
        9: {
            0: [0x0B],
        },
        10: {},
        11: {},
        12: {
            0: [0x05],
        },
        13: {},
        14: {
            0: [0x0F],
        },
        15: {
            0: [0x04],
        },
        16: {
            0: [0x08, 0xD5],
        },
    }

    for definition in range(1, ENEMY_ITEM_OBJECT_SET):
        # these objects are in all level object definitions
        object_id_ranges_by_domain_and_definition[definition][1] = [0x90, 0xC0, 0xE0]
        object_id_ranges_by_domain_and_definition[definition][2] = [0x07, 0x10]

    object_id_ranges_by_domain = object_id_ranges_by_domain_and_definition[object_set_num]

    if domain not in object_id_ranges_by_domain:
        return False

    return any(obj_id in _obj_range(object_set_num, jump_obj_id) for jump_obj_id in object_id_ranges_by_domain[domain])


class LevelObject(InLevelObject):
    """Represent one parsed SMB3 level-object record.

    ``LevelObject`` decodes the packed bytes used in normal SMB3 level streams
    into the placement fields that later editor and parser layers consume. The
    first byte combines domain and ``y`` position, the second byte stores the
    object id, and the third byte stores the ``x`` position. A fourth byte is
    present only for object shapes that carry an additional encoded length.

    Parameters
    ----------
    data : bytearray
        Raw 3-byte or 4-byte level-object record from a level data stream.

    Attributes
    ----------
    data : bytearray
        Original raw bytes retained by :class:`~smb3parse.objects.InLevelObject`.
    domain : Domain
        Domain extracted from the high three bits of the first byte.
    y : int
        Vertical coordinate extracted from the low five bits of the first byte.
    id : ObjectId
        Object identifier stored in the second byte.
    x : int
        Horizontal coordinate stored in the third byte.
    additional_length : int
        Optional fourth byte present on objects that encode a trailing length
        or span value.

    Raises
    ------
    ValueError
        If the record is not 3 or 4 bytes long, or if the decoded ``y`` value
        exceeds the horizontal-height limit expected by the level parser.

    Notes
    -----
    The constructor validates the same record-shape assumptions that the rest
    of ``smb3parse`` relies on: level objects are either three or four bytes
    long, and their decoded ``y`` coordinate must remain inside the horizontal
    level height limit shared by the parser's level model.
    """

    def __init__(self, data: bytearray):
        """Decode a raw level-object record into placement fields.

        This constructor is the byte-stream boundary for normal SMB3 level
        objects. It unpacks the record into the domain and coordinates that the
        level parser, object classification helpers, and later editor-facing
        code use instead of re-reading the packed bytes.

        Parameters
        ----------
        data : bytearray
            Raw SMB3 level-object bytes. Three-byte records contain the packed
            domain/``y`` byte plus ``id`` and ``x``. Four-byte records append an
            extra length byte for shapes that span multiple tiles.

        Raises
        ------
        ValueError
            If ``data`` is not a 3-byte or 4-byte record.
        ValueError
            If the decoded ``y`` value exceeds
            :data:`smb3parse.levels.DEFAULT_HORIZONTAL_HEIGHT`.
        """
        super(LevelObject, self).__init__(data)

        if len(data) not in [3, 4]:
            raise ValueError(f"Length of the given data must be 3 or 4, was {len(data)}.")

        self.domain = data[0] >> 5
        self.y = data[0] & 0b0001_1111

        if self.y > DEFAULT_HORIZONTAL_HEIGHT:
            raise ValueError(
                f"Data designating y value cannot be higher than {DEFAULT_HORIZONTAL_HEIGHT}, was {self.y}."
            )

        self.id = data[1]
        self.x = data[2]

        if len(data) == 4:
            self.additional_length = data[3]
