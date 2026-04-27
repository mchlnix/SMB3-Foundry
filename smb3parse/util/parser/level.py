"""Aggregate parsed SMB3 objects and enemies into one level parse result.

This module defines :class:`ParsedLevel`, the lightweight container returned by
the parser after it decodes one SMB3 level header, object stream, and enemy
stream into editor-facing records. The object parser populates the raw
placement lists first, then downstream tools use this aggregate to size the
serialized byte streams and to answer whether the level contains transition
objects that jump to other areas. New maintainers usually read this file after
``smb3parse.util.parser.object`` for the record types and alongside
``smb3parse.levels.level`` for the higher-level level model that consumes the
parsed data.

See Also
--------
smb3parse.util.parser.object.ParsedObject
    Parsed normal level-object records stored in :class:`ParsedLevel`.
smb3parse.util.parser.object.ParsedEnemy
    Parsed enemy records stored alongside normal level objects.
smb3parse.levels.level.Level
    Level model that consumes parsed records and header metadata together.
"""

from dataclasses import dataclass, field

from smb3parse.constants import (
    CLOUDY_OBJECT_SET,
    ENEMY_ITEM_OBJECT_SET,
    ENEMY_SIZE,
    GIANT_OBJECT_SET,
    HILLY_OBJECT_SET,
    PIRANHA_PLANT_OBJECT_SET,
    PLAINS_OBJECT_SET,
    UNDERGROUND_OBJECT_SET,
)
from smb3parse.levels import HEADER_LENGTH
from smb3parse.objects.level_object import goes_to_next_level
from smb3parse.util.parser.object import ParsedEnemy, ParsedObject


