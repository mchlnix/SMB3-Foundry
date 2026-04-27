"""Resolve SMB3 object-set metadata and level-data bank offsets.

This module validates object-set numbers and exposes :class:`ObjectSet`, a
small ROM-backed helper that turns an SMB3 object-set id into three pieces of
state used throughout level parsing: a human-readable name, the PRG-backed base
offset for that set's level data, and the ending-graphic group chosen by that
set. Callers typically construct :class:`ObjectSet` before decoding a level so
later object, header, and graphics loaders can agree on which banked data to
read.

The workflow is intentionally narrow. Validation helpers gate user or parser
input, :class:`ObjectSet` reads the object-set bank table from the ROM when the
set refers to level data, and higher-level level parsers reuse the computed
``level_offset`` when translating SMB3 addresses into file offsets. For the
actual object decoders that consume the resulting object-set number and offset,
read next in :mod:`smb3parse.objects.level_object` and
:mod:`smb3parse.levels.level`.

See Also
--------
smb3parse.levels.level.Level
    Higher-level level parser that consumes object-set metadata while building
    a decoded level model.
smb3parse.objects.level_object.LevelObject
    Decoded object record whose interpretation depends on the selected object
    set.
"""

from smb3parse.constants import (
    AIR_SHIP_OBJECT_SET,
    BASE_OFFSET,
    CLOUDY_OBJECT_SET,
    DESERT_OBJECT_SET,
    DUNGEON_OBJECT_SET,
    ENEMY_ITEM_OBJECT_SET,
    GIANT_OBJECT_SET,
    HILLY_OBJECT_SET,
    ICE_OBJECT_SET,
    MAX_OBJECT_SET,
    MIN_OBJECT_SET,
    MUSHROOM_OBJECT_SET,
    OBJECT_SET_NAMES,
    PAGE_A000_OFFSET,
    PIPE_OBJECT_SET,
    PIRANHA_PLANT_OBJECT_SET,
    PLAINS_OBJECT_SET,
    SKY_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    UNDERGROUND_OBJECT_SET,
    WATER_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
    Constants,
)
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

# number of consecutive objects in a group that share the same byte length
OBJECT_GROUP_SIZE = 16


def assert_valid_object_set_number(object_set_number: int):
    """Raise when an object-set id falls outside the SMB3 table bounds.

    Parameters
    ----------
    object_set_number : int
        Object-set number that a caller wants to use for level parsing or
        object decoding.

    Raises
    ------
    ValueError
        Raised when ``object_set_number`` is not one of the stock SMB3 object
        sets represented in the ROM tables.
    """
    if not is_valid_object_set_number(object_set_number):
        raise ValueError(f"Object set number {object_set_number} is invalid.")


def is_valid_object_set_number(object_set_number: int):
    """Whether an integer can index the stock SMB3 object-set tables.

    Parameters
    ----------
    object_set_number : int
        Candidate object-set number to check.

    Returns
    -------
    bool
        ``True`` when the number falls inside the inclusive SMB3 object-set
        range, otherwise ``False``.
    """
    return object_set_number in range(MIN_OBJECT_SET, MAX_OBJECT_SET + 1)


