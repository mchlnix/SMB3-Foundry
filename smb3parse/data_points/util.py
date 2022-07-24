from builtins import NotImplementedError
from dataclasses import dataclass
from typing import Callable, overload

from smb3parse.levels import (
    FIRST_VALID_ROW,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
)
from smb3parse.util.rom import Rom


@dataclass
class Position:
    x: int
    y: int
    screen: int

    @property
    def tile_data_index(self):
        return self.screen * WORLD_MAP_SCREEN_SIZE + (self.row - FIRST_VALID_ROW) * WORLD_MAP_SCREEN_WIDTH + self.column

    @property
    def row(self):
        return self.y

    @row.setter
    def row(self, value):
        self.y = value

    @property
    def column(self):
        return self.x

    @column.setter
    def column(self, value):
        self.x = value

    @property
    def xy(self):
        return self.screen * WORLD_MAP_SCREEN_WIDTH + self.x, self.y

    def copy(self):
        return Position.from_xy(*self.xy)

    @staticmethod
    def from_xy(x, y):
        """
        Returns a Position object, with the screen and x coordinate set from x and the y coordinate set from y.

        Expects the screen to be part of the x coordinate, so for a position of 5, 6 on screen 2, we would expect to get
        x=21, y=6.
        """
        screen = x // WORLD_MAP_SCREEN_WIDTH
        x = x % WORLD_MAP_SCREEN_WIDTH

        return Position(x, y, screen)

    @staticmethod
    def from_tile_data_index(index: int):
        screen = index // WORLD_MAP_SCREEN_SIZE
        index %= WORLD_MAP_SCREEN_SIZE

        row = index // WORLD_MAP_SCREEN_WIDTH
        index %= WORLD_MAP_SCREEN_WIDTH

        column = index

        return Position(column, row + FIRST_VALID_ROW, screen)

    def __add__(self, other):
        x, y = self.xy
        o_x, o_y = other.xy

        return Position.from_xy(x + o_x, y + o_y)

    def __neg__(self):
        x, y = self.xy
        return Position.from_xy(-x, -y)

    def __sub__(self, other):
        return self + -other


class DataPoint:
    def __init__(self, rom: Rom):
        self._rom = rom

        self.calculate_addresses()
        self.read_values()

    def calculate_addresses(self):
        raise NotImplementedError

    def read_values(self):
        raise NotImplementedError

    def write_back(self, rom: Rom = None):
        raise NotImplementedError


# TODO change to using position? in the back end or front?
class _PositionMixin:
    def __init__(self, *args, **kwargs):
        self.screen_address = 0x0
        self.screen = 0

        self.x_address = 0x0
        self.x = 0

        self.y_address = 0x0
        self.y = 0

        super(_PositionMixin, self).__init__(*args, **kwargs)

    @property
    def pos(self):
        return Position(self.x, self.y, self.screen)

    @pos.setter
    def pos(self, value):
        self.x = value.x
        self.y = value.y
        self.screen = value.screen

    @property
    def row(self):
        return self.y

    @row.setter
    def row(self, value):
        self.y = value

    @property
    def column(self):
        return self.x

    @column.setter
    def column(self, value):
        self.x = value

    @overload
    def is_at(self, position: Position) -> bool:
        ...

    @overload
    def is_at(self, screen: int, row: int, column: int) -> bool:
        ...

    def is_at(self, *args):
        pos = self._pos_from_args(*args)

        return self.screen == pos.screen and self.column == pos.column and self.row == pos.row

    @overload
    def set_pos(self, position: "Position") -> None:
        ...

    @overload
    def set_pos(self, screen: int, row: int, column: int) -> None:
        ...

    def set_pos(self, *args):
        if len(args) == 1:
            position = args[0]
            assert isinstance(position, Position), position

            self.screen = position.screen
            self.column = position.column
            self.row = position.row

        elif len(args) == 3:
            assert all(isinstance(coord, int) for coord in args)
            self.screen, self.row, self.column = args

        else:
            raise ValueError("Method takes one Position object or three integers as screen, row, column.")

    @staticmethod
    def _pos_from_args(*args):
        if len(args) == 1:
            position = args[0]
            assert isinstance(position, Position), position

            return position

        elif len(args) == 3:
            assert all(isinstance(coord, int) for coord in args), args

            screen, row, column = args

            return Position(column, row, screen)

        else:
            raise ValueError("Method takes one Position object or three integers as screen, row, column.")


class _IndexedMixin:
    index: int
    calculate_addresses: Callable

    def change_index(self, index: int):
        self.index = index

        self.calculate_addresses()
