from smb3parse.asm6_converter import to_int, to_label, to_hex
from foundry.game.level.Level import Level
import yaml
from yaml import CLoader as Loader
from foundry.game.File import ROM
from foundry import data_dir
import os
from dataclasses import dataclass
from PySide2.QtWidgets import QApplication

from smb3parse.util.rom import Rom

with open(data_dir.joinpath("world_locations.yaml")) as f:
    worlds = yaml.load(f, Loader=Loader)

with open(data_dir.joinpath("tileset_info.yaml")) as f:
    tilesets = yaml.load(f, Loader=Loader)

with open(data_dir.joinpath("levels.dat"), "r") as level_data:
    level_names = {}
    for line_no, line in enumerate(level_data.readlines()):
        data = line.rstrip("\n").split(",")

        numbers = [int(_hex, 16) for _hex in data[0:5]]
        level_name = data[5]

        game_world, level_in_world, rom_level_offset, enemy_offset, real_obj_set = numbers
        level_name = f"{level_name}_W{game_world}"
        rom_level_offset -= 9
        level_names.update({(rom_level_offset, enemy_offset, real_obj_set): level_name})

ROM.load_from_file(data_dir.joinpath("smb3.nes"))


def load_world_info(world):
    count = to_int(worlds[world]["columns"]) - to_int(worlds[world]["rows"])
    objects = to_int(worlds[world]["object_sets"]) + to_int(worlds[world]["offset"])
    layouts = to_int(worlds[world]["level_layouts"]) + to_int(worlds[world]["offset"])
    obj_sets = to_int(worlds[world]["rows"]) + to_int(worlds[world]["offset"])
    rows = to_int(worlds[world]["rows"]) + to_int(worlds[world]["offset"])
    coloums = to_int(worlds[world]["columns"]) + to_int(worlds[world]["offset"])
    return count, objects, layouts, obj_sets, rows, coloums


world_layouts = {}
levels = {}
level_main = []
level_alt = []
custom_layouts = {}


def load_levels():
    for i, world in enumerate(worlds):
        if world == 8 or world == "custom":
            continue
        levelz, objects, layouts, obj_sets, rows, coloums = load_world_info(world)
        world_layout = {}
        for level in range(levelz):
            obj_set = ROM().get_byte(obj_sets) & 0x0F
            obj_sets += 1

            row = ROM().get_byte(rows) >> 4
            rows += 1

            coloum = ROM().get_byte(coloums)
            coloums += 1

            objects_address = ROM().get_word(objects) + 0x11
            objects += 2

            bank = tilesets[obj_set]["C000"]
            level_address = (ROM().get_word(layouts) % 0x2000) + (0x2000 * bank) + 0x10
            layouts += 2

            if obj_set == 7:
                print(hex(objects_address), hex(level_address))
                world_layout.update({(row, coloum): level_main.index(objects_address >> 8)})
                continue
            if obj_set > 14:
                world_layout.update({(row, coloum): n_spade})  # Not n spade
                continue
            if (obj_set, objects_address, level_address) in levels:
                world_layouts.update({(row, coloum): add_level(obj_set, level_address, objects_address)})
                continue

            level_idx = add_level(obj_set, level_address, objects_address)
            world_layout.update({(row, coloum): level_idx})
        world_layouts.update({i: world_layout})


def load_custom_levels():
    custom_level_types = worlds["custom"]
    for type, levels in custom_level_types.items():
        layouts = []
        for idx, key in enumerate(levels):
            if key == "items":
                continue
            level = levels[key]
            name, gens, objs, obj_set = level["name"], to_int(level["generators"]), to_int(level["objects"]) + 0xD011, \
                to_int(level["object_set"])
            bank = tilesets[obj_set]["C000"]

            gens = gens + (0x2000 * bank) + 0x10
            if 0x2F000 > gens > 0x2E000:
                if key == 2 or key == 3 or key == 5 or key == 6 or key == 7 or type == "coin_ship":
                    gens += 0x1000
            if 0x25000 > gens > 0x24000:
                if key == 1 or key == 2:
                    gens += 0x1000
                objs -= 0x1000
            if 0x1B000 > gens > 0x1A000:
                gens += 0x1000
                objs -= 0x1000
            if 0x1F000 > gens > 0x1E000:
                gens += 0x1000
                objs -= 0x1000

            level_info = (obj_set, gens, objs)
            layouts.append(add_level(*level_info, force=True))

            if obj_set == 15:
                global n_spade
                n_spade = add_level(*level_info, force=True)

            if obj_set == 7 and key == 0:
                global toad_house
                for _ in range(0xF):
                    toad_house = add_level(*level_info, force=True)

        custom_layouts.update({type: layouts})


