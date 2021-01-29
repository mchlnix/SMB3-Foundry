from typing import Tuple
from abc import abstractmethod

from foundry.game.ObjectSet import ObjectSet


def get_orientation_of_generator(object_set: ObjectSet, type: int) -> int:
    """
    Finds the orientation of a generator from a tileset and type of the generator
    :param object_set: The tileset
    :param type: The type of the generator
    :return: The orientation or generator utilized in game
    """
    return object_set.get_definition_of(type).orientation


def get_type_of_generator(domain: int, index: int) -> int:
    """
    The index into the types of blocks into a ObjectSet from a given index and domain
    For every domain there are 16 single-block 'types' and 15 multi-block 'types'
    Single-Block generators exist as the first 16 generators 'types' of the domain
    Multi-Block generators exist inside the remainder 240 indexes, partitioned every 16 indexes
    :param domain: The domain of the generator
    :param index: The index of the generator
    :return: The type of the object
    """
    domain_offset = domain * 0x1F  # There are 31 types in a single domain

    if index <= 0x0F:
        return index + domain_offset

    # There are 16 types already used from the single-block types, one is derived from the bit shift and
    # the others are added directly by the 15
    return (index >> 4) + domain_offset + 15


class AbstractLevelObject:
    """
    A generic interface to generate a LevelObject from
    """

    _width: int
    _height: int
    _x: int
    _y: int

    def __init__(self, object_set: ObjectSet, domain: int, index: int, rect: Tuple[Tuple[int, int], Tuple[int, int]]):
        self.object_set: ObjectSet = object_set
        self.domain: int = domain
        self.index: int = index
        self.rect = rect

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.object_set}, {self.domain}, {self.index}, {self.rect})"

    @property
    def orientation(self) -> int:
        """
        The type of generator used to create the object
        """
        return get_orientation_of_generator(self.object_set, self.type)

    @property
    def type(self) -> int:
        """
        The index into the types of blocks into a ObjectSet from a given index and domain
        For every domain there are 16 single-block 'types' and 15 multi-block 'types'
        Single-Block generators exist as the first 16 generators 'types' of the domain
        Multi-Block generators exist inside the remainder 240 indexes, partitioned every 16 indexes
        """
        return get_type_of_generator(self.domain, self.index)

    @property
    def width(self) -> int:
        """
        The width of the generator
        """
        return self._width

    @width.setter
    @abstractmethod
    def width(self, width: int) -> None:
        pass

    @property
    def height(self) -> int:
        """
        The height of the generator
        """
        return self._height

    @height.setter
    @abstractmethod
    def height(self, height):
        pass

    @property
    def size(self) -> Tuple[int, int]:
        """
        The width and height of the generator
        """
        return self.width, self.height

    @size.setter
    def size(self, size: Tuple[int, int]) -> None:
        self.width, self.height = size

    @property
    def x(self) -> int:
        """
        The x coordinate of the generator
        """
        return self._x

    @x.setter
    @abstractmethod
    def x(self, x: int) -> None:
        pass

    @property
    def y(self) -> int:
        """
        The y coordinate of the generator
        """
        return self._y

    @y.setter
    @abstractmethod
    def y(self, y: int) -> None:
        pass

    @property
    def position(self) -> Tuple[int, int]:
        """
        The position of the generator
        """
        return self.x, self.y

    @position.setter
    def position(self, position: Tuple[int, int]) -> None:
        self.x, self.y = position

    @property
    def rect(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        The position and size of the generator as a representation of into 2D space
        """
        return self.position, self.size

    @rect.setter
    def rect(self, rect: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
        self.position, self.size = rect
