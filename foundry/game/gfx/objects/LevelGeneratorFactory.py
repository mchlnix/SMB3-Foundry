"""A factory for level generators"""

from typing import List
from foundry.game.gfx.objects.LevelGeneratorBase import BlockGeneratorHandler, BlockGeneratorBase


class BlockGeneratorHandlerFactory:
    """A factory for making block generators"""
    _tileset: int

    def __init__(self, tileset: int):
        self.tileset = tileset

    @property
    def tileset(self) -> int:
        """The tileset for the factory"""
        return self._tileset

    @tileset.setter
    def tileset(self, tileset: int) -> None:
        self._tileset = tileset
        self.base_factory = BlockGeneratorBaseFactory(self.tileset)

    def generator_from_data(self, data: bytearray) -> BlockGeneratorHandler:
        """Makes a block generator handler from bytes"""
        return BlockGeneratorHandler(self.base_factory.generator_from_data(data))

    def generators_from_data(self, data: bytearray) -> List[BlockGeneratorHandler]:
        """Makes block generator handlers from bytes"""
        return [BlockGeneratorHandler(base_gen) for base_gen in self.base_factory.generators_from_data(data)]


class BlockGeneratorBaseFactory:
    """A factory for making block generators"""
    tileset: int

    def __init__(self, tileset: int):
        self.tileset = tileset

    def generator_from_data(self, data: bytearray) -> BlockGeneratorBase:
        """Makes a block generator base from bytes"""
        return BlockGeneratorBase.from_bytes(tileset=self.tileset, data=data)

    def generators_from_data(self, data: bytearray) -> List[BlockGeneratorBase]:
        """Makes block generators bases from bytes"""
        block_gens = []
        while True:
            if data[0] == 0xFF:
                return block_gens
            block_gens.append(self.generator_from_data(data))
            length = len(block_gens[-1].to_bytes())
            try:
                data = data[length:]
            except IndexError:
                return block_gens