class ObjectSet:
    """Represent one SMB3 object set as ROM-backed parsing metadata.

    Instances of this helper bridge the gap between the numeric object-set id
    stored in a level header and the richer metadata that parsers need later in
    the pipeline. Construction resolves which level-data bank backs that id,
    computes the file offset that makes SMB3's bank-local addresses usable to
    callers, and records the ending-graphic group tied to that family.
    Downstream loaders can then carry one decoded object-set record while they
    parse headers, objects, and end-of-level decoration rules.

    Parameters
    ----------
    rom : smb3parse.util.rom.Rom
        ROM image that stores the bank table used to locate level data for the
        object set.
    object_set_number : int
        SMB3 object-set id selected by the level header or by higher-level
        tooling.

    Attributes
    ----------
    rom : smb3parse.util.rom.Rom
        ROM image consulted when translating the object-set id into a file
        offset.
    number : int
        Raw SMB3 object-set id.
    level_offset : int
        File offset that higher-level level parsers add to level-local
        addresses for this object set.
    name : str
        Human-readable name for the object set.

    Notes
    -----
    Enemy/item data is the one special case in this file. That object-set id
    does not use the level-data bank table, so it keeps the base offset and
    does not expose an ending-graphic index.
    """

    def __init__(self, rom: Rom, object_set_number: int):
        """Resolve the parsing metadata that downstream level loaders reuse.

        Construction is the handoff from a raw header value to the richer
        state that later parsing stages need. The initializer keeps the raw
        object-set number, translates it through SMB3's bank table when the set
        points at level data, and leaves the instance holding one stable
        ``level_offset`` value that callers can reuse for header, object, and
        graphics lookups without repeating the bank arithmetic.

        Parameters
        ----------
        rom : smb3parse.util.rom.Rom
            ROM image that stores the object-set bank table.
        object_set_number : int
            SMB3 object-set id whose level-data bank and display name should be
            resolved.

        Notes
        -----
        For level object sets, construction reads one byte from the ROM's
        ``OFFSET_BY_OBJECT_SET_A000`` table, expands that bank number into a
        file offset, then subtracts the implicit CPU ``0xA000`` mapping so
        later level-local addresses can be translated directly into ROM
        positions.
        """
        self.rom = rom
        self.number = object_set_number

        self.level_offset = BASE_OFFSET

        if self.number != ENEMY_ITEM_OBJECT_SET:
            object_set_offset = self.rom.int(Constants.OFFSET_BY_OBJECT_SET_A000 + self.number) * PRG_BANK_SIZE

            self.level_offset += object_set_offset - PAGE_A000_OFFSET

            self._ending_graphic_index = _object_set_to_ending_graphic_index[object_set_number]

        if self.number < len(OBJECT_SET_NAMES):
            self.name = OBJECT_SET_NAMES[self.number]
        else:
            self.name = f"Object Set {self.number:#x}"

    @property
    def ending_graphic_index(self):
        """Ending-decoration group used by level object sets.

        Level parsing and rendering code use this property when they need the
        SMB3 ending graphic family associated with an object set. Enemy and
        item data does not participate in that workflow, so those callers must
        not request this property.

        Returns
        -------
        int
            Ending-graphic group index associated with the object set.

        Raises
        ------
        ValueError
            Raised when the object set refers to enemy/item data instead of a
            level-data family.
        """
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"{self.name} is not a level object set and does not provide an ending graphic offset.")

        return self._ending_graphic_index

    def __repr__(self):
        """Debugger-facing identity string for one decoded SMB3 object set.

        The representation keeps both the numeric object-set id and the
        resolved display name together so parser logs and interactive sessions
        can tell which SMB3 family supplied a later offset or rendering choice
        without re-opening the ROM tables.

        Returns
        -------
        str
            Representation that preserves both the raw object-set number and
            the resolved display name.
        """
        return f"ObjectSet({self.number}), {self.name}"


# TODO this could be read out of the ROM see LoadLevel_EndGoalDecoSquare
_object_set_to_ending_graphic_index = {
    WORLD_MAP_OBJECT_SET: 0,
    PLAINS_OBJECT_SET: 0,
    DUNGEON_OBJECT_SET: 0,
    HILLY_OBJECT_SET: 0,
    MUSHROOM_OBJECT_SET: 0,
    AIR_SHIP_OBJECT_SET: 0,
    CLOUDY_OBJECT_SET: 0,
    UNDERGROUND_OBJECT_SET: 0,
    SPADE_BONUS_OBJECT_SET: 0,
    ENEMY_ITEM_OBJECT_SET: 0,
    SKY_OBJECT_SET: 1,
    ICE_OBJECT_SET: 1,
    PIRANHA_PLANT_OBJECT_SET: 2,
    DESERT_OBJECT_SET: 2,
    GIANT_OBJECT_SET: 2,
    WATER_OBJECT_SET: 3,
    PIPE_OBJECT_SET: 3,
}
