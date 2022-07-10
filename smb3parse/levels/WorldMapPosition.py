import typing

from smb3parse.data_points import LevelPointerData, Position

if typing.TYPE_CHECKING:
    from world_map import WorldMap


class WorldMapPosition(Position):
    def __init__(self, world, screen: int, row: int, column: int):
        super(WorldMapPosition, self).__init__(column, row, screen)
        self.world: "WorldMap" = world

    @property
    def level_pointer(self) -> LevelPointerData:
        return self.world.level_for_position(self)

    def can_have_level(self):
        """Whether the position and tile supports entering a level."""
        return self.world.is_enterable(self.tile())

    def sprite(self):
        return self.world.sprite_at(self)

    def has_sprite(self):
        return bool(self.sprite())

    def tile(self):
        return self.world.tile_at(self)

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