def load_remaining_levels():
    """Generates a default level for the remaining levels not filled"""
    default_level = (1, 0x2A850 - 9, 0xD2C0 + 3)
    while True:
        if 0 == add_level(*default_level, alt=False, force=True):
            break
    while True:
        if 0 == add_level(*default_level, alt=True, force=True):
            break


default_level_idx = -1


def get_level_name(level):
    global default_level_idx
    default_level_idx += 1
    try:
        return to_label(level_names[level])
    except KeyError:
        return to_label(f"Default_Level_{default_level_idx}")


def add_level(obj_set, generator_address, object_address, alt=False, force=False):
    if force or ((generator_address, object_address, obj_set) not in levels
                 and generator_address != 0x10010
                 and 0xC000 < object_address < 0xE000
                 and obj_set != 0):
        if alt:
            if len(level_alt) >= 0x100:
                return 0
            index = len(level_alt) + 0x100
        else:
            if len(level_main) >= 0x100:
                return 0
            index = len(level_main)
        level_info = (generator_address, object_address, obj_set)
        level_name = get_level_name(level_info)
        if force:
            level_name = f"{level_name}_{index}"
        level = Level(level_name, *level_info, qt=False)
        levels.update({index if force else level_info: level})
        if alt:
            level_alt.append(index if force else level_info)
        else:
            level_main.append(index if force else level_info)
        header = level.header
        alt_level_info = (header.jump_object_set_number, header.jump_level_address, header.jump_enemy_address + 1)
        alt_level_idx = max(add_level(*alt_level_info, True), 0)
        level.next_level = alt_level_idx
        print(hex(index), [hex(i) for i in level_info], level_name)
        return index
    try:
        level_info = (generator_address, object_address, obj_set)
        try:
            return level_main.index(level_info)
        except ValueError:
            return level_alt.index(level_info) + 0x100
    except ValueError:
        return toad_house


n_spade = 0
toad_house = 0
load_custom_levels()
load_levels()
load_remaining_levels()


print(f"Loaded {len(levels)} levels")


class BankHandler:
    def __init__(self, banks):
        self.amount_of_banks = banks
        self.banks = [Bank() for _ in range(banks)]

    def add_level(self, level: Level):
        for bank in self.banks:
            if bank.add_level(level):
                break

    def get_label_bank(self, label: str):
        for idx, bank in enumerate(self.banks):
            if label in bank.labels:
                return idx
        return False


class Bank:
    def __init__(self, len: int=0):
        self.length = len
        self.labels = {}
        self.s = ""

    def add_level(self, level: Level):
        bytes = level.to_bytes()
        generators, objects = len(bytes[0][1]), len(bytes[1][1])
        if self.length + generators + objects < 0x2000:
            self.labels.update({f"{level.name}_generators": self.length})
            self.length += generators
            self.labels.update({f"{level.name}_objects": self.length})
            self.length += objects
            self.s = f"{self.s}\n{level.to_asm6()}"
            return True
        return False


def get_level_indexing(levelz: "[Level]", banks: BankHandler):
    level_label_hi = "level_label_hi:\n"
    level_label_lo = "level_label_lo:\n"
    level_obj_hi = "level_obj_hi:\n"
    level_obj_lo = "level_obj_lo:\n"
    level_bank = "level_bank:\n"
    level_object_set = "level_object_set:\n"
    for level_info in levelz:
        level = levels[level_info]
        level_label_hi = f"{level_label_hi}\t.byte >{level.name}_generators\n"
        level_label_lo = f"{level_label_lo}\t.byte <{level.name}_generators\n"
        level_obj_hi = f"{level_obj_hi}\t.byte >{level.name}_objects\n"
        level_obj_lo = f"{level_obj_lo}\t.byte <{level.name}_objects\n"
        bank = banks.get_label_bank(f"{level.name}_generators")
        level_bank = f"{level_bank}\t.byte {bank}\n"
        level_object_set = f"{level_object_set}\t.byte {level.object_set_number}\n"
    return level_label_hi, level_label_lo, level_obj_hi, level_obj_lo, level_bank, level_object_set


DIRECTORY = "level_data"


def save_custom_levels():
    if not os.path.isdir(DIRECTORY):
        os.mkdir(DIRECTORY)
    if not os.path.isdir(f"{DIRECTORY}/custom"):
        os.mkdir(f"{DIRECTORY}/custom")
    for idx, key in enumerate(custom_layouts):
        layouts = custom_layouts[key]
        world_levels = f"{key}_levels:\n"
        for level in layouts:
            world_levels = f"{world_levels}\t.byte {level}\n"
        world_dir = f"{DIRECTORY}/custom"
        with open(f"{world_dir}/{key}_levels.asm", "w+") as f:
            f.write(world_levels)


