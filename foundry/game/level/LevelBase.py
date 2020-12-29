from typing import List, Dict
from foundry.game.File import ROM
from smb3parse.levels.level_header import LevelHeader
from foundry.game.gfx.objects.LevelGeneratorBase import BlockGeneratorHandler
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.level.LevelConstants import LEGACY_HEADER_LENGTH


def read_generator_data(start: int, tileset: int):
    """Reads level data from a location and continues until a detonator is found"""


class LevelBase:
    """Provides the fundamental structure for level data"""
    def __init__(self, header: LevelHeader,
                 generators: List[BlockGeneratorHandler] = None, objects: List[EnemyObject] = None):
        self._header = header
        self._generators = generators if generators is not None else []
        self._objects = objects if objects is not None else []

    @classmethod
    def from_bytes_legacy(cls, generators_pointer: int, objects_pointer: int, tileset: int):
        """Converts data into level structure"""
        header_data = ROM().bulk_read(LEGACY_HEADER_LENGTH, generators_pointer)
        header, generators_pointer = LevelHeader.legacy_from_bytes(header_data), generators_pointer + 9

    @property
    def header(self) -> LevelHeader:
        return self._header

    @header.setter
    def header(self, header: LevelHeader):
        self._header = header

    @property
    def generators(self) -> List[BlockGeneratorHandler]:
        return self._generators

    @generators.setter
    def generators(self, generators: List[BlockGeneratorHandler]):
        self._generators = generators

    @property
    def objects(self):
        return self._objects

    @objects.setter
    def objects(self, objects: List[EnemyObject]):
        self._objects = objects

    def __repr__(self):
        return f"LevelBase(header={self.header}, generators={self.generators}, objects={self.objects})"

