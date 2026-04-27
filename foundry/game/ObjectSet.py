"""Foundry-facing wrapper around SMB3 object-set metadata.

The base ``smb3parse`` object set knows how SMB3 groups objects, graphics, and
ending-object tables in ROM. This module adds the editor metadata loaded from
``objects.dat`` so object decoding, previews, and renderers can ask one object
set for both ROM-derived layout information and Foundry's richer definition
records. It is the shared lookup object that lets one editor workflow move from
``level header chose object set N`` to ``use these definitions, ending tables,
and graphics rules for every object decoded in that level``.

See Also
--------
foundry.game.ObjectDefinitions
    Supplies the parsed definition rows attached to each object set here.
foundry.game.gfx.objects.in_level.level_object
    Uses object sets to decode object bytes against the right definition bank.
"""

from functools import lru_cache

from foundry.game.File import ROM
from foundry.game.ObjectDefinitions import ObjectDefinition, load_object_definitions
from smb3parse.constants import ENEMY_ITEM_OBJECT_SET
from smb3parse.objects.object_set import ObjectSet as SMB3ObjectSet

# TODO: make relative to a label in Constants
ENDING_OBJECT_BASE_OFFSET = 0x1C8F9
"""
There are different Level Ending Objects. The design and necessary blocks to use are written into the ROM at this
address. To figure out which belongs to which Object Set we need to get the index for said Object Set and then multiply
by ENDING_OBJECT_BLOCK_COUNT.
"""

ENDING_OBJECT_BLOCK_COUNT = 96
"""Size in blocks of Level Ending Object data per object saved in the ROM."""


class ObjectSet(SMB3ObjectSet):
    """Represent an SMB3 object set with Foundry definitions.

    The base ``smb3parse`` object set supplies ROM-derived object-set metadata.
    Foundry extends it with editor object definitions and a special display name
    for the enemy/item set. The resulting object is the handoff point between
    ROM-derived set metadata from ``smb3parse`` and Foundry's higher-level
    object definition data from ``objects.dat``.

    Parameters
    ----------
    object_set_number : int
        Object set number that selects graphics and object definitions.

    Attributes
    ----------
    definitions : list[ObjectDefinition]
        Editor definitions indexed by object id.
    name : str
        Display name for the object set.

    Notes
    -----
    Factories and renderers reuse ``ObjectSet`` instances heavily. The cached
    constructor keeps object-definition lookups stable and cheap while still
    reflecting the ROM-selected object-set number.

    Examples
    --------
    Load the shared wrapper for the object set chosen by a level header and
    use it to resolve both definition metadata and the ending-object ROM
    table used by previews::

        object_set = ObjectSet.from_number(3)
        definition = object_set.get_definition_of(0x12)
        ending_offset = object_set.get_ending_offset()

        assert definition is object_set.definitions[0x12]
        assert ending_offset >= ENDING_OBJECT_BASE_OFFSET
    """

    def __init__(self, object_set_number: int):
        """Load object-set metadata and editor definitions.


        Parameters
        ----------
        object_set_number : int
            Object set number that selects graphics and object definitions.
        """
        super(ObjectSet, self).__init__(ROM(), object_set_number)

        if self.number == ENEMY_ITEM_OBJECT_SET:
            self.name = "Enemy Object Set"

        self.definitions = load_object_definitions(self.number)

    def get_definition_of(self, object_id: int) -> ObjectDefinition:
        """Look up the editor definition bound to an object id.

        This is the handoff from ROM-selected object-set context to the
        normalized metadata record used by object factories and renderers.

        Parameters
        ----------
        object_id : int
            Identifier of the object.

        Returns
        -------
        ObjectDefinition
            Definition metadata used to render and edit the object.
        """
        return self.definitions[object_id]

    def get_ending_offset(self) -> int:
        """Compute the ROM offset for this set's ending-object block table.

        This keeps end-cap table indexing in one place for object definition
        parsing and avoids applying level-ending object logic to the enemy set.
        Callers use this offset when resolving the hard-coded ending graphics
        that live outside ``objects.dat``. The calculation bridges from the
        current object's set-level metadata to the shared ROM table that stores
        the matching ending graphics, so renderer setup can move from an object
        set number to the correct ending-graphics bank without duplicating ROM
        layout math. In practice this is the workflow boundary that moves
        ending-object decoding out of definition metadata and into the ROM state
        still needed by preview and render paths.

        Returns
        -------
        int
            ROM offset for this object set's ending-object block data.

        Raises
        ------
        ValueError
            If called for the enemy/item object set.
        """
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"This method shouldn't be called for the {self.name}")

        return ENDING_OBJECT_BASE_OFFSET + self.ending_graphic_index * ENDING_OBJECT_BLOCK_COUNT

    @staticmethod
    @lru_cache(16)
    def from_number(object_set_num: int) -> "ObjectSet":
        """Load or reuse the shared object-set wrapper for a set number.

        Object definitions and base metadata are reused heavily by object
        factories and renderers, so instances are cached by object-set number.
        That keeps decode and preview paths working with a stable shared object
        set instead of reparsing the same definitions repeatedly.

        Parameters
        ----------
        object_set_num : int
            Object set number to load.

        Returns
        -------
        'ObjectSet'
            Cached object set wrapper.

        Examples
        --------
        Reuse the cached wrapper selected by a level header before looking up
        object metadata::

            object_set = ObjectSet.from_number(3)
            object_definition = object_set.get_definition_of(0x12)

            assert object_set is ObjectSet.from_number(3)
            assert object_definition is object_set.definitions[0x12]
        """
        return ObjectSet(object_set_num)
