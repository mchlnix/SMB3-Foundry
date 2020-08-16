from foundry.core.util import LEVEL_BASE_OFFSET, LEVEL_HEADER_LENGTH, LEVEL_MIN_LENGTH, LEVEL_PARTITION_LENGTH, \
    LEVEL_BASE_HEIGHT, LEVEL_BASE_WIDTH, OBJECT_BASE_OFFSET
from smb3parse.objects.object_set import ObjectSet, assert_valid_object_set_number
from smb3parse.asm6_converter import to_hex
from dataclasses import dataclass
from foundry.core.geometry.Size.Size import Size
from foundry.game.Position import Position
from foundry.game.Rect import Rect
from typing import Union

MARIO_X_POSITIONS = [0x18, 0x70, 0xD8, 0x80]  # 0x10249
MARIO_Y_POSITIONS = [0x17, 0x04, 0x00, 0x14, 0x07, 0x0B, 0x0F, 0x18]  # 0x3D7A0 + 0x3D7A8
LEGACY_TIMES = [400, 300, 200, 0]


class LevelHeader:
    def __init__(self, header_bytes: [bytearray, bytes], object_set_number: int):
        if len(header_bytes) != LEVEL_HEADER_LENGTH:
            raise ValueError(f"A level header is made up of {LEVEL_HEADER_LENGTH} bytes, but {len(header_bytes)} were given.")

        assert_valid_object_set_number(object_set_number)

        self._object_set_number = object_set_number
        self._object_set = ObjectSet(self._object_set_number)

        self.data = header_bytes

        self.start_y_index = (self.data[4] & 0b1110_0000) >> 5

        self.screens = self.data[4] & 0b0000_1111
        self.length = LEVEL_MIN_LENGTH + self.screens * LEVEL_PARTITION_LENGTH
        self.width = self.length
        self.height = LEVEL_BASE_HEIGHT

        self.start_x_index = (self.data[5] & 0b0110_0000) >> 5

        self.enemy_palette_index = (self.data[5] & 0b0001_1000) >> 3
        self.object_palette_index = self.data[5] & 0b0000_0111

        self.pipe_ends_level = not (self.data[6] & 0b1000_0000)
        self.scroll_type_index = (self.data[6] & 0b0110_0000) >> 5
        self.is_vertical = self.data[6] & 0b0001_0000

        if self.is_vertical:
            self.height = self.length
            self.width = LEVEL_BASE_WIDTH

        self.jump_object_set_number = self.data[6] & 0b0000_1111  # for indexing purposes
        self.jump_object_set = ObjectSet(self.jump_object_set_number)

        self.start_action = (self.data[7] & 0b1110_0000) >> 5

        self.graphic_set_index = self.data[7] & 0b0001_1111

        self.time_index = (self.data[8] & 0b1100_0000) >> 6

        self.music_index = self.data[8] & 0b0000_1111

        self.jump_level_address = (
            (self.data[1] << 8) + self.data[0] + self.jump_object_set.level_offset
        )
        self.jump_enemy_address = (self.data[3] << 8) + self.data[2] + OBJECT_BASE_OFFSET
        self.next_level = 0

    @property
    def alt_obj_address(self):
        return self.jump_level_address - self.jump_object_set.level_offset

    @property
    def alt_spr_address(self):
        return self.jump_enemy_address - OBJECT_BASE_OFFSET

    def mario_position(self):
        x = MARIO_X_POSITIONS[self.start_x_index] >> 4
        y = MARIO_Y_POSITIONS[self.start_y_index]

        if self.is_vertical:
            y += (self.screens - 1) * 15  # TODO: Why?

        return x, y

    ASM6_SCREENS = [
        "LEVEL1_SIZE_01", "LEVEL1_SIZE_02", "LEVEL1_SIZE_03", "LEVEL1_SIZE_04",
        "LEVEL1_SIZE_05", "LEVEL1_SIZE_06", "LEVEL1_SIZE_07", "LEVEL1_SIZE_08",
        "LEVEL1_SIZE_09", "LEVEL1_SIZE_10", "LEVEL1_SIZE_11", "LEVEL1_SIZE_12",
        "LEVEL1_SIZE_13", "LEVEL1_SIZE_14", "LEVEL1_SIZE_15", "LEVEL1_SIZE_16"
    ]

    @property
    def screen_to_asm6(self):
        return self.ASM6_SCREENS[self.screens]

    ASM6_Y_STARTS = [
        "LEVEL1_YSTART_170", "LEVEL1_YSTART_040", "LEVEL1_YSTART_000", "LEVEL1_YSTART_140",
        "LEVEL1_YSTART_070", "LEVEL1_YSTART_0B0", "LEVEL1_YSTART_0F0", "LEVEL1_YSTART_180"
    ]

    @property
    def start_y_to_asm6(self):
        return self.ASM6_Y_STARTS[self.start_y_index]

    ASM6_BG_PALS = [
        "LEVEL2_BGPAL_00", "LEVEL2_BGPAL_01", "LEVEL2_BGPAL_02", "LEVEL2_BGPAL_03",
        "LEVEL2_BGPAL_04", "LEVEL2_BGPAL_05", "LEVEL2_BGPAL_06", "LEVEL2_BGPAL_07"
    ]

    @property
    def bg_palette_to_asm6(self):
        return self.ASM6_BG_PALS[self.object_palette_index]

    ASM6_SPR_PALS = [
        "LEVEL2_OBJPAL_08", "LEVEL2_OBJPAL_09", "LEVEL2_OBJPAL_10", "LEVEL2_OBJPAL_11"
    ]

    @property
    def spr_palette_to_asm6(self):
        return self.ASM6_SPR_PALS[self.enemy_palette_index]

    ASM6_X_STARTS = [
        "LEVEL2_XSTART_18", "LEVEL2_XSTART_70", "LEVEL2_XSTART_D8", "LEVEL2_XSTART_80"
    ]

    @property
    def x_start_to_asm6(self):
        return self.ASM6_X_STARTS[self.start_x_index]

    ASM6_TILESETS = [
        "LEVEL3_TILESET_00", "LEVEL3_TILESET_01", "LEVEL3_TILESET_02", "LEVEL3_TILESET_03",
        "LEVEL3_TILESET_04", "LEVEL3_TILESET_05", "LEVEL3_TILESET_06", "LEVEL3_TILESET_07",
        "LEVEL3_TILESET_08", "LEVEL3_TILESET_09", "LEVEL3_TILESET_10", "LEVEL3_TILESET_11",
        "LEVEL3_TILESET_12", "LEVEL3_TILESET_13", "LEVEL3_TILESET_14", "LEVEL3_TILESET_15"
    ]

    @property
    def tileset_to_asm6(self):
        return self.ASM6_TILESETS[self.jump_object_set_number]

    @property
    def vertical_to_asm6(self):
        if self.is_vertical:
            return "LEVEL3_VERTICAL | "
        else:
            return ""

    @property
    def pipe_exit_to_asm6(self):
        if not self.pipe_ends_level:
            return "LEVEL3_PIPENOTEXIT | "
        else:
            return ""

    def to_asm6(self, name):
        s = f"{name}_header:" \
            f"\n\t.byte {to_hex(self.next_level & 0xFF)}; Next Level" \
            f"\n\t.byte {self.screen_to_asm6} | {self.start_y_to_asm6}; Screens | Y Start" \
            f"\n\t.byte {to_hex((self.next_level & 0x0F00) >> 1)} | " \
            f"{self.x_start_to_asm6} | {self.spr_palette_to_asm6} | " \
            f"{self.bg_palette_to_asm6}; Next Level High | X Start | Sprite Palette | Block Palette" \
            f"\n\t.byte {self.pipe_exit_to_asm6}{to_hex(self.scroll_type_index << 5)} | {self.vertical_to_asm6}" \
            f"{self.tileset_to_asm6}; Pipe exit | Scroll type | Vertical | Alt object set" \
            f"\n\t.byte {to_hex(self.start_action << 5)} | {to_hex(self.graphic_set_index)}" \
            f"; Start action | Graphic set" \
            f"\n\t.byte {to_hex(self.time_index << 6)} | {to_hex(self.music_index)}; Time | Music"
        return s