def save_worlds():
    if not os.path.isdir(DIRECTORY):
        os.mkdir(DIRECTORY)
    if not os.path.isdir(f"{DIRECTORY}/worlds"):
        os.mkdir(f"{DIRECTORY}/worlds")
    worlds_rows_hi = f"world_rows_hi:\n"
    worlds_coloums_hi = f"world_coloums_hi:\n"
    worlds_levels_hi = f"world_levels_hi:\n"
    worlds_rows_lo = f"world_rows_lo:\n"
    worlds_coloums_lo = f"world_coloums_lo:\n"
    worlds_levels_lo = f"world_levels_lo:\n"
    world_layouts.update({"world_9": {}})
    for idx, key in enumerate(world_layouts):
        worlds_rows_hi = f"{worlds_rows_hi}\t.byte >world_rows_{idx}\n"
        worlds_coloums_hi = f"{worlds_coloums_hi}\t.byte >world_coloums_{idx}\n"
        worlds_levels_hi = f"{worlds_levels_hi}\t.byte >world_levels_{idx}\n"
        worlds_rows_lo = f"{worlds_rows_lo}\t.byte <world_rows_{idx}\n"
        worlds_coloums_lo = f"{worlds_coloums_lo}\t.byte <world_coloums_{idx}\n"
        worlds_levels_lo = f"{worlds_levels_lo}\t.byte <world_levels_{idx}\n"
        world = world_layouts[key]
        world_rows = f"world_rows_{idx}:\n"
        world_coloums = f"world_coloums_{idx}:\n"
        world_levels = f"world_levels_{idx}:\n"
        for key, level in world.items():
            world_rows = f"{world_rows}\t.byte {key[0]}\n"
            world_coloums = f"{world_coloums}\t.byte {key[1]}\n"
            world_levels = f"{world_levels}\t.byte {level}\n"
        world_levels = f"{world_levels}world_levels_{idx}_end:\n"
        world_dir = f"{DIRECTORY}/worlds/world_{idx}"
        if not os.path.isdir(world_dir):
            os.mkdir(world_dir)
        with open(f"{DIRECTORY}/worlds/rows_hi.asm", "w+") as f:
            f.write(worlds_rows_hi)
        with open(f"{DIRECTORY}/worlds/coloums_hi.asm", "w+") as f:
            f.write(worlds_coloums_hi)
        with open(f"{DIRECTORY}/worlds/levels_hi.asm", "w+") as f:
            f.write(worlds_levels_hi)
        with open(f"{DIRECTORY}/worlds/rows_lo.asm", "w+") as f:
            f.write(worlds_rows_lo)
        with open(f"{DIRECTORY}/worlds/coloums_lo.asm", "w+") as f:
            f.write(worlds_coloums_lo)
        with open(f"{DIRECTORY}/worlds/levels_lo.asm", "w+") as f:
            f.write(worlds_levels_lo)
        with open(f"{world_dir}/rows.asm", "w+") as f:
            f.write(world_rows)
        with open(f"{world_dir}/coloums.asm", "w+") as f:
            f.write(world_coloums)
        with open(f"{world_dir}/levels.asm", "w+") as f:
            f.write(world_levels)


def save_levels():
    if not os.path.isdir(DIRECTORY):
        os.mkdir(DIRECTORY)
    banks = BankHandler(16)
    levelz = level_main
    levelz.extend(level_alt)
    for level_info in levelz:
        level = levels[level_info]
        banks.add_level(level)
    level_label_hi, level_label_lo, level_obj_hi, level_obj_lo, level_bank, level_os = get_level_indexing(levelz, banks)
    with open(f"{DIRECTORY}/level_label_hi.asm", "w+") as f:
        f.write(level_label_hi)
    with open(f"{DIRECTORY}/level_label_lo.asm", "w+") as f:
        f.write(level_label_lo)
    with open(f"{DIRECTORY}/level_obj_hi.asm", "w+") as f:
        f.write(level_obj_hi)
    with open(f"{DIRECTORY}/level_obj_lo.asm", "w+") as f:
        f.write(level_obj_lo)
    with open(f"{DIRECTORY}/level_bank.asm", "w+") as f:
        f.write(level_bank)
    with open(f"{DIRECTORY}/level_object_set.asm", "w+") as f:
        f.write(level_os)
    for idx, bank in enumerate(banks.banks):
        with open(f"{DIRECTORY}/bank_{hex(idx)}.asm", "w+") as f:
            f.write(f"; Bank {idx}\n{bank.s}")


save_levels()
save_worlds()
save_custom_levels()