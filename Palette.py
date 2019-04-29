from Data import NESPalette
from File import ROM

MAP_PALETTE_ADDRESS = 0x36BE2
PALETTE_ADDRESS = 0x36CA2

LEVEL_PALETTE_GROUPS_PER_OBJECT_SET = 8
ENEMY_PALETTE_GROUPS_PER_OBJECT_SET = 4
PALETTES_PER_PALETTES_GROUP = 4

COLORS_PER_PALETTE = 4
COLOR_SIZE = 1  # byte

PALETTE_DATA_SIZE = (
    (LEVEL_PALETTE_GROUPS_PER_OBJECT_SET + ENEMY_PALETTE_GROUPS_PER_OBJECT_SET)
    * PALETTES_PER_PALETTES_GROUP
    * COLORS_PER_PALETTE
)


def load_palette(object_set, palette_group):
    rom = ROM()

    palette_offset = MAP_PALETTE_ADDRESS + (object_set * PALETTE_DATA_SIZE)
    palette_offset += palette_group * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

    rom.seek(palette_offset)

    palettes = []
    for _ in range(PALETTES_PER_PALETTES_GROUP):
        palettes.append(rom.bulk_read(COLORS_PER_PALETTE))

    return palettes


def get_bg_color_for(object_set, palette_group):
    palette = load_palette(object_set, palette_group)

    return NESPalette[palette[0][0]]