@dataclass
class ParsedLevel:
    """Store one fully decoded SMB3 level parse.

    ``ParsedLevel`` is the parser-side handoff between byte decoding and
    higher-level level modeling. It groups the header-derived object-set and
    palette numbers with the parsed object and enemy records so editor and
    serialization code can answer size questions and detect transition objects
    without rescanning the original byte streams.

    Parameters
    ----------
    object_set_num : int
        Object-set number taken from the level header and reused when
        classifying level exits.
    graphics_set_num : int
        Graphics-set number chosen by the level header.
    object_palette_num : int
        Palette index applied to normal level objects.
    enemy_palette_num : int
        Palette index applied to enemy records.
    screen_memory : list[int]
        Parsed screen-memory data carried with the level parse.
    parsed_objects : list[ParsedObject]
        Decoded normal level-object records in stream order.
    parsed_enemies : list[ParsedEnemy], optional
        Decoded enemy records in stream order.

    Attributes
    ----------
    object_set_num : int
        Object-set number that controls how object ids are interpreted.
    graphics_set_num : int
        Graphics-set number preserved from the header parse.
    object_palette_num : int
        Palette index for normal objects.
    enemy_palette_num : int
        Palette index for enemies.
    screen_memory : list[int]
        Parsed screen-memory bytes kept with the aggregate level result.
    parsed_objects : list[ParsedObject]
        Decoded level-object records that still retain their original bytes.
    parsed_enemies : list[ParsedEnemy]
        Decoded enemy records that still retain their original bytes.

    Notes
    -----
    This dataclass intentionally stays close to the parser's decoded data
    shapes. It does not reinterpret the level as editor geometry on its own;
    instead, it preserves the decoded records so downstream consumers can make
    object-set-sensitive decisions such as jump and exit detection.
    """

    object_set_num: int
    graphics_set_num: int
    object_palette_num: int
    enemy_palette_num: int
    screen_memory: list[int]
    parsed_objects: list[ParsedObject]
    parsed_enemies: list[ParsedEnemy] = field(default_factory=list)

    @property
    def object_data_length(self):
        """Serialized byte length of the header and normal object stream.

        The parser keeps normal level objects as decoded records, but save and
        replay paths still need to know how many bytes those records occupy when
        written back out. This property reconstructs that boundary by adding the
        fixed level-header length to the raw byte lengths retained by each
        parsed object.

        Returns
        -------
        int
            Total byte length of the level header plus all serialized normal
            level objects.
        """
        return HEADER_LENGTH + sum(len(obj.obj_bytes) for obj in self.parsed_objects)

    @property
    def enemy_data_length(self):
        """Serialized byte length of the parsed enemy stream.

        Enemy records remain fixed-width after parsing, so downstream save paths
        can recover the serialized enemy-stream length from the decoded record
        count without revisiting the original ROM bytes.

        Returns
        -------
        int
            Total byte length of the serialized enemy stream.
        """
        return len(self.parsed_enemies) * ENEMY_SIZE

    def has_jump(self):
        """Presence check for any transition object in the parsed level.

        This check is the parser-side shortcut for later tools that need to
        know whether a level can transfer Mario to another area. It evaluates
        both normal level objects and enemy-item records against the shared
        jump-classification helper so downstream code does not have to rescan
        both record lists separately. Consumers such as level summarizers,
        pointer editors, and save paths use this boolean to decide whether the
        header jump destination is part of the level's effective routing state
        before they inspect individual parsed records.

        Returns
        -------
        bool
            ``True`` when either the normal object stream or the enemy stream
            contains a transition record that later exit-routing code must
            treat as a jump to another level or area.
        """
        return any(
            goes_to_next_level(self.object_set_num, parsed_object.domain, parsed_object.obj_id)
            for parsed_object in self.parsed_objects
        ) or any(
            goes_to_next_level(ENEMY_ITEM_OBJECT_SET, parsed_enemy.domain, parsed_enemy.obj_id)
            for parsed_enemy in self.parsed_enemies
        )

    def has_generic_exit(self):
        """Presence check for objects that route through the world's generic exit.

        Some SMB3 object sets include doors or pipes that ignore the jump
        destination encoded in the level header and instead route Mario through
        the world's shared generic-exit slot. This helper lets parser consumers
        detect that alternate routing path from the decoded object list before
        they interpret the header destination as authoritative for exit
        previews, serialization, or editor summaries. That boundary matters
        because downstream world-map and pointer-editing code must preserve the
        shared world exit slot instead of treating the level header's jump
        address as the only source of truth.

        Returns
        -------
        bool
            ``True`` when the parsed object stream contains an object that uses
            the world-level generic-exit destination instead of the
            header-defined jump target.
        """
        if self.object_set_num in [HILLY_OBJECT_SET, UNDERGROUND_OBJECT_SET]:
            domain = 4
            id_range = range(0xE0, 0xF0)
        elif self.object_set_num == CLOUDY_OBJECT_SET:
            domain = 3
            id_range = range(0x60, 0x70)
        elif self.object_set_num in [PIRANHA_PLANT_OBJECT_SET, GIANT_OBJECT_SET]:
            domain = 3
            id_range = range(0x50, 0x70)
        else:
            return False

        return any(
            parsed_object.domain == domain and parsed_object.obj_id in id_range for parsed_object in self.parsed_objects
        )

    def has_big_q_level(self):
        """Presence check for objects that route through the Big Q bonus slot.

        Plains-style object sets can encode transitions that route Mario to the
        world's shared Big Question Block bonus level instead of the
        header-defined jump destination. Parser consumers use this helper to
        distinguish those shared-destination objects from ordinary jump targets
        before they serialize or present the level's exits.

        Returns
        -------
        bool
            ``True`` when the parsed object stream contains an object that
            routes through the world's shared Big Question Block level slot.
        """
        if self.object_set_num in range(PLAINS_OBJECT_SET, ENEMY_ITEM_OBJECT_SET):
            domain = 1
            id_range = range(0xB0, 0xC0)
        else:
            return False

        return any(
            parsed_object.domain == domain and parsed_object.obj_id in id_range for parsed_object in self.parsed_objects
        )
