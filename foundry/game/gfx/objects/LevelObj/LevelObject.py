

from foundry.game.ObjectDefinitions import GeneratorType
from foundry.game.ObjectSet import ObjectSet

from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT
from foundry.game.gfx.objects.LevelObj.AbstractLevelObject import \
    AbstractLevelObject, get_type_of_generator, get_orientation_of_generator


SCREEN_HEIGHT = 15
SCREEN_WIDTH = 16


_horizontal_generator_orientations = [
    GeneratorType.HORIZONTAL,
    GeneratorType.HORIZONTAL_2,
    GeneratorType.HORIZ_TO_GROUND,
    GeneratorType.DESERT_PIPE_BOX,
    GeneratorType.DIAG_DOWN_LEFT,
    GeneratorType.DIAG_DOWN_RIGHT,
    GeneratorType.DIAG_UP_RIGHT,
    GeneratorType.DIAG_WEIRD,
]
_vertical_generator_orientations = [
    GeneratorType.VERTICAL
]


def get_generators_bytes(object_set: ObjectSet, obj_type: int) -> int:
    """
    A method to find the amounts of bytes a given generator would take with an object set and type
    :param object_set: The tileset
    :param obj_type: The type of object
    :return: The amount of bytes the generator takes up
    """
    if object_set.get_definition_of(obj_type).is_4byte:
        return 4
    return 3


def get_generators_expansion(index: int, orientation: int, bytes_len: int):
    """
    Provides the valid ways a generator could expand
    For example: A 3 horizontal and vertical generator would expand horizontally and vertically respectively
    :param index: The index of the generator
    :param orientation: The orientation of the generator
    :param bytes_len: The bytes of the generator
    :return: The horizontal and vertical expansion types
    """
    if index <= 0x0F:  # Single or Prefab Block
        return EXPANDS_NOT
    elif bytes_len == 4:  # 4 byte objects can expand both ways
        return EXPANDS_BOTH
    elif GeneratorType(orientation) in _horizontal_generator_orientations:
        return EXPANDS_HORIZ
    elif GeneratorType(orientation) in [
        GeneratorType.VERTICAL,
        GeneratorType.DIAG_WEIRD
    ]:
        return EXPANDS_VERT
    else:
        return EXPANDS_NOT


def get_generators_index_expansions(index: int, orientation: int, bytes_len: int):
    """
    Provides if the width or height is stored inside the index or if nothing is stored in the index at all
    For example: A three horizontal and vertical generator would expand horizontally and vertically respectively
    A four byte object on the other hand stores would be reversed, because 255 cannot fit inside the index
    :param index: The index of the generator
    :param orientation: The orientation of the generator
    :param bytes_len: The bytes of the generator
    :return: The horizontal and vertical expansion types
    """
    if index <= 0x0F or GeneratorType(orientation) == GeneratorType.SINGLE_BLOCK_OBJECT:
        return EXPANDS_NOT

    if GeneratorType(orientation) in _horizontal_generator_orientations:
        if bytes_len == 4:
            return EXPANDS_VERT
        else:
            return EXPANDS_HORIZ
    elif GeneratorType(orientation) in _vertical_generator_orientations:
        if bytes_len == 4:  # Todo: Fix render function to consider expansion properly
            return EXPANDS_VERT
        else:
            return EXPANDS_HORIZ
    else:
        return EXPANDS_BOTH


