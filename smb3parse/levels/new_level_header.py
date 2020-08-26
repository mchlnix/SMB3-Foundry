from foundry.core.util import LEVEL_BASE_OFFSET, LEVEL_HEADER_LENGTH, LEVEL_MIN_LENGTH, LEVEL_PARTITION_LENGTH, \
    LEVEL_BASE_HEIGHT, LEVEL_BASE_WIDTH, OBJECT_BASE_OFFSET
from smb3parse.objects.object_set import ObjectSet, assert_valid_object_set_number
from smb3parse.asm6_converter import to_hex
from dataclasses import dataclass
from foundry.core.geometry.Size.Size import Size
from foundry.core.geometry.Position.Position import Position
from foundry.game.Rect import Rect
from typing import Union

MARIO_X_POSITIONS = [0x18, 0x70, 0xD8, 0x80]  # 0x10249
MARIO_Y_POSITIONS = [0x17, 0x04, 0x00, 0x14, 0x07, 0x0B, 0x0F, 0x18]  # 0x3D7A0 + 0x3D7A8
LEGACY_TIMES = [400, 300, 200, 0]


@dataclass
class LevelHeader:
    next_tileset: int
    next_level: int
    vertical: bool
    size: Size
    start_pos: Position
    start_action: int
    scroll_type: int
    graphic_set: int
    time: int
    music_idx: int
    pipe_action: bool
    bg_palette_idx: int
    sfx_palette_idx: int
    jump_level_address: int = None  # These are for legacy roms
    jump_enemy_address: int = None

    @classmethod
    def legacy_from_bytes(cls, data: [bytearray, bytes], *args):
        """
        A function to load the base header of SMB3
        Note: This routine does not fully load the header.
        The alternative level cannot be explicitly found utilizing the header and must be found elsewhere.
        :param data: The bytes of the old header
        :param tileset: The tileset of the current level
        :return: LevelConfig
        """
        jump_object_set_number = data[6] & 0b0000_1111  # for indexing purposes
        jump_object_set = ObjectSet(jump_object_set_number)
        vertical = True if data[6] & 0b0001_0000 else False
        length = LEVEL_MIN_LENGTH + ((data[4] & 0b0000_1111) * LEVEL_PARTITION_LENGTH)
        return cls(
            next_level=0,
            next_tileset=data[6] & 0b0000_1111,
            vertical=vertical,
            size=Size(LEVEL_BASE_WIDTH, length) if vertical else Size(length, LEVEL_BASE_HEIGHT),
            start_pos=cls.get_legacy_start_position((data[5] & 0b0110_0000) >> 5, (data[4] & 0b1110_0000) >> 5),
            start_action=(data[7] & 0b1110_0000) >> 5,
            scroll_type=(data[6] & 0b0110_0000) >> 5,
            graphic_set=data[7] & 0b0001_1111,
            time=LEGACY_TIMES[(data[8] & 0b1100_0000) >> 6],
            music_idx=data[8] & 0b0000_1111,
            pipe_action=not (data[6] & 0b1000_0000),
            bg_palette_idx=data[5] & 0b0000_0111,
            sfx_palette_idx=(data[5] & 0b0001_1000) >> 3,
            jump_level_address=(data[1] << 8) + data[0] + jump_object_set.level_offset,
            jump_enemy_address=(data[3] << 8) + data[2] + OBJECT_BASE_OFFSET
        )

    @staticmethod
    def get_legacy_start_position(x: int, y: int) -> Position:
        """
        Convert the legacy start position into x/y cordinates
        :param x: The x position
        :param y: The y position
        :return: The position
        """
        return Position(MARIO_X_POSITIONS[x], MARIO_Y_POSITIONS[y])

    @property
    def jump_object_set_number(self) -> int:
        return self.next_tileset

    @jump_object_set_number.setter
    def jump_offset_set_number(self, next_tileset: int):
        self.next_tileset = next_tileset

    @property
    def is_vertical(self) -> bool:
        return self.vertical

    @is_vertical.setter
    def is_vertical(self, vertical: bool):
        self.vertical = vertical

    @property
    def graphic_set_index(self) -> int:
        """Legacy routine for backwards compatibility"""
        return self.graphic_set

    @graphic_set_index.setter
    def graphic_set_index(self, graphic_set: int):
        """Legacy routine for backwards compatibility"""
        self.graphic_set = graphic_set

    @property
    def object_palette_index(self) -> int:
        """Legacy routine for backwards compatibility"""
        return self.bg_palette_idx

    @object_palette_index.setter
    def object_palette_index(self, bg_palette_idx: int):
        """Legacy routine for backwards compatibility"""
        self.bg_palette_idx = bg_palette_idx

    @property
    def enemy_palette_index(self) -> int:
        """Legacy routine for backwards compatibility"""
        return self.sfx_palette_idx

    @enemy_palette_index.setter
    def enemy_palette_index(self, sfx_palette_idx):
        """Legacy routine for backwards compatibility"""
        self.sfx_palette_idx = sfx_palette_idx

    @property
    def start_x_index(self) -> int:
        """Converts the start index into the base game equivalent"""
        return MARIO_X_POSITIONS.index(self.start_pos.x)

    @start_x_index.setter
    def start_x_index(self, idx: int):
        """Takes the legacy version and upscales it into the modern equivalent"""
        self.start_pos.x = MARIO_X_POSITIONS[idx]

    @property
    def start_y_index(self) -> int:
        return MARIO_Y_POSITIONS.index(self.start_pos.y)

    @start_y_index.setter
    def start_y_index(self, idx: int):
        """Takes the legacy version and upscales it into the modern equivalent"""
        self.start_pos.y = MARIO_Y_POSITIONS[idx]

    def mario_position(self):
        x = MARIO_X_POSITIONS[self.start_x_index] >> 4
        y = MARIO_Y_POSITIONS[self.start_y_index]

        if self.is_vertical:
            y += (self.screens - 1) * 15  # TODO: Why?

        return x, y

    @property
    def time_index(self) -> int:
        """"Converts time to the legacy equivalent"""
        return LEGACY_TIMES.index(self.time)

    @time_index.setter
    def time_index(self, idx: int):
        """Takes the legacy version and upscales it into the modern equivalent"""
        self.start_pos.y = LEGACY_TIMES[idx]

    @property
    def pipe_ends_level(self) -> bool:
        """Legacy routine"""
        return self.pipe_action

    @pipe_ends_level.setter
    def pipe_ends_level(self, pipe_action: bool):
        """Legacy routine"""
        self.pipe_action = pipe_action

    @property
    def scroll_type_index(self) -> int:
        """Legacy routine"""
        return self.scroll_type

    @scroll_type_index.setter
    def scroll_type_index(self, scroll_type: int):
        """Legacy routine"""
        self.scroll_type = scroll_type

    @property
    def music_index(self) -> int:
        """Legacy routine"""
        return self.music_idx

    @music_index.setter
    def music_index(self, music_idx: int):
        """Legacy routine"""
        self.music_idx = music_idx

    @property
    def length(self) -> int:
        """Legacy routine"""
        return LEVEL_MIN_LENGTH + self.screens * LEVEL_PARTITION_LENGTH

    @property
    def width(self) -> int:
        """Legacy routine"""
        return self.size.width

    @width.setter
    def width(self, width: int):
        """Legacy routine"""
        self.size.width = width

    @property
    def height(self) -> int:
        """Legacy routine"""
        return self.size.height

    @height.setter
    def height(self, height: int):
        """Legacy routine"""
        self.size.height = height

    @property
    def screens(self):
        """Legacy routine"""
        length = self.size.width if self.vertical else self.size.height
        return (length - LEVEL_MIN_LENGTH) // LEVEL_PARTITION_LENGTH

    @screens.setter
    def screens(self, screens: int):
        """Legacy routine for compatibility"""
        length = LEVEL_MIN_LENGTH + (screens * LEVEL_PARTITION_LENGTH)
        self.size = Size(LEVEL_BASE_WIDTH, length) if self.vertical else Size(length, LEVEL_BASE_HEIGHT)

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
        return self.ASM6_BG_PALS[self.bg_palette_idx]

    ASM6_SPR_PALS = [
        "LEVEL2_OBJPAL_08", "LEVEL2_OBJPAL_09", "LEVEL2_OBJPAL_10", "LEVEL2_OBJPAL_11"
    ]

    @property
    def spr_palette_to_asm6(self):
        return self.ASM6_SPR_PALS[self.sfx_palette_idx]

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
        return self.ASM6_TILESETS[self.next_tileset]

    @property
    def vertical_to_asm6(self):
        if self.vertical:
            return "LEVEL3_VERTICAL | "
        else:
            return ""

    @property
    def pipe_exit_to_asm6(self):
        if not self.pipe_action:
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
            f"\n\t.byte {self.pipe_exit_to_asm6}{to_hex(self.scroll_type << 5)} | {self.vertical_to_asm6}" \
            f"{self.tileset_to_asm6}; Pipe exit | Scroll type | Vertical | Alt object set" \
            f"\n\t.byte {to_hex(self.start_action << 5)} | {to_hex(self.graphic_set)}" \
            f"; Start action | Graphic set" \
            f"\n\t.byte {to_hex(self.time_index << 6)} | {to_hex(self.music_idx)}; Time | Music"
        return s


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