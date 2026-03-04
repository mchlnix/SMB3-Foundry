from foundry.game.gfx.block_cache import BlockCache
from foundry.game.gfx.drawable.Block import Block, get_tile
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import PaletteGroup, _palette_group_cache


def restore_all_palettes():
    for palette_group in _palette_group_cache.values():
        palette_group.restore()

    get_tile.cache_clear()
    BlockCache.clear_cache()
    Block.clear_cache()
    PaletteGroup.changed = False


def restore_graphics():
    GraphicsSet.from_number.cache_clear()
    restore_all_palettes()


def change_color(
    palette_group: PaletteGroup,
    index_in_group: int,
    index_in_palette: int,
    new_color_index: int,
):
    # colors at index 0 are shared among all palettes of a palette group
    if index_in_palette == 0:
        for palette_ in palette_group._palettes:
            palette_[0] = new_color_index
    else:
        palette_group[index_in_group][index_in_palette] = new_color_index

    get_tile.cache_clear()
    BlockCache.clear_cache()