class LevelObject(AbstractLevelObject):
    """
    A basic implementation of a level object
    """

    def __eq__(self, other):
        return self.to_bytes(False) == other.to_bytes(False)

    @classmethod
    def from_bytes(cls, object_set: ObjectSet, data: bytearray, is_vertical: bool):
        """
        Generates a LevelObject from bytes
        :param object_set: The tileset the generator derives from
        :param data: The bytes to be converted
        :param is_vertical: If the level the generator is in is vertical or not
        """
        # where to look for the graphic data?
        domain = (data[0] & 0b1110_0000) >> 5

        pos_main, pos_sec = data[1], data[0] & 0b0001_1111
        if is_vertical:
            offset = (pos_main // SCREEN_WIDTH) * SCREEN_HEIGHT

            pos_sec += offset
            pos_main %= SCREEN_WIDTH
        x, y = pos_main, pos_sec

        # describes what object it is
        index = data[2]

        # a classmethod cannot call a property, so we call it directly
        orientation = cls._orientation(object_set, obj_type := cls._type(domain, index))
        primary_expansion = cls._index_expansion(index, orientation, data_len := cls._bytes(object_set, obj_type))

        if primary_expansion == EXPANDS_NOT:
            width, height = 0, 0
        elif data_len == 3 and primary_expansion == EXPANDS_HORIZ:
            width, height = index & 0x0F, 0
        elif data_len == 3 and primary_expansion == EXPANDS_VERT:
            width, height = 0, index & 0x0F
        elif data_len == 4 and primary_expansion == EXPANDS_HORIZ:
            try:
                width, height = index & 0x0F, data[3]
            except IndexError:
                width, height = index & 0x0F, 0
        elif data_len == 4 and primary_expansion == EXPANDS_VERT:
            try:
                width, height = data[3], index & 0x0F
            except IndexError:
                width, height = 0, index & 0x0F
        else:
            print(GeneratorType(orientation))
            raise AttributeError(f"Invalid Index Expansion Value: {index}")

        return cls(object_set, domain, index, ((x, y), (width, height)))

    def to_bytes(self, is_vertical: bool) -> bytearray:
        """
        Converts the LevelObject to bytes
        :param is_vertical: If the level is a vertical level or not
        """

        if is_vertical:
            offset = self.y // SCREEN_HEIGHT

            pos_main = self.x + offset * SCREEN_WIDTH
            pos_sec = self.y % SCREEN_HEIGHT
        else:
            pos_main, pos_sec = self.x, self.y

        data = bytearray([(self.domain << 5) | pos_sec, pos_main, self.index])

        if self.bytes == 4:
            if self.index_expansion == EXPANDS_VERT:
                data.append(self.width)
            else:
                data.append(self.height)

        return data

    @property
    def bytes(self) -> int:
        """
        The length in bytes that the generator takes up
        """
        return get_generators_bytes(self.object_set, self.type)

    """
    _bytes is the method utilized by a given classmethod for determining the bytes a have.
    _bytes is used opposed to get_generator_bytes to allow for a subclass to override the bytes without
    breaking Liskov's Substitution Principle in a case where the new bytes method breaks the classmethods.
    Instead, the subclass is forced to denote how to change bytes in order to work, providing more control.
    """
    _bytes = get_generators_bytes

    @property
    def expansion(self):
        """
        All possible ways something could expand
        """
        return get_generators_expansion(self.index, self.orientation, self.bytes)

    """
    _expansion is the method utilized by a given classmethod for determining the expansions types of a generator.
    _expansion is used opposed to get_generators_expansion to allow for a subclass to override the bytes without
    breaking Liskov's Substitution Principle in a case where the new expansion method breaks the classmethods.
    Instead, the subclass is forced to denote how to change expansions in order to work, providing more control.
    """
    _expansion = get_generators_expansion

    @property
    def index_expansion(self):
        """
        The expansion utilized from the index of the generator
        """
        return get_generators_index_expansions(self.index, self.orientation, self.bytes)

    """
    _index_expansion is the method utilized by a given classmethod for determining the index expansion of a generator.
    _index_expansion is used opposed to get_generators_index_expansions to allow for a subclass to override the bytes 
    without breaking Liskov's Substitution Principle in a case where the new index_expansion method breaks the 
    classmethods.  Instead, the subclass is forced to denote how to change index_expansion in order to work, providing 
    more control.
    """
    _index_expansion = get_generators_index_expansions

    @property
    def index(self) -> int:
        """
        The index of the generator
        """
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        if hasattr(self, "_index") and index == self.index:
            return

        self._index = index

        if self.index_expansion == EXPANDS_NOT:
            self.width, self.height = 0, 0
        elif self.bytes == 3 and self.index_expansion == EXPANDS_HORIZ:
            self.width, self.height = self.index & 0x0F, 0
        elif self.bytes == 3 and self.index_expansion == EXPANDS_VERT:
            self.width, self.height = 0, self.index & 0x0F
        elif self.bytes == 4 and self.index_expansion == EXPANDS_HORIZ:
            self.width = index & 0x0F
        else:
            self.height = index & 0x0F

    @property
    def width(self) -> int:
        return super().width

    @width.setter
    def width(self, width: int) -> None:
        if hasattr(self, "_width") and width == self.width:
            return
        elif self.expansion == EXPANDS_NOT:
            self._width = 0
        elif self.index_expansion == EXPANDS_HORIZ:
            self._width = min(max(0, width), 0x0F)
            self._index = (self.index & 0xF0) + self._width
        else:
            self._width = min(max(0, width), 0xFF)

    @property
    def height(self) -> int:
        return super().height

    @height.setter
    def height(self, height):
        if hasattr(self, "_height") and height == self.height:
            return
        elif self.expansion == EXPANDS_NOT:
            self._height = 0
        elif self.index_expansion == EXPANDS_VERT:
            self._height = min(max(0, height), 0x0F)
            self._index = (self.index & 0xF0) + self._height
        else:
            self._height = min(max(0, height), 0xFF)

    @property
    def x(self) -> int:
        return super().x

    @x.setter
    def x(self, x: int) -> None:
        self._x = min(max(x, 0), 0xFF)

    @property
    def y(self) -> int:
        return super().y

    @y.setter
    def y(self, y: int) -> None:
        self._y = min(max(y, 0), 0xFF)

    """
    _type is the method utilized by a given classmethod for determining the type of the generator.
    _type is used opposed to get_type_of_generator to allow for a subclass to override the bytes without
    breaking Liskov's Substitution Principle in a case where the new type method breaks the classmethods.
    Instead, the subclass is forced to denote how to change _type in order to work, providing more control.
    """
    _type = get_type_of_generator

    """
    _orientation is the method utilized by a given classmethod for determining the generator utilized in game.
    _orientation is used opposed to get_orientation_of_generator to allow for a subclass to override the bytes without
    breaking Liskov's Substitution Principle in a case where the new orientation method breaks the classmethods.
    Instead, the subclass is forced to denote how to change _orientation in order to work, providing more control.
    """
    _orientation = get_orientation_of_generator
