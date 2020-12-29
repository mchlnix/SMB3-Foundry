from foundry.core.geometry.Position.Position import Position


class LevelPosition(Position):
    SCREEN_WIDTH = 0x10

    @property
    def rel_x(self) -> int:
        """The x position in terms of the screen the position is in"""
        return self.x % self.SCREEN_WIDTH

    @property
    def rel_x_inverse(self) -> int:
        """The x position in terms of the screen from right to left"""
        return self.SCREEN_WIDTH - self.rel_x

    @property
    def screen_pos(self) -> int:
        """Provides a way to combine the x and y position, useful for recreating in-game logic"""
        return self.x + (self.y * self.SCREEN_WIDTH)

    @classmethod
    def from_pos(cls, pos: Position) -> "LevelPosition":
        return cls(pos.x, pos.y)
