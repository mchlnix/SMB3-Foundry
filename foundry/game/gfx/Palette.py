"""Load and persist SMB3 palette groups for editor rendering.

This module turns SMB3's tileset-indexed palette tables into editable
``PaletteGroup`` objects that Foundry can share across block rendering, object
rendering, and palette-editor workflows. It is the boundary between ROM-backed
palette bytes and the in-memory palette rows that the editor mutates before
writing colors back to the ROM.

See Also
--------
foundry.game.gfx.GraphicsSet
    Supplies the graphics data that is rendered with the palette rows loaded
    here.
foundry.game.gfx.drawable.Block
    Consumes these palette groups when converting SMB3 tile data into Qt
    renderable blocks.
"""

from contextlib import suppress
from dataclasses import dataclass

from PySide6.QtGui import QColor

from foundry import root_dir
from foundry.game.File import ROM
from foundry.gui.util import grouper
from smb3parse.constants import Constants
from smb3parse.levels import BASE_OFFSET
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

PALETTE_PRG_NO = 22

PALETTE_BASE_ADDRESS = BASE_OFFSET + PALETTE_PRG_NO * PRG_BANK_SIZE
PALETTE_OFFSET_LIST_JP = 0x374AB  # found by searching through the JP ROM, calculating backwards to find the offset list
PALETTE_OFFSET_SIZE = 2  # bytes

PALETTE_GROUPS_PER_OBJECT_SET = 8
ENEMY_PALETTE_GROUPS_PER_OBJECT_SET = 4
PALETTES_PER_PALETTES_GROUP = 4

COLORS_PER_PALETTE = 4
COLOR_SIZE = 1  # byte

PALETTE_DATA_SIZE = (
    (PALETTE_GROUPS_PER_OBJECT_SET + ENEMY_PALETTE_GROUPS_PER_OBJECT_SET)
    * PALETTES_PER_PALETTES_GROUP
    * COLORS_PER_PALETTE
)

color_data = root_dir.joinpath("data", "Default.pal").read_bytes()

NES_COLOR_COUNT = 64
BYTES_IN_COLOR = 3 + 1  # bytes + separator
assert len(color_data) == NES_COLOR_COUNT * BYTES_IN_COLOR, (
    len(color_data),
    NES_COLOR_COUNT * BYTES_IN_COLOR,
)

NESPalette = [QColor(r, g, b) for r, g, b, _ in grouper(color_data, 4, incomplete="strict")]


