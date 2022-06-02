from PySide6.QtCore import QRect

from foundry.game.gfx.objects.LevelObject import GROUND, SCREEN_HEIGHT, SCREEN_WIDTH
from foundry.game.gfx.objects.ObjectLike import ObjectLike


class Jump(ObjectLike):
    POINTER_DOMAIN = 0b111

    SIZE = 3  # bytes

    def __init__(self, data):
        self.data = data

        # domain: 0b1110
        # unused: 0b0001

        self.blocks = []
        self.is_4byte = False
        self.name = "Jump object"

        assert self.is_jump(data)

        self.screen_index = data[0] & 0x0F
        self.exit_vertical = (data[1] & 0xF0) >> 4
        self.exit_action = data[1] & 0x0F
        # for some reason those are flipped, meaning 5678, 1234
        self.exit_horizontal = ((data[2] & 0xF) << 4) + (data[2] >> 4)

    def to_bytes(self):
        return self.data

    def __repr__(self):
        return (
            f"Jump: Screen #{self.screen_index}, "
            + f"Exit ({self.exit_horizontal}, {self.exit_vertical}), "
            + f"Action #{self.exit_action}"
        )

    def __str__(self):
        return f"Jump on screen #{self.screen_index}"

    @staticmethod
    def is_jump(data):
        return data[0] >> 5 == Jump.POINTER_DOMAIN

    @staticmethod
    def from_properties(screen_index, action, horiz, vert):
        data = bytearray(3)

        data[0] |= 0b1110_0000
        data[0] |= screen_index

        data[1] |= vert << 4
        data[1] |= action

        data[2] |= ((horiz & 0xF) << 4) + (horiz >> 4)

        return Jump(data)

    def render(self):
        pass

    def draw(self, dc, zoom, transparent):
        pass

    def get_status_info(self):
        return []

    def set_position(self, x, y):
        pass

    def move_by(self, dx, dy):
        pass

    def get_position(self):
        return 0, 0

    def resize_by(self, dx, dy):
        pass

    def point_in(self, x, y):
        return False

    def change_type(self, new_type):
        pass

    def get_rect(self, block_length=1, vertical=False) -> QRect:
        if vertical:
            return QRect(
                0,
                block_length * (1 + SCREEN_HEIGHT * self.screen_index),
                block_length * SCREEN_WIDTH,
                block_length * SCREEN_HEIGHT,
            )
        else:
            return QRect(
                block_length * SCREEN_WIDTH * self.screen_index,
                0,
                block_length * SCREEN_WIDTH,
                block_length * GROUND,
            )

    def __contains__(self, point):
        return False
