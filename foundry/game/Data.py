"""Static SMB3 level metadata shared by ROM-backed level loading.

This module defines the lightweight records and tables that describe Foundry's
stock SMB3 level catalog before any per-level bytes are decoded. ``Mario3Level``
stores one row from the vanilla level lookup table, ``VANILLA_SMB3_LEVEL_COUNT``
captures the expected stock entry count, and ``mushroom_houses`` preserves the
editor-facing labels for the game's mushroom-house reward patterns.

The workflow role is deliberately narrow: :mod:`foundry.game.level` loads the
ROM-facing ``levels.dat`` table into ``Mario3Level`` records, then higher-level
editor code such as :mod:`foundry.game.level.Level` uses those records to map
layout addresses back to world numbers, level numbers, and human-readable
labels.

See Also
--------
foundry.game.level
    Loads ``levels.dat`` into ``Mario3Level`` records and world-index tables.
foundry.game.level.Level
    Consumes the loaded records when resolving level metadata during editing.

Examples
--------
Use ``Mario3Level`` as the typed container that travels from the static level
table into level lookup code::

    >>> from foundry.game.Data import Mario3Level
    >>> stock_level = Mario3Level(1, 1, 0x1FCA3, 0xC537, 0x01, "World 1-1")
    >>> stock_level.game_world, stock_level.level_in_world
    (1, 1)
    >>> hex(stock_level.rom_level_offset)
    '0x1fca3'
"""

from typing import NamedTuple

VANILLA_SMB3_LEVEL_COUNT = 298


class Mario3Level(NamedTuple):
    """Store one stock SMB3 level-table entry.

    Foundry loads the vanilla world and level lookup table into these records
    so code that maps a layout address back to a world or level number can pass
    around one typed metadata object instead of parallel integer lists.

    The data flow is ROM offset table -> ``Mario3Level`` records -> address
    lookups used by editor labels and level-loading helpers.

    Attributes
    ----------
    enemy_offset : int
        Enemy and item stream address for the stock level.
    game_world : int
        One-based SMB3 world number.
    level_in_world : int
        One-based level number within the world.
    name : str
        Human-readable level name from the stock table.
    real_obj_set : int
        Object-set number used to decode the level.
    rom_level_offset : int
        Layout and header stream address in the ROM.

    Examples
    --------
    The level table loader and the reverse-lookup helpers both treat one stock
    row as a single ``Mario3Level`` record::

        >>> from foundry.game.Data import Mario3Level
        >>> level = Mario3Level(1, 1, 0x1FCA3, 0xC537, 0x01, "World 1-1")
        >>> level.name
        'World 1-1'
        >>> hex(level.rom_level_offset), hex(level.enemy_offset)
        ('0x1fca3', '0xc537')
    """

    game_world: int
    level_in_world: int
    rom_level_offset: int
    enemy_offset: int
    real_obj_set: int
    name: str


mushroom_houses = [
    "P-Wing Only",
    "Warp Whistle Only",
    "P-Wing Only",
    "Frog Suit Only",
    "Tanooki Suit Only",
    "Hammer Suit Only",
    "Frog, Tanooki, Hammer Suit",
    "Mushroom, Leaf, Flower",
    "Leaf, Flower, Frog Suit",
    "Leaf, Flower, Tanooki Suit",
    "Anchor Only",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
]