@dataclass(eq=False)
class PaletteGroup:
    """Represent one SMB3 palette group.

    The NES PPU exposes color as 6-bit indexes into a 64-color palette, and each background or
    sprite palette contains four entries. SMB3 stores palette groups by tileset; each group here is
    the four 4-color rows selected by a level header for object rendering.

    Attributes
    ----------
    _object_set : int
        Object set whose tileset selects the palette offset table entry.
    _offset : int
        ROM address of the palette offset list used to load or save the group.
    _palettes : list[bytearray]
        Four palette rows, each containing four NES color indexes.
    changed : bool
        Class-level flag set when any palette edit needs to be saved or restored.
    index : int
        Palette-group index selected by the level header.

    Notes
    -----
    The class exists so Foundry can treat one ROM-selected palette group as a
    stable editing unit. Renderers, block caches, and palette editors all share
    the same in-memory rows here, while ``save`` remains the one persistence
    boundary that folds those edits back into SMB3's tileset-indexed tables.

    Examples
    --------
    Editor code usually loads one group, mutates its rows in memory, and then
    persists the shared result back to the ROM::

        palette_group = load_palette_group(object_set=1, palette_group_index=0)
        palette_group[0] = bytearray([0x0F, 0x21, 0x11, 0x01])
        palette_group.save()

    The same object also acts as the rollback point when a palette edit should
    be discarded instead of written back::

        palette_group[0] = bytearray([0x0F, 0x30, 0x21, 0x11])
        palette_group.restore()
    """

    _object_set: int
    index: int  # needed for cache keys outside
    _offset: int
    _palettes: list[bytearray]

    changed = False

    def restore(self):
        """Restore this group from ROM data.

        This discards editor changes for the group and reloads the original four palette rows using
        the same object-set and palette-group index. In other words, it is the
        rollback path from shared in-memory palette edits back to the ROM-backed
        baseline that rendering and editor tools started from.

        Examples
        --------
        Palette-editor code can abandon staged color edits by reloading the
        active ROM-backed rows::

            palette_group[0] = bytearray([0x0F, 0x30, 0x21, 0x11])
            palette_group.restore()
        """
        new_palette_group = load_palette_group(self._object_set, self.index, use_cache=False)

        self._palettes = new_palette_group._palettes

    def __getitem__(self, item):
        """Fetch one palette row by index.

        Renderers use the returned four-color row when converting NES color
        indexes into Qt colors, so this is the read path from a palette-group
        wrapper into one concrete SMB3 palette row.

        Parameters
        ----------
        item : int
            Palette row index within the group.

        Returns
        -------
        bytearray
            Four NES color indexes for the selected row.
        """
        return self._palettes[item]

    def __setitem__(self, key, value):
        """Replace a palette row.

        The palette editor writes rows through this mapping-style API before the group is persisted
        back to ROM, so the mutation updates the in-memory editing state that a
        later ``save`` call will serialize.

        Parameters
        ----------
        key : int
            Palette row index within the group.
        value : bytearray
            Replacement row of four NES color indexes.
        """
        self._palettes[key] = value

    def __eq__(self, other):
        """Compare whether two palette groups refer to the same ROM-backed slot.

        Equality follows the cache identity of object set and palette-group
        index rather than a deep comparison of edited color rows.

        Parameters
        ----------
        other : object
            Palette group to compare.

        Returns
        -------
        bool
            True when both objects refer to the same palette-group slot.

        Raises
        ------
        TypeError
            If ``other`` is not a ``PaletteGroup``.
        """
        if not isinstance(other, PaletteGroup):
            raise TypeError(f"Cannot compare PaletteGroup with {type(other)}.")

        return hash(self) == hash(other)

    def __hash__(self):
        """Compute the cache hash for this palette group.

        The hash matches the cache key used by ``load_palette_group``, so cache
        lookups, equality checks, and shared palette state all agree on what
        counts as "the same ROM palette slot."

        Returns
        -------
        int
            Hash of the object set and palette-group index.
        """
        return hash((self._object_set, self.index))

    def save(self, rom: Rom | None = None):
        """Write this palette group back to ROM.

        SMB3 stores palette rows behind a tileset-indexed offset table. Saving
        resolves the same offset used for loading, then writes the four palette
        rows sequentially so editor-side color changes become ROM-visible
        palette data. Once this write completes, later block rendering,
        object rendering, and ROM saves all observe the updated colors through
        normal ROM reads. This is the persistence boundary for palette editing:
        all in-memory row edits remain shared editor state until this method
        commits them back to SMB3's palette tables.

        Parameters
        ----------
        rom : Rom | None, optional
            ROM data source used for game data lookups.
        """
        if rom is None:
            rom = ROM()

        palette_offset_position = self._offset + (self._object_set * PALETTE_OFFSET_SIZE)
        palette_offset = rom.little_endian(palette_offset_position)

        palette_address = PALETTE_BASE_ADDRESS + palette_offset
        palette_address += self.index * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

        palettes = []

        for palette in self._palettes:
            palettes.append(rom.write(palette_address, palette))

            palette_address += COLORS_PER_PALETTE


_palette_group_cache: dict[tuple[int, int], PaletteGroup] = {}


