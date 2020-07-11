from typing import Tuple
import yaml
from yaml import CLoader as Loader
from abc import ABC, abstractmethod

from foundry import data_dir
from smb3parse.asm6_converter import to_hex
from foundry.game.Size import Size
from foundry.game.Position import Position
from foundry.game.level.LevelConstants import SCREEN_WIDTH, SCREEN_HEIGHT
from foundry.game.ObjectDefinitions import ObjectDefinition as GeneratorDefinition
from foundry.game.ObjectDefinitions import get_generator_from_index, return_domain_and_index_from_generator, \
    get_tileset_from_index, get_type, from_type


with open(data_dir.joinpath("definition_to_generator_base.yaml")) as f:
    GENERATOR_INFORMATION = yaml.load(f, Loader=Loader)
NAMES = GENERATOR_INFORMATION["Names"]
DEFINITIONS = GENERATOR_INFORMATION["Definitions"]
CONVERT = GENERATOR_INFORMATION["Convert"]


class BlockGeneratorHandler:
    _block_generator: "BlockGeneratorBase"

    def __init__(self, block_generator: "BlockGeneratorBase"):
        self._block_generator = block_generator

    def __repr__(self) -> str:
        return f"BlockGeneratorHandler({self._block_generator})"

    def __str__(self) -> str:
        return f"BlockGeneratorHandler containing "\
               f"{self.block_generator.generator.description} at {self.position.x}, " \
               f"{self.position.y} with a size of {self.base_size.width}x{self.base_size.height}"

    def __len__(self) -> int:
        return len(self.block_generator.to_bytes()[1])

    def __eq__(self, other: "BlockGeneratorHandler") -> bool:
        return self.block_generator == other.block_generator

    @property
    def block_generator(self) -> "BlockGeneratorBase":
        """The block generator that the class controls"""
        return self._block_generator

    @property
    def position(self) -> Position:
        """The horizontal position of the generator"""
        return self.block_generator.position

    @position.setter
    def position(self, pos: Position) -> None:
        self.block_generator.position = pos

    @property
    def vertical_position(self) -> Position:
        """The vertical position of the generator"""
        return self.block_generator.vertical_position

    @vertical_position.setter
    def vertical_position(self, pos: Position) -> None:
        self.block_generator.vertical_position = pos

    @property
    def base_size(self) -> Size:
        """The base size of the generator"""
        return self.block_generator.base_size

    @base_size.setter
    def base_size(self, size: Size) -> None:
        self._block_generator = self._block_generator.change_size(size)

    @property
    def bmp_size(self) -> Size:
        return self.block_generator.bmp_size

    @property
    def real_size(self) -> Size:
        """The actual amount of space the generator should take up"""
        return self.block_generator.real_size

    @property
    def type(self) -> int:
        """The type of the generator in terms of its tileset"""
        domain, index = return_domain_and_index_from_generator(self.block_generator.generator_definition)
        return get_type(domain=domain, index=index)

    @type.setter
    def type(self, t: int) -> None:
        tileset = get_tileset_from_index(self.block_generator.generator_definition)
        generator_definition = (tileset << 11) + from_type(t)
        position, size = self.block_generator.position, self.block_generator.base_size
        self._block_generator = BlockGeneratorBase.generator_from_attributes(generator_definition, position, size)

    @property
    def tileset(self) -> int:
        """The tileset that this generator resides"""
        return get_tileset_from_index(self.block_generator.generator_definition)

    @tileset.setter
    def tileset(self, tileset: int) -> None:
        generator_definition = (tileset << 11) + self.block_generator.generator_definition & 0b0111_1111_1111
        position, size = self.block_generator.position, self.block_generator.base_size
        self._block_generator = BlockGeneratorBase.generator_from_attributes(generator_definition, position, size)

    def to_bytes(self) -> Tuple[int, bytearray]:
        return self.block_generator.to_bytes()

    def to_asm6(self) -> str:
        return self.block_generator.to_asm6()


def get_object_definition_index_from_data(tileset: int, data: bytearray) -> int:
    return (tileset << 11) + ((data[0] & 0b1110_0000) << 3) + data[2]


def get_simple_size(size: int) -> int:
    return min(max(size, 0), 0x0F)


