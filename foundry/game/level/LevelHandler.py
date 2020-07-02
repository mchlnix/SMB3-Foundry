from dataclasses import dataclass
from typing import List, Dict

import yaml
from yaml import CLoader as Loader

from foundry.game.File import ROM, BankHandler, get_bank_offset, to_word
from foundry.game.level.Level import Level
from smb3parse.asm6_converter import to_hex
from foundry import data_dir
from foundry.game.Range import Range


with open(data_dir.joinpath("level_data.yaml")) as f:
    level_data = yaml.load(f, Loader=Loader)
LEVEL_BANK_OFFSET = level_data["level_bank_offset"]


@dataclass
class SimpleLevel:
    generators_idx: int
    objects_idx: int
    tileset: int
    bank: int
    idx: int = None


def find_level_data_regions(levels: List[SimpleLevel]) -> {int: Range}:
    """
    Finds the general size of each level for simplicity
    :param levels: The levels to be sorted through
    :return: A list of ranges
    """
    level_starts = [(level.generators_idx, level.idx) for level in levels]
    level_starts.sort(key=lambda tup: tup[0])
    level_ranges = {}
    for idx, level in enumerate(level_starts):
        start, end = (level[0] - 0x10) % 0x2000, (level_starts[idx + 1][0] - 0x10) % 0x2000
        length = end - start
        if length < 0 or length >= 200:  # enforce banking or double check for big levels
            length = get_level_bytes_len(levels[level[1]])
        level_ranges.update({level[1]: Range(level[0], level[0] + length)})
    return level_ranges


def get_level_bytes_len(level: SimpleLevel) -> int:
    data = Level("", level.generators_idx, level.objects_idx, level.tileset, qt=False).to_bytes_joined()
    return len(data)


def level_data_offset(name: str):
    """Gets the correct level data for a given key"""
    return to_hex(get_bank_offset(level_data[name]["bank"])) + to_hex(level_data[name]["offset"])


def save_levels(lvl_data: List[bytearray], gen_pointers: List[int]):
    """Saves the levels"""
    bank_handler = BankHandler(16)
    banks, generator_pointers, objects_pointers = [], [], []
    for idx, level in enumerate(lvl_data):
        bank, offset = bank_handler.add_data(list(level))
        bank += LEVEL_BANK_OFFSET
        banks.append(bank)
        generator_pointers.append(get_bank_offset(bank) + offset)
        objects_pointers.append(get_bank_offset(bank) + offset + gen_pointers[idx])
    bank_handler.save_to_rom(LEVEL_BANK_OFFSET)
    ROM().bulk_write(bytearray(banks), level_data_offset("banks"))
    ROM().bulk_write(bytearray(generator_pointers), level_data_offset("generators"))
    ROM().bulk_write(bytearray(objects_pointers), level_data_offset("objects"))


class LevelHandler:
    """Handles loading levels so we can easily intertwine them"""
    def __init__(self, levels: List[SimpleLevel]):
        self.levels = levels

    def save_level(self, idx: int, level: Level):
        """Saves a level and moves levels to make space"""
        level_ranges = find_level_data_regions(self.levels)
        lvl_data = [ROM().bulk_read(lvl_range.size, lvl_range.start) for _, lvl_range in level_ranges.items()]
        gen_pointers = [self.levels[key].objects_idx - self.levels[key].generators_idx for key in level_ranges]
        gens, objs = level.to_bytes()
        lvl_data[idx] = bytearray(gens + objs)
        gen_pointers[idx] = level_ranges[idx].start + len(gens)
        save_levels(lvl_data, gen_pointers)


    @classmethod
    def form_lists(cls, gen_pointers: List[int], obj_pointers: List[int], tilesets: List[int], banks: List[int]):
        """Makes a level handler from preexisting level information"""
        return cls([SimpleLevel(*level, i) for i, level in enumerate(zip(gen_pointers, obj_pointers, tilesets, banks))])

    @classmethod
    def from_rom(cls):
        """Makes a level handler from the rom and specified locations from level_data.yaml"""
        bank_offset = level_data_offset("banks")
        gen_offset = level_data_offset("generators")
        obj_offset = level_data_offset("objects")
        tileset_offset = level_data_offset("tilesets")
        if None in [bank_offset, gen_offset, obj_offset, tileset_offset]:
            print(f"None is not a valid address in ROM in:"
                  f"\nbank_offset - {bank_offset if bank_offset is None else hex(bank_offset)}"
                  f"\ngen_offset - {gen_offset if gen_offset is None else hex(gen_offset)}"
                  f"\nobj_offset - {obj_offset if obj_offset is None else hex(obj_offset)}"
                  f"\ntileset_offset - {tileset_offset if tileset_offset is None else hex(tileset_offset)}")
            raise ValueError

        banks = [ROM.get_byte(bank_offset + idx) for idx in range(0x200)]
        generator_pointers = [
            to_word(ROM.get_byte(gen_offset + idx), ROM.get_byte(gen_offset + idx + 0x200)) for idx in range(0x200)
        ]
        objects_pointers = [
            to_word(ROM.get_byte(obj_offset + idx), ROM.get_byte(obj_offset + idx + 0x200)) for idx in range(0x200)
        ]
        tilesets = [ROM.get_byte(tileset_offset + idx) for idx in range(0x200)]
        return cls.form_lists(
            gen_pointers=generator_pointers, obj_pointers=objects_pointers, tilesets=tilesets, banks=banks
        )
