"""Load sprite data into a readable format"""
import yaml
import pickle
from yaml import CLoader as Loader
from typing import Tuple, List

from foundry import data_dir
from foundry.core.geometry.Size.Size import Size
from smb3parse.asm6_converter import convert_str_to_int_white_space as to_int
from foundry.game.gfx.objects.objects.LevelObjectDefinition import LevelObjectDefinition, Animation, Hitbox, \
    SpriteGraphic, ObjectOperation


def load_sprite_routines(directory: str) -> Tuple[List[str], List[str], List[str]]:
    """Provide the sprite routines"""
    with open(f"{directory}/sprite_init.yaml") as file:
        init = yaml.load(file, Loader=Loader)
    with open(f"{directory}/sprite_update.yaml") as file:
        updates = yaml.load(file, Loader=Loader)
    with open(f"{directory}/sprite_hit.yaml") as file:
        hits = yaml.load(file, Loader=Loader)
    return init.values(), updates.values(), hits.values()


def load_sprite_bmp(directory: str) -> Tuple[List[int], List[Size]]:
    """Provides the palette and size of the sprite"""
    with open(f"{directory}/sprite_attr_1.yaml") as file:
        attrs = yaml.load(file, Loader=Loader)
    palettes, heights, widths = list(zip(*([[to_int(s) for s in line.split('|')] for line in attrs.values()])))
    return palettes, [Size(width, height) for width, height in zip(widths, heights)]


def get_sprite_attributes_2(attr) -> Tuple[int, bool, bool]:
    """Provides the sprite attributes 2"""
    hitbox = attr & 0xF0 >> 4
    ignores_stomping = True if attr & 0b100 else False
    shelled = True if attr & 0b1 else False
    return hitbox, ignores_stomping, shelled


def get_sprite_attributes_3(attr) -> Tuple[int, bool, bool, bool, bool]:
    """Provides the sprite attributes 3"""
    pause_action = attr & 0x0F
    can_squash = True if attr & 0x10 else False
    stomp_hurts = True if attr & 0x20 else False
    can_bump_into_shell = True if attr & 0x40 else False
    tail_immune = True if attr & 0x80 else False
    return pause_action, can_squash, stomp_hurts, can_bump_into_shell, tail_immune


def load_sprite_attributes(directory: str) -> Tuple:
    """Provides the sprite's attributes"""
    with open(f"{directory}/sprite_attr_2.yaml") as file:
        attrs = list(map(to_int, yaml.load(file, Loader=Loader).values()))
    hitboxes, ignore_stomping, shelled = list(zip(*([get_sprite_attributes_2(a) for a in attrs])))
    with open(f"{directory}/sprite_attr_3.yaml") as file:
        attrs = list(map(to_int, yaml.load(file, Loader=Loader).values()))
    pause_act, can_squash, stomp_hurts, bump_into_shell, tail_immune = \
        list(zip(*([get_sprite_attributes_3(a) for a in attrs])))
    return hitboxes, ignore_stomping, shelled, pause_act, can_squash, stomp_hurts, bump_into_shell, tail_immune


def get_sprite_main_attributes(attr) -> Tuple[int, bool, bool, bool, bool]:
    """Provides the sprite attributes 3"""
    bounding_box = attr & 0x0F
    bounce_off_others = True if attr & 0x10 else False
    weapon_immunity = True if attr & 0x20 else False
    fire_immunity = True if attr & 0x40 else False
    killed_by_items = False if attr & 0x80 else True
    return bounding_box, bounce_off_others, weapon_immunity, fire_immunity, killed_by_items


def load_sprite_main_attributes(directory: str) -> Tuple:
    """Provides the sprite's main attributes"""
    with open(f"{directory}/sprite_attr_0.yaml") as file:
        attrs = list(map(to_int, yaml.load(file, Loader=Loader).values()))
    bound_box, bounce_off, weapon_immun, fire_immun, killed_by_items = list(
        zip(*([get_sprite_main_attributes(a) for a in attrs]))
    )
    return bound_box, bounce_off, weapon_immun, fire_immun, killed_by_items


def load_sprite_kill_action(directory: str) -> Tuple[int]:
    """Provide the sprite kill attribute"""
    with open(f"{directory}/sprite_kill_act.yaml") as file:
        return tuple(map(to_int, yaml.load(file, Loader=Loader).values()))


def load_sprite_page(directory: str) -> Tuple[int]:
    """Provide the page the graphics are on"""
    with open(f"{directory}/sprite_page.yaml") as file:
        return tuple(map(to_int, yaml.load(file, Loader=Loader).values()))


def load_sprite_graphics(directory: str) -> List[List[SpriteGraphic]]:
    """Provide the graphics for the sprite"""
    with open(f"{directory}/sprite_gfx.yaml") as file:
        gfx = list(yaml.load(file, Loader=Loader).values())
    for idx, l in enumerate(gfx):
        for i, graphic in enumerate(l):
            gfx[idx][i] = SpriteGraphic(graphic)
    return gfx


def load_objects(directory) -> List[LevelObjectDefinition]:
    """
    A function to load the level object definitions from yaml files
    This function mainly servers as a backup helper function and should be treated as such
    """
    gfxes = load_sprite_graphics(directory)
    pages = load_sprite_page(directory)
    kill_actions = load_sprite_kill_action(directory)
    bound_boxs, bounce_offs, weapon_immuns, fire_immuns, killed_by_items = load_sprite_main_attributes(directory)
    hitboxes, ignore_stompings, shelleds, pause_acts, can_squashs, stomp_hurts, bump_into_shells, \
    tail_immunes = load_sprite_attributes(directory)
    palettes, sizes = load_sprite_bmp(directory)
    inits, updates, hits = load_sprite_routines(directory)

    operations = []
    for (init, update, hit, pause_action, kill_action, ignore_stomping, shelled, can_squash, stomp_hurt,
         can_bump_into_shell, tail_immune, object_collision, weapon_immunity, fire_immunity, custom_collision) \
        in zip(
            inits, updates, hits, pause_acts, kill_actions, ignore_stompings, shelleds, can_squashs, stomp_hurts,
            killed_by_items, tail_immunes, bounce_offs, weapon_immuns, fire_immuns, bump_into_shells
    ):
        operation = ObjectOperation(
            init, update, hit, pause_action, kill_action, ignore_stomping, shelled, can_squash,
            stomp_hurt, can_bump_into_shell, tail_immune, object_collision, weapon_immunity,
            fire_immunity, custom_collision)
        operations.append(operation)

    hitboxes = [Hitbox(bound_box, hitbox) for (bound_box, hitbox) in zip(bound_boxs, hitboxes)]
    animations = [
        Animation(page, size, palette, graphics) for (page, size, palette, graphics)
        in zip(pages, sizes, palettes, gfxes)
    ]

    return [
        LevelObjectDefinition(operation, animation, hitbox) for (operation, animation, hitbox) in
        zip(operations, hitboxes, animations)
    ]


level_obs = load_objects(data_dir.joinpath("sprite_loader/"))
with open(data_dir.joinpath("sprite_loader/objects.pickle"), "wb+") as f:
    pickle.dump(level_obs, f, pickle.HIGHEST_PROTOCOL)