def get_complex_size(size: int) -> int:
    return min(max(size, 0), 0xFF)


class BlockGeneratorBase(ABC):
    generator_definition: int
    position: Position
    base_size: Size

    def __init__(self, generator_definition: int, position: Position, base_size: Size):
        self._generator_definition = generator_definition
        self.position = position
        self._base_size = base_size

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._generator_definition}, {self._position}, {self._base_size})"

    def __str__(self) -> str:
        return f"{get_generator_from_index(self._generator_definition).description} at {self._position.x}, " \
               f"{self._position.y} with a size of {self._base_size.width}x{self._base_size.height}"

    def __len__(self) -> int:
        return len(self.to_bytes()[1])

    def __eq__(self, other: "BlockGeneratorBase") -> bool:
        return self.to_bytes() == other.to_bytes()

    @property
    def generator(self) -> GeneratorDefinition:
        """The generator definition from the generator index"""
        return get_generator_from_index(self._generator_definition)

    @property
    def generator_definition(self):
        """The generator index"""
        return self._generator_definition

    @property
    def position(self):
        """Where the generator is"""
        return self._position

    @position.setter
    def position(self, pos: Position):
        pos.y = max(min(0b0001_1111, pos.y), 0)
        pos.x = max(min(0xFF, pos.x), 0)
        self._position = pos

    @property
    def vertical_position(self):
        """Where the generator is in vertical space"""
        return Position(self.position.x % SCREEN_WIDTH,
                        self.position.y + (self.position.x // SCREEN_WIDTH * SCREEN_HEIGHT))

    @vertical_position.setter
    def vertical_position(self, pos: Position):
        offset = pos.y // SCREEN_HEIGHT
        self.position = Position(pos.x + offset * SCREEN_WIDTH, pos.y % SCREEN_HEIGHT)

    @property
    def real_size(self):
        """The actual size the generator should take up"""
        return self.base_size * self.bmp_size

    @property
    def bmp_size(self):
        """The base size of the generator in terms of its units"""
        return self.generator.bmp.size

    @property
    def base_size(self):
        """The width and height in terms of its bytes"""
        return self._base_size

    def change_size(self, size: Size) -> "BlockGeneratorBase":
        """
        Attempts to set the size to a different value
        :param size: The desired size
        :return: The object with the new size
        """
        difference = size - self.base_size
        return self.change_width(difference.width).change_height(difference.height)

    def get_simple_size(self, size_offset: int) -> int:
        """
        Gets the size of the small nibble with a given offset
        :param size_offset: The difference to be added
        :return: The small nibble of the new size
        """
        try:
            return get_simple_size(self.to_bytes()[1][2] & 0x0F + size_offset)
        except IndexError:
            return 0

    def get_complex_size(self, size_offset: int) -> int:
        """
        Gets the size of the small nibble with a given offset
        :param size_offset: The difference to be added
        :return: The small nibble of the new size
        """
        try:
            return get_complex_size(self.to_bytes()[1][3] + size_offset)
        except IndexError:
            return 0

    @abstractmethod
    def change_width(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded horizontally
        :return: A new block generator
        """

    @abstractmethod
    def change_height(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded vertically
        :return: A new block generator
        """

    def _set_index(self, index: int) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new index
        :param index: The index of the block
        :return: A new block generator
        """
        tileset, data = self.to_bytes
        data[2] = index
        return BlockGeneratorBase.generator_from_bytes(tileset=tileset, data=data)

    def get_properties(self) -> Tuple[int, int, int, int, int, int, int]:
        x, y = self.position.x, self.position.y
        width, height = self.base_size.width - 1, self.base_size.height - 1
        domain, index = return_domain_and_index_from_generator(self.generator_definition)
        tileset = get_tileset_from_index(self.generator_definition)
        return tileset, domain, index, width, height, x, y

    @abstractmethod
    def to_asm6(self) -> str:
        """
        Convert the block generator into compiler ready format.
        :return: A string for 6502, asm6, format.
        """

    @abstractmethod
    def to_bytes(self) -> Tuple[int, bytearray]:
        """
        Convert the block generator into the format it will be read in game.
        :return: A tuple providing the supposed tileset and bytes provided in game.
        """

    @classmethod
    @abstractmethod
    def from_bytes(cls, tileset: int, data: bytearray) -> "BlockGeneratorBase":
        """
        Convert data into in readable data
        :param tileset: The tileset for the generator
        :param data: The data in game
        :return: A block generator
        """

    @classmethod
    def generator_from_attributes(
            cls, definition_idx: int, position: Position, base_size: Size
    ) -> "BlockGeneratorBase":
        """
        Makes a new generator from specified attributes.  This is useful as it finds the correct generator to use.
        :param definition_idx: The index of the generator definition
        :param position: The position of the generator
        :param base_size: The size of the generator
        :return: The corresponding subclass of BlockGeneratorBase
        """
        definition = get_generator_from_index(definition_idx)
        generator = GENERATORS[NAMES[CONVERT[DEFINITIONS[definition.bmp.obj_generator]]]]
        return generator(generator_definition=definition_idx, position=position, base_size=base_size)

    @classmethod
    def generator_from_bytes(
            cls, tileset: int, data: bytearray
    ) -> "BlockGeneratorBase":
        """
        Makes a new generator from a specified tileset a bytes.
        This is useful as it finds the correct generator to use.
        :param tileset: The tileset that the generator resides inside
        :param data: The data for that makes up the generator
        :return: The corresponding subclass of BlockGeneratorBase
        """
        data.extend([0, 0, 0, 0, 0])
        generator_definition = get_generator_from_index(
            get_object_definition_index_from_data(tileset=tileset, data=data)
        )
        generator = GENERATORS[NAMES[CONVERT[DEFINITIONS[generator_definition.bmp.obj_generator]]]]
        return generator.from_bytes(tileset=tileset, data=data)


class SlopeGenerator(BlockGeneratorBase):
    def to_asm6(self) -> str:
        """
        Convert the block generator into compiler ready format.
        :return: A string for 6502, asm6, format.
        """
        tileset, domain, index, width, height, x, y = self.get_properties()
        s = f"\t.byte {to_hex(domain << 5)} | {to_hex(y)}, {to_hex(max(min(x, 0xFF), 0))}, " \
            f"{to_hex(index + width)} ; {self.generator.description}\n"
        return s

    def to_bytes(self) -> Tuple[int, bytearray]:
        """
        Convert the block generator into the format it will be read in game
        :return: A tuple providing the supposed tileset and bytes provided in game.
        """
        tileset, domain, index, width, height, x, y = self.get_properties()
        return tileset, bytearray([(domain << 5) + y, x, (index & 0xF0) + width])

    def change_width(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded horizontally
        :return: A new block generator
        """
        tileset, data = self.to_bytes()
        data[2] &= 0xF0 + self.get_simple_size(amount)
        return SlopeGenerator.from_bytes(tileset=tileset, data=data)

    def change_height(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded vertically
        :return: A new block generator
        """
        return self.change_width(amount)

    @classmethod
    def from_bytes(cls, tileset: int, data: bytearray) -> "SlopeGenerator":
        """
        Convert data into in readable data
        :param tileset: The tileset for the generator
        :param data: The data in game
        :return: A block generator
        """
        generator_index = get_object_definition_index_from_data(tileset=tileset, data=data)
        position = Position(data[1], data[0] & 0b0001_1111)
        size = Size(1 + (data[2] & 0x0F), 1 + (data[2] & 0x0F))
        return cls(generator_definition=generator_index, position=position, base_size=size)


class VerticalGenerator(BlockGeneratorBase):
    def to_asm6(self) -> str:
        """
        Convert the block generator into compiler ready format.
        :return: A string for 6502, asm6, format.
        """
        tileset, domain, index, width, height, x, y = self.get_properties()
        if self.generator.bytes == 3:
            return f"\t.byte {to_hex(domain << 5)} | {to_hex(y)}, {to_hex(x)}, " \
                f"{to_hex(index + height)} ; {self.generator.description}\n"
        elif self.generator.bytes == 4:
            return f"\t.byte {to_hex(domain << 5)} | {to_hex(y)}, {to_hex(x)}, " \
                f"{to_hex(index + width)}, {to_hex(height)} ; {self.generator.description}\n"
        else:
            raise NotImplementedError

    def to_bytes(self) -> Tuple[int, bytearray]:
        """
        Convert the block generator into the format it will be read in game
        :return: A tuple providing the supposed tileset and bytes provided in game.
        """
        tileset, domain, index, width, height, x, y = self.get_properties()

        if self.generator.bytes == 3:
            return tileset, bytearray([(domain << 5) + y, x, (index & 0xF0) + height])
        elif self.generator.bytes == 4:
            return tileset, bytearray([(domain << 5) + y, x, (index & 0xF0) + width, height])
        else:
            raise NotImplementedError

    def change_width(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded horizontally
        :return: A new block generator
        """
        if self.generator.bytes == 3:
            return self
        elif self.generator.bytes == 4:
            tileset, data = self.to_bytes()
            data[2] &= 0xF0 + self.get_simple_size(size_offset=amount)
            return SlopeGenerator.from_bytes(tileset=tileset, data=data)
        else:
            return NotImplemented

    def change_height(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded vertically
        :return: A new block generator
        """
        if self.generator.bytes == 3:
            tileset, data = self.to_bytes()
            data[2] &= 0xF0 + self.get_simple_size(size_offset=amount)
            return SlopeGenerator.from_bytes(tileset=tileset, data=data)
        elif self.generator.bytes == 4:
            tileset, data = self.to_bytes()
            data[3] = self.get_complex_size(size_offset=amount)
            return SlopeGenerator.from_bytes(tileset=tileset, data=data)
        else:
            raise NotImplementedError

    @classmethod
    def from_bytes(cls, tileset: int, data: bytearray) -> "VerticalGenerator":
        """
        Convert data into in readable data
        :param tileset: The tileset for the generator
        :param data: The data in game
        :return: A block generator
        """
        generator_index = get_object_definition_index_from_data(tileset=tileset, data=data)
        position = Position(data[1], data[0] & 0b0001_1111)
        gen = get_generator_from_index(generator_index)
        if gen.bytes == 3:
            size = Size(1, 1 + (data[2] & 0x0F))
        elif gen.bytes == 4:
            size = Size(1 + (data[2] & 0x0F), 1 + data[3])
        else:
            return NotImplemented
        return cls(generator_definition=generator_index, position=position, base_size=size)


class HorizontalGenerator(BlockGeneratorBase):
    def to_asm6(self) -> str:
        """
        Convert the block generator into compiler ready format.
        :return: A string for 6502, asm6, format.
        """
        tileset, domain, index, width, height, x, y = self.get_properties()
        if self.generator.bytes == 3:
            return f"\t.byte {to_hex(domain << 5)} | {to_hex(y)}, {to_hex(x)}, " \
                f"{to_hex(index + width)} ; {self.generator.description}\n"
        elif self.generator.bytes == 4:
            return f"\t.byte {to_hex(domain << 5)} | {to_hex(y)}, {to_hex(x)}, " \
                f"{to_hex(index + height)}, {to_hex(width)} ; {self.generator.description}\n"
        else:
            raise NotImplementedError

    def to_bytes(self) -> Tuple[int, bytearray]:
        """
        Convert the block generator into the format it will be read in game
        :return: A tuple providing the supposed tileset and bytes provided in game.
        """
        tileset, domain, index, width, height, x, y = self.get_properties()
        gen = get_generator_from_index(self.generator_definition)
        if gen.bytes == 3:
            return tileset, bytearray([(domain << 5) + y, x, (index & 0xF0) + width])
        elif gen.bytes == 4:
            return tileset, bytearray([(domain << 5) + y, x, (index & 0xF0) + height, width])
        else:
            raise NotImplementedError

    def change_width(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded horizontally
        :return: A new block generator
        """
        if self.generator.bytes == 3:
            tileset, data = self.to_bytes()
            data[2] &= 0xF0 + self.get_simple_size(size_offset=amount)
            return SlopeGenerator.from_bytes(tileset=tileset, data=data)
        elif self.generator.bytes == 4:
            tileset, data = self.to_bytes()
            data[3] = self.get_complex_size(size_offset=amount)
            return SlopeGenerator.from_bytes(tileset=tileset, data=data)
        else:
            raise NotImplementedError

    def change_height(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded vertically
        :return: A new block generator
        """
        if self.generator.bytes == 3:
            tileset, data = self.to_bytes()
            data[2] &= 0xF0 + self.get_simple_size(size_offset=amount)
            return SlopeGenerator.from_bytes(tileset=tileset, data=data)
        elif self.generator.bytes == 4:
            tileset, data = self.to_bytes()
            data[3] = self.get_complex_size(size_offset=amount)
            return SlopeGenerator.from_bytes(tileset=tileset, data=data)
        else:
            raise NotImplementedError

    @classmethod
    def from_bytes(cls, tileset: int, data: bytearray) -> "HorizontalGenerator":
        """
        Convert data into in readable data
        :param tileset: The tileset for the generator
        :param data: The data in game
        :return: A block generator
        """
        generator_index = get_object_definition_index_from_data(tileset=tileset, data=data)
        position = Position(data[1], data[0] & 0b0001_1111)
        gen = get_generator_from_index(generator_index)
        if gen.bytes == 3:
            size = Size(1 + (data[2] & 0x0F), 1)
        elif gen.bytes == 4:
            size = Size(1 + data[3], 1 + (data[2] & 0x0F))
        else:
            raise NotImplementedError
        return cls(generator_definition=generator_index, position=position, base_size=size)


class SimpleGenerator(BlockGeneratorBase):
    def to_asm6(self) -> str:
        """
        Convert the block generator into compiler ready format.
        :return: A string for 6502, asm6, format.
        """
        tileset, domain, index, width, height, x, y = self.get_properties()
        return f"\t.byte {to_hex(domain << 5)} | {to_hex(y)}, {to_hex(x)}, " \
            f"{to_hex(index)} ; {self.generator.description}\n"

    def to_bytes(self) -> Tuple[int, bytearray]:
        """
        Convert the block generator into the format it will be read in game
        :return: A tuple providing the supposed tileset and bytes provided in game.
        """
        tileset, domain, index, width, height, x, y = self.get_properties()
        return tileset, bytearray([(domain << 5) + y, x, index])

    def change_width(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded horizontally
        :return: A new block generator
        """
        return self

    def change_height(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded vertically
        :return: A new block generator
        """
        return self

    @classmethod
    def from_bytes(cls, tileset: int, data: bytearray) -> "SimpleGenerator":
        """
        Convert data into in readable data
        :param tileset: The tileset for the generator
        :param data: The data in game
        :return: A block generator
        """
        generator_index = get_object_definition_index_from_data(tileset=tileset, data=data)
        position = Position(data[1], data[0] & 0b0001_1111)
        size = Size(1, 1)
        return cls(generator_definition=generator_index, position=position, base_size=size)


class CrashGenerator(BlockGeneratorBase):
    def to_asm6(self) -> str:
        """
        Convert the block generator into compiler ready format.
        :return: A string for 6502, asm6, format.
        """
        return ""

    """Effectively removes the object from existing"""
    def to_bytes(self) -> Tuple[int, bytearray]:
        """
        Convert the block generator into the format it will be read in game
        :return: A tuple providing the supposed tileset and bytes provided in game.
        """
        tileset = get_tileset_from_index(self.generator_definition)
        return tileset, bytearray()

    def change_width(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded horizontally
        :return: A new block generator
        """
        return self

    def change_height(self, amount: int = 1) -> "BlockGeneratorBase":
        """
        Provides a new block generator with the new size
        :param amount: The amount to be expanded vertically
        :return: A new block generator
        """
        return self

    @classmethod
    def from_bytes(cls, tileset: int, data: bytearray) -> "CrashGenerator":
        """
        Convert data into in readable data
        :param tileset: The tileset for the generator
        :param data: The data in game
        :return: A block generator
        """
        generator_index = get_object_definition_index_from_data(tileset=tileset, data=data)
        position = Position(data[1], data[0] & 0b0001_1111)
        size = Size(1, 1)
        return cls(generator_definition=generator_index, position=position, base_size=size)


GENERATORS = {
    0: SimpleGenerator,
    1: HorizontalGenerator,
    2: VerticalGenerator,
    3: SlopeGenerator
}
