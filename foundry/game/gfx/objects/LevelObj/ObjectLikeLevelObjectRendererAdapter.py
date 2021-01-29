from typing import List, Tuple

from PySide2.QtCore import QRect, QSize

from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.ObjectSet import ObjectSet
from foundry.game.ObjectDefinitions import EndType, GeneratorType
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from foundry.game.gfx.objects.LevelObj.LevelObject import LevelObject
from foundry.game.gfx.objects.LevelObj.LevelObjectRenderer import LevelObjectRenderer
from foundry.game.gfx.drawable.Block import Block


ENDING_STR = {
    EndType.UNIFORM: "Uniform",
    EndType.END_ON_TOP_OR_LEFT: "Top or Left",
    EndType.END_ON_BOTTOM_OR_RIGHT: "Bottom or Right",
    EndType.TWO_ENDS: "Top & Bottom/Left & Right",
}


ORIENTATION_TO_STR = {
    GeneratorType.HORIZONTAL: "Horizontal",
    GeneratorType.VERTICAL: "Vertical",
    GeneratorType.DIAG_DOWN_LEFT: "Diagonal ↙",
    GeneratorType.DESERT_PIPE_BOX: "Desert Pipe Box",
    GeneratorType.DIAG_DOWN_RIGHT: "Diagonal ↘",
    GeneratorType.DIAG_UP_RIGHT: "Diagonal ↗",
    GeneratorType.HORIZ_TO_GROUND: "Horizontal to the Ground",
    GeneratorType.HORIZONTAL_2: "Horizontal Alternative",
    GeneratorType.DIAG_WEIRD: "Diagonal Weird",  # up left?
    GeneratorType.SINGLE_BLOCK_OBJECT: "Single Block",
    GeneratorType.CENTERED: "Centered",
    GeneratorType.PYRAMID_TO_GROUND: "Pyramid to Ground",
    GeneratorType.PYRAMID_2: "Pyramid Alternative",
    GeneratorType.TO_THE_SKY: "To the Sky",
    GeneratorType.ENDING: "Ending",
}


