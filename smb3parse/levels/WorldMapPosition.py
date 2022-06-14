import typing
from typing import Tuple

if typing.TYPE_CHECKING:
    from world_map import WorldMap


class WorldMapPosition:
    def __init__(self, world, screen: int, row: int, column: int):
        self.world: "WorldMap" = world
        self.screen = screen
        self.row = row
        self.column = column

    @property
    def level_info(self) -> Tuple[int, int, int]:
        return self.world.level_for_position(self.screen, self.row, self.column)

    def can_have_level(self):
        """Whether the position and tile supports entering a level."""
        return self.world.is_enterable(self.tile())

    def sprite(self):
        return self.world.sprite_at(self.screen, self.row, self.column)[0]

    def item(self):
        return self.world.sprite_at(self.screen, self.row, self.column)[1]

    def has_sprite(self):
        return bool(self.sprite())

    def tile(self):
        return self.world.tile_at(self.screen, self.row, self.column)

    def tuple(self):
        return self.world.number, self.screen, self.row, self.column

    def __eq__(self, other):
        if not isinstance(other, WorldMapPosition):
            return False

        return (
            self.world.number == other.world.number
            and self.screen == other.screen
            and self.row == other.row
            and self.column == other.column
        )

    def __repr__(self):
        return f"WorldMapPosition({self.world}, screen={self.screen}, row={self.row}, column={self.column})"