def load_palette_group(object_set: int, palette_group_index: int, use_cache=True) -> PaletteGroup:
    """Load the palette group selected by a level header.

    This mirrors SMB3's palette-selection path: the object set chooses a tileset offset table entry,
    and the level header chooses which four-row object palette group to use. Foundry keeps the
    resolved group cached so renderers and dialogs share the same edited palette state.

    Parameters
    ----------
    object_set : int
        Object set whose tileset selects the SMB3 palette offset table entry.
    palette_group_index : int
        Level-header palette group index within the object-set palette data.
    use_cache : bool, optional
        Whether to reuse cached palette data instead of reading from ROM.

    Returns
    -------
    PaletteGroup
        Palette group containing the four resolved palette rows.

    Raises
    ------
    ValueError
        If neither the US nor JP palette offset table yields valid NES color indexes.
    """
    key = (object_set, palette_group_index)

    if use_cache and key in _palette_group_cache:
        return _palette_group_cache[key]

    # the data is in different locations for US and JP roms
    for palette_offset_list in (Constants.Palette_By_Tileset, PALETTE_OFFSET_LIST_JP):
        # ignore ValueError when we don't find valid palette data, might be the other version
        with suppress(ValueError):
            palettes = _load_palettes_from_rom(object_set, palette_group_index, palette_offset_list)
            _palette_group_cache[key] = PaletteGroup(object_set, palette_group_index, palette_offset_list, palettes)

            return _palette_group_cache[key]
    else:
        raise ValueError("Couldn't find valid Palette data at offsets for stock US or stock JP ROM.")


def _load_palettes_from_rom(object_set, palette_group_index, palette_offset_list_address: int):
    """Read four palette rows from ROM.

    SMB3 stores object-set palette data behind a table of little-endian offsets. The resolved data
    is interpreted as four rows of four NES color indexes, matching the PPU palette shape used for
    background and sprite rendering.

    Parameters
    ----------
    object_set : int
        Object set whose tileset selects the palette offset table entry.
    palette_group_index : int
        Level-header palette group index within the object-set palette data.
    palette_offset_list_address : int
        ROM palette offset list address.

    Returns
    -------
    list[bytearray]
        Four palette rows, each containing four NES color indexes.

    Raises
    ------
    ValueError
        If any loaded color index is outside the NES PPU's 64-color range.
    """
    rom = ROM()

    palette_offset_position = palette_offset_list_address + (object_set * PALETTE_OFFSET_SIZE)
    palette_offset = rom.little_endian(palette_offset_position)

    palette_address = PALETTE_BASE_ADDRESS + palette_offset
    palette_address += palette_group_index * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

    palettes = []

    for _ in range(PALETTES_PER_PALETTES_GROUP):
        palettes.append(bytearray(rom.read(palette_address, COLORS_PER_PALETTE)))

        palette_address += COLORS_PER_PALETTE

    # There are 64 colors in the NES's palette. Any other value indicates, that we did not find the right palette data
    if not all(color_index in range(NES_COLOR_COUNT) for palette in palettes for color_index in palette):
        raise ValueError("Found invalid Palette index value. Probably didn't find correct Palette Data in ROM.")

    return palettes


def save_all_palette_groups(rom: Rom | None = None):
    """Save every cached palette group.

    Palette edits are shared through the module cache. This function flushes every cached group back
    through the same offset-table layout SMB3 uses, then clears the global dirty flag when saving to
    the active ROM.

    Parameters
    ----------
    rom : Rom | None, optional
        ROM data source used for game data lookups.
    """
    for palette_group in _palette_group_cache.values():
        palette_group.save(rom)

    if rom is None:
        PaletteGroup.changed = False


def bg_color_for_object_set(object_set_number: int, palette_group_index: int) -> QColor:
    """Return the backdrop color for an object set and palette group.

    NES palette entry 0 is the universal backdrop color for a palette group. Foundry uses it as the
    level preview background for the selected object set and level-header palette index.

    Parameters
    ----------
    object_set_number : int
        Object set number that selects graphics and object definitions.
    palette_group_index : int
        Index of the palette group.

    Returns
    -------
    QColor
        Background color for the object set.
    """
    palette_group = load_palette_group(object_set_number, palette_group_index)

    return bg_color_for_palette_group(palette_group)


def bg_color_for_palette_group(palette_group: PaletteGroup) -> QColor:
    """Return the backdrop color for a loaded palette group.

    The first byte of the first palette row maps to the PPU backdrop color, which is shown wherever
    background and sprites are transparent.

    Parameters
    ----------
    palette_group : PaletteGroup
        Palette group used for drawing the object.

    Returns
    -------
    QColor
        Background color for the palette group.
    """
    return NESPalette[palette_group[0][0]]