class ObjectLikeLevelObjectRendererAdapter(ObjectLike):
    """
    This class treats a LevelObjectRenderer as a ObjectLike object.
    This is desired as ObjectLike contains many methods that do no transfer nicely into a LevelObject.
    This adapter solves this problem by providing an interface to convert between the two.
    """

    def __init__(self, level_object_renderer: LevelObjectRenderer):
        self.level_object_renderer = level_object_renderer

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.level_object_renderer})"

    @classmethod
    def as_legacy(
        cls,
        data: bytearray,
        object_set: int,
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        objects_ref: List[ObjectLike],
        is_vertical: bool,
        index: int,
        size_minimal: bool = False,
    ):
        """
        A deprecated method used for backwards compatibility of the previous LevelObject
        """
        level_obj = LevelObject.from_bytes(ObjectSet(object_set), data, is_vertical)
        level_obj_renderer = LevelObjectRenderer(
            level_obj, palette_group, graphics_set, objects_ref, index, is_vertical, size_minimal
        )
        return cls(level_obj_renderer)

    @property
    def data(self):
        return self.level_object_renderer.to_bytes()

    @property
    def object_set(self):
        return self.level_object_renderer.object_set

    @property
    def palette_group(self):
        return self.level_object_renderer.palette_group

    @property
    def is_single_block(self) -> bool:
        return self.level_object_renderer.index <= 0x0F

    @property
    def selected(self) -> bool:
        return self.level_object_renderer.selected

    @selected.setter
    def selected(self, selected: bool) -> None:
        self.level_object_renderer.selected = selected

    @property
    def type(self):
        return self.level_object_renderer.type

    @property
    def blocks(self) -> List[int]:
        return self.level_object_renderer.blocks

    @property
    def object_info(self):
        return self.level_object_renderer.object_set.number, self.domain, self.object_index

    @property
    def x_position(self) -> int:
        return self.level_object_renderer.x

    @property
    def y_position(self) -> int:
        return self.level_object_renderer.y

    @property
    def rendered_width(self) -> int:
        return self.level_object_renderer.block_group_renderer.width

    @property
    def rendered_height(self) -> int:
        return self.level_object_renderer.block_group_renderer.height

    @property
    def object_index(self) -> int:
        return self.level_object_renderer.index

    @object_index.setter
    def object_index(self, index: int) -> None:
        self.level_object_renderer.index = index

    @property
    def obj_index(self) -> int:
        return self.object_index

    @obj_index.setter
    def obj_index(self, index: int) -> None:
        self.object_index = index

    @property
    def domain(self) -> int:
        return self.level_object_renderer.domain

    @domain.setter
    def domain(self, domain: int) -> None:
        self.level_object_renderer.domain = domain

    @property
    def orientation(self) -> GeneratorType:
        return GeneratorType(self.level_object_renderer.orientation)

    @property
    def name(self) -> str:
        return self.level_object_renderer.object_set.get_definition_of(self.level_object_renderer.type).description

    @property
    def index_in_level(self) -> int:
        return self.level_object_renderer.index_in_level

    @property
    def rect(self) -> QRect:
        # Represent what it actually looks like by retrieving renderer's rect
        x = self.level_object_renderer.block_group_renderer.x
        y = self.level_object_renderer.block_group_renderer.y
        return QRect(x, y, self.rendered_width, self.rendered_height)

    @rect.setter
    def rect(self, rect: QRect) -> None:
        x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
        width = width - self.rendered_width + self.level_object_renderer.width
        height = height - self.rendered_height + self.level_object_renderer.height
        self.level_object_renderer.rect = ((x, y), (width, height))

    def display_size(self, zoom_factor: int = 1):
        return QSize(self.rendered_width * Block.SIDE_LENGTH, self.rendered_height * Block.SIDE_LENGTH) * zoom_factor

    @property
    def is_4byte(self) -> bool:
        return self.level_object_renderer.bytes == 4

    def render(self) -> None:
        self.level_object_renderer.has_updated = True  # Require an update next draw

    def draw(self, dc, zoom, transparent):
        self.level_object_renderer.draw(dc, zoom, transparent)

    def get_status_info(self) -> List[tuple]:
        return [
            ("x", self.level_object_renderer.x),
            ("y", self.level_object_renderer.y),
            ("Width", self.level_object_renderer.width),
            ("Height", self.level_object_renderer.height),
            ("Orientation", ORIENTATION_TO_STR[GeneratorType(self.level_object_renderer.orientation)]),
            (
                "Ending",
                ENDING_STR[
                    EndType(
                        self.level_object_renderer.object_set.get_definition_of(self.level_object_renderer.type).ending
                    )
                ],
            ),
        ]

    def set_position(self, x, y) -> None:
        self.level_object_renderer.position = (x, y)

    def move_by(self, dx, dy) -> None:
        x, y = self.level_object_renderer.position
        self.level_object_renderer.position = (x + dx, y + dy)

    def get_position(self) -> Tuple[int, int]:
        return self.level_object_renderer.position

    def resize_by(self, dx, dy):
        if not dx:
            dx = self.level_object_renderer.width
        if not dy:
            dy = self.level_object_renderer.height
        self.level_object_renderer.size = (dx, dy)

    def point_in(self, x: int, y: int) -> bool:
        return self.rect.contains(x, y)

    def change_type(self, new_type):
        new_type += self.level_object_renderer.type
        if new_type < 0 and self.domain > 0:
            domain = self.domain - 1
            index = 0xF0
        elif new_type > 0xFF and self.domain < 7:
            domain = self.domain + 1
            index = 0x00
        else:
            index = max(0, min(0xFF, new_type))
            domain = self.domain
        self.level_object_renderer.domain = domain
        self.level_object_renderer.index = index

    def __contains__(self, position: Tuple[int, int]) -> bool:
        return self.point_in(*position)

    def to_bytes(self) -> bytearray:
        return self.level_object_renderer.to_bytes()

    def expands(self):
        return self.level_object_renderer.expansion

    def primary_expansion(self):
        return self.level_object_renderer.index_expansion

    def as_image(self):
        return self.level_object_renderer.as_image()

    def increment_type(self):
        self.change_type(True)

    def decrement_type(self):
        self.change_type(False)

    def change_type(self, increment: int):
        if self.obj_index < 0x10 or self.obj_index == 0x10 and not increment:
            value = 1
        else:
            self.obj_index = self.obj_index // 0x10 * 0x10
            value = 0x10

        if not increment:
            value *= -1

        new_type = self.obj_index + value

        if new_type < 0 and self.domain > 0:
            new_domain = self.domain - 1
            new_type = 0xF0
        elif new_type > 0xFF and self.domain < 7:
            new_domain = self.domain + 1
            new_type = 0x00
        else:
            new_type = min(0xFF, new_type)
            new_type = max(0, new_type)

            new_domain = self.domain

        self.level_object_renderer.domain = new_domain
        self.level_object_renderer.index = new_type
