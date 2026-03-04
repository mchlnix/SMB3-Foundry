from operator import itemgetter
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint
from PySide6.QtGui import QUndoCommand

from foundry.game.File import ROM
from foundry.game.gfx import change_color
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.Palette import PaletteGroup, load_palette_group
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.asm import load_asm_enemy
from smb3parse.constants import PIPE_PAIR_COUNT
from smb3parse.data_points import Position
from smb3parse.data_points.pipe_data import PipeData
from smb3parse.objects.object_set import OBJECT_SET_NAMES

if TYPE_CHECKING:
    from foundry.gui.visualization.level.LevelView import LevelView

# The idea here is that we give the UndoCommands a reference to the level and any primitive data it needs. If it needs
# to change a LevelObject or EnemyItem, then it needs to reference those via an index into the respective lists inside
# the given Level object.
# This is because we want to support reloading a Level from the ROM while preserving the current UndoStack. But since
# this invalidates all references in the UndoCommands, it's easier to simply swap out the underlying Level reference,
# instead of the object references as well.
# In addition, we do not fix the "old value" of whatever we want to change with the UndoCommand on creation of said
# UndoCommand, but when we call redo(). This is, because whenever we add a UndoCommand to the UndoStack, this method is
# called to actually do the work. So that is the perfect time to get the old value, and if we switch the level
# reference, the perfect time to get the value again from the now updated level.


# TODO reference objects only by their index and don't keep references to them
# Only keep references to the level to be replaced?
class SetLevelAddressData(QUndoCommand):
    def __init__(self, level: Level, header_offset: int, enemy_offset: int):
        super(SetLevelAddressData, self).__init__(None)

        self.level = level

        self.old_header_offset = self.level.header_offset
        self.old_enemy_offset = self.level.enemy_offset

        self.new_header_offset = header_offset
        self.new_enemy_offset = enemy_offset

        self.setText(f"Save Level to {self.new_header_offset:#x} and {self.new_enemy_offset:#x}")

    def undo(self):
        self.level.set_addresses(self.old_header_offset, self.old_enemy_offset)

    def redo(self):
        self.level.set_addresses(self.new_header_offset, self.new_enemy_offset)


class AttachLevelToRom(SetLevelAddressData):
    def __init__(self, level: Level, header_offset: int, enemy_offset: int):
        super(AttachLevelToRom, self).__init__(level, header_offset, enemy_offset)

        self.setText(f"Attach Level to {self.new_header_offset:#x} and {self.new_enemy_offset:#x}")


class DetachLevelFromRom(SetLevelAddressData):
    def __init__(self, level: Level):
        super(DetachLevelFromRom, self).__init__(level, 0x0, 0x0)

        self.setText("Detach Level from Rom")


class SetLevelAttribute(QUndoCommand):
    def __init__(self, level: LevelRef, name: str, new_value, display_name="", display_value=""):
        super(SetLevelAttribute, self).__init__(None)

        self.level_ref = level

        self.name = name
        self.old_value = getattr(level, name)
        self.new_value = new_value

        if not display_name:
            display_name = f"Level {' '.join(name.split('_')).capitalize()}"

        if not display_value:
            display_value = str(new_value)

        self.setText(f"{display_name} to {display_value}")

    def undo(self):
        setattr(self.level_ref.level, self.name, self.old_value)

    def redo(self):
        self.old_value = getattr(self.level_ref.level, self.name)
        setattr(self.level_ref.level, self.name, self.new_value)


class SetNextAreaObjectAddress(SetLevelAttribute):
    def __init__(self, level_ref: LevelRef, new_address: int):
        super(SetNextAreaObjectAddress, self).__init__(level_ref, "next_area_objects", new_address)

        self.setText(f"Object Address of Next Area to {new_address:#x}")


class SetNextAreaEnemyAddress(SetLevelAttribute):
    def __init__(self, level_ref: LevelRef, new_address: int):
        super(SetNextAreaEnemyAddress, self).__init__(level_ref, "next_area_enemies", new_address)

        self.setText(f"Enemy Address of Next Area to {new_address:#x}")


class SetNextAreaObjectSet(SetLevelAttribute):
    def __init__(self, level_ref: LevelRef, new_object_set: int):
        super(SetNextAreaObjectSet, self).__init__(level_ref, "next_area_object_set_no", new_object_set)

        self.setText(f"Object Set of Next Area to {OBJECT_SET_NAMES[new_object_set]}")


class ChangeLockIndex(QUndoCommand):
    def __init__(self, level: Level, enemy: EnemyItem, new_lock_index: int):
        super(ChangeLockIndex, self).__init__(None)

        self.level = level
        self.enemy_index = level.enemies.index(enemy)
        self.old_index = 0

        self.new_index = new_lock_index

        enemy = self.level.enemies[self.enemy_index]
        self.setText(f"Set {enemy.name} to break Lock #{new_lock_index}")

    def undo(self):
        enemy = self.level.enemies[self.enemy_index]
        enemy.lock_index = self.old_index

    def redo(self):
        enemy = self.level.enemies[self.enemy_index]
        self.old_index = enemy.lock_index

        enemy.lock_index = self.new_index


class UpdatePalette(QUndoCommand):
    def __init__(
        self,
        level,
        index_in_group: int,
        index_in_palette: int,
        new_color_index: int,
    ):
        super(UpdatePalette, self).__init__("Change Palette Color", None)

        self.level = level

        self.palette_group = load_palette_group(level.object_set_number, level.object_palette_index)
        self.index_in_group = index_in_group

        self.palette_was_changed = PaletteGroup.changed

        self.index_in_palette = index_in_palette

        self.old_color_index = 0
        self.new_color_index = new_color_index

    def undo(self):
        change_color(
            self.palette_group,
            self.index_in_group,
            self.index_in_palette,
            self.old_color_index,
        )

        self.level.reload()
        PaletteGroup.changed = self.palette_was_changed

    def redo(self):
        self.palette_group = load_palette_group(self.level.object_set_number, self.level.object_palette_index)
        self.old_color_index = self.palette_group[self.index_in_group][self.index_in_palette]

        change_color(
            self.palette_group,
            self.index_in_group,
            self.index_in_palette,
            self.new_color_index,
        )

        self.level.reload()
        PaletteGroup.changed = True


class MoveObjects(QUndoCommand):
    """
    We visually move the objects before calling this command, so we cannot rely on the level data being accurate at this
    point. Instead, we get two lists of the moved objects before moving them and at the point where we want to solidify
    the move.
    We have to get the data to undo and redo from those lists and apply them to the level afterwards. Therefore, keeping
    both a connection between the objects and their positions, but also from the object to its index in the level.
    """

    def __init__(
        self,
        level: Level,
        objects_before: list[InLevelObject],
        objects_after: list[InLevelObject],
    ):
        super(MoveObjects, self).__init__(None)

        self.level = level

        indexed_lo_before, indexed_lo_after, indexed_en_before, indexed_en_after = separate_and_index_objects(
            level, objects_before, objects_after
        )

        # !!! remember old positions for each, this data does not exist in the current level, so we cannot get this
        # !!! information in undo(), but it should not be affected by a level change
        self.level_object_before_positions, self.enemy_item_before_positions = self._get_separate_indexed_positions(
            indexed_lo_before, indexed_en_before
        )

        # remember new positions for each, index in level to old position
        self.level_object_after_positions, self.enemy_item_after_positions = self._get_separate_indexed_positions(
            indexed_lo_after, indexed_en_after
        )

        self.setText(f"Move {object_names(objects_after)}")

        # undo once, because we visually already moved them
        self.undo()

    @staticmethod
    def _get_separate_indexed_positions(
        indexed_level_objects: list[tuple[int, InLevelObject]],
        indexed_enemy_items: list[tuple[int, InLevelObject]],
    ):
        # make a dictionary of the indexes and positions of the given objects
        indexed_level_object_positions: dict[int, tuple[int, int]] = {
            index: old_level_object.get_position() for index, old_level_object in indexed_level_objects
        }
        indexed_enemy_item_positions: dict[int, tuple[int, int]] = {
            index: old_enemy_item.get_position() for index, old_enemy_item in indexed_enemy_items
        }

        return indexed_level_object_positions, indexed_enemy_item_positions

    def undo(self):
        self._apply_positions(self.level_object_before_positions, self.enemy_item_before_positions)

        self.level.data_changed.emit()

    def redo(self):
        self._apply_positions(self.level_object_after_positions, self.enemy_item_after_positions)

        self.level.data_changed.emit()

    def _apply_positions(self, level_positions, enemy_positions):
        # get level object in level by index
        for index, position in level_positions.items():
            level_object = self.level.objects[index]
            level_object.set_position(*position)

        for index, position in enemy_positions.items():
            enemy_item = self.level.enemies[index]
            enemy_item.set_position(*position)


class MoveObject(MoveObjects):
    def __init__(self, level: Level, object_before: InLevelObject, object_after: InLevelObject):
        super().__init__(level, [object_before], [object_after])


class ResizeObjects(QUndoCommand):
    def __init__(
        self,
        level: Level,
        objects_before: list[InLevelObject],
        objects_after: list[InLevelObject],
    ):
        super(ResizeObjects, self).__init__(None)

        self.level = level

        # ignore enemies/items because they can't be resized
        indexed_lo_before, indexed_lo_after, *_ = separate_and_index_objects(level, objects_before, objects_after)

        self.objects_after = objects_after

        self.object_data_before: list[tuple[int, bytes]] = [(index, obj.to_bytes()) for index, obj in indexed_lo_before]
        self.object_data_after: list[tuple[int, bytes]] = [(index, obj.to_bytes()) for index, obj in indexed_lo_after]

        self.setText(f"Resize {object_names(objects_after)}")

        # objects are already resized; undo so the undo stack can redo it, when pushed
        self.undo()

    def undo(self):
        for index, data in self.object_data_before:
            obj = self.level.objects[index]
            obj.data = bytearray(data)  # copy to not pass by reference

            obj._setup()

        self.level.data_changed.emit()

    def redo(self):
        for index, data in self.object_data_after:
            obj = self.level.objects[index]
            obj.data = bytearray(data)  # copy to not pass by reference

            obj._setup()

        self.level.data_changed.emit()


def objects_to_indexed_objects(level: Level, objects: list[InLevelObject]) -> list[tuple[int, InLevelObject]]:
    indexes: list[tuple[int, InLevelObject]] = []

    for obj in objects:
        if isinstance(obj, LevelObject):
            index = level.objects.index(obj)

        else:
            assert isinstance(obj, EnemyItem), type(obj)
            index = level.enemies.index(obj)

        indexes.append((index, obj))

    indexes.sort(key=itemgetter(0))

    return indexes


def separate_and_index_objects(level: Level, objects_before: list[InLevelObject], objects_after: list[InLevelObject]):
    indexed_lo_before = []
    indexed_lo_after = []

    indexed_en_before = []
    indexed_en_after = []

    for obj_before, obj_after in zip(objects_before, objects_after):
        if isinstance(obj_before, LevelObject):
            assert isinstance(obj_after, LevelObject)
            index = level.objects.index(obj_after)

            indexed_lo_before.append((index, obj_before))
            indexed_lo_after.append((index, obj_after))
        else:
            assert isinstance(obj_after, EnemyItem)
            index = level.enemies.index(obj_after)

            indexed_en_before.append((index, obj_before))
            indexed_en_after.append((index, obj_after))

    return indexed_lo_before, indexed_lo_after, indexed_en_before, indexed_en_after


def move_objects(level: Level, indexed_objects: list[tuple[int, InLevelObject]], restore_only=False):
    for index, obj in indexed_objects:
        if isinstance(obj, LevelObject):
            if not restore_only:
                level.objects.remove(obj)

            level.objects.insert(index, obj)

        else:
            assert isinstance(obj, EnemyItem)
            if not restore_only:
                level.enemies.remove(obj)

            level.enemies.insert(index, obj)


def object_names(objects: list[InLevelObject]) -> str:
    amount = len(objects)

    if amount == 1:
        return f"'{objects[0].name}'"

    if objects and all(isinstance(obj, EnemyItem) for obj in objects):
        return f"{amount} enemies"
    else:
        return f"{amount} objects"


class ToForeground(QUndoCommand):
    def __init__(self, level: Level, objects: list[InLevelObject]):
        super(ToForeground, self).__init__(None)

        self.level = level
        self.objects = objects

        self.indexes_before: list[tuple[int, InLevelObject]] = objects_to_indexed_objects(level, objects)

        self.setText(f"Bring {object_names(objects)} to the foreground")

    def undo(self):
        move_objects(self.level, self.indexes_before)

        self.level.data_changed.emit()

    def redo(self):
        self._update_object_refs()

        self.level.bring_to_foreground(self.objects)

        self.level.data_changed.emit()

    def _update_object_refs(self):
        # update object references with indexes
        self.objects.clear()

        for index, obj in self.indexes_before:
            if isinstance(obj, LevelObject):
                self.objects.append(self.level.objects[index])
            else:
                self.objects.append(self.level.enemies[index])

        self.indexes_before = objects_to_indexed_objects(self.level, self.objects)


class ToBackground(ToForeground):
    def __init__(self, level: Level, objects: list[InLevelObject]):
        super(ToBackground, self).__init__(level, objects)

        self.indexes_before.reverse()

        self.setText(f"Put {object_names(objects)} in the background")

    def redo(self):
        self._update_object_refs()

        self.level.bring_to_background(self.objects)

        self.level.data_changed.emit()


class ImportASMEnemies(QUndoCommand):
    def __init__(self, level: Level, path: PathLike):
        super(ImportASMEnemies, self).__init__(None)

        self.level = level

        self.path = path

        self.enemy_data_before = bytearray()
        self.enemy_data_after = bytearray()

        self.setText(f"Importing Enemies from {Path(path).name}")

    def undo(self):
        self.level._load_enemies(self.enemy_data_before)

        self.level.data_changed.emit()

    def redo(self):
        _, (_, self.enemy_data_before) = self.level.to_bytes()

        if not self.enemy_data_after:
            load_asm_enemy(self.path, self.level)

            _, (_, self.enemy_data_after) = self.level.to_bytes()

        self.level._load_enemies(self.enemy_data_after)

        self.level.data_changed.emit()


class AddObject(QUndoCommand):
    def __init__(self, level: Level, obj: InLevelObject, index=-1):
        super(AddObject, self).__init__(None)

        self.level = level
        self.obj = obj

        self.setText(f"Add {obj.name}")

        if index == -1:
            if isinstance(obj, LevelObject):
                self.index_to_add = len(self.level.objects)
            else:
                assert isinstance(obj, EnemyItem)
                self.index_to_add = len(self.level.enemies)
        else:
            self.index_to_add = index

    def undo(self):
        if isinstance(self.obj, LevelObject):
            self.level.objects.pop(self.index_to_add)
        else:
            self.level.enemies.pop(self.index_to_add)

        self.level.data_changed.emit()

    def redo(self):
        # create a new object instead of using the cached one in case graphic data has changed in the meantime
        if isinstance(self.obj, LevelObject):
            self.level.add_object(
                self.obj.domain,
                self.obj.obj_index,
                Position.from_tuple(self.obj.get_position()),
                self.obj.length,
                self.index_to_add,
            )
        else:
            assert isinstance(self.obj, EnemyItem)
            self.level.add_enemy(self.obj.obj_index, Position.from_tuple(self.obj.get_position()), self.index_to_add)

        self.level.data_changed.emit()


class AddLevelObjectAt(QUndoCommand):
    def __init__(
        self,
        level_view: "LevelView",
        pos: QPoint,
        domain=0,
        obj_type=0,
        length: int | None = None,
        index=-1,
    ):
        super(AddLevelObjectAt, self).__init__(None)

        self.view = level_view
        self.level = level_view.level_ref

        # convert here, in case there's a zoom change happening between undo and redo
        self.level_point = level_view.to_level_point(pos)

        self.domain = domain
        self.obj_type = obj_type
        self.length = length

        self.index = index

    def undo(self):
        self.level.objects.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        added_object = self.level.add_object(self.domain, self.obj_type, self.level_point, self.length, self.index)

        # in case the index was just -1
        self.index = self.level.objects.index(added_object)

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {added_object.name} at {added_object.x_position}, {added_object.y_position}")

        self.level.data_changed.emit()


class AddEnemyAt(QUndoCommand):
    def __init__(self, level_view: "LevelView", pos: QPoint, enemy_type=0, index=-1):
        super(AddEnemyAt, self).__init__(None)

        self.view = level_view
        self.level = level_view.level_ref

        # convert here, in case there's a zoom change happening between undo and redo
        self.level_point = level_view.to_level_point(pos)

        self.enemy_type = enemy_type

        self.index = index

    def undo(self):
        self.level.enemies.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        added_enemy = self.level.add_enemy(self.enemy_type, self.level_point, self.index)

        # in case the index was just -1
        self.index = self.level.enemies.index(added_enemy)

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {added_enemy.name} at {added_enemy.x_position}, {added_enemy.y_position}")

        self.level.data_changed.emit()


class PasteObjectsAt(QUndoCommand):
    def __init__(
        self,
        level_view: "LevelView",
        paste_data: tuple[list[InLevelObject], Position],
        pos: QPoint = None,
    ):
        super(PasteObjectsAt, self).__init__(None)

        self.view = level_view
        self.paste_data = paste_data

        objects, _ = paste_data

        self.object_count = len(list(filter(lambda obj: isinstance(obj, LevelObject), objects)))
        self.enemy_count = len(objects) - self.object_count

        self.created_objects: list[LevelObject] = []
        self.created_enemies: list[EnemyItem] = []

        if pos is None:
            self.level_point = self.view.last_mouse_position
        else:
            self.level_point = self.view.to_level_point(pos)

        self.last_mouse_position: Position = self.view.last_mouse_position.copy()

        self.setText(f"Paste {object_names(objects)}")

    def undo(self):
        for _ in range(self.object_count):
            self.view.level_ref.level.objects.pop()

        for _ in range(self.enemy_count):
            self.view.level_ref.level.enemies.pop()

        self.view.level_ref.level.data_changed.emit()

    def redo(self):
        # this will create clones of the cached objects, not paste them with their old graphics (in case of ROM reload)
        if not self.created_objects and not self.created_enemies:
            self.view.paste_objects_at(self.paste_data, self.level_point)

            if self.object_count:
                self.created_objects = self.view.level_ref.level.objects[-self.object_count :]

            if self.enemy_count:
                self.created_enemies = self.view.level_ref.level.enemies[-self.enemy_count :]
        else:
            self.view.level_ref.level.objects.extend(self.created_objects)
            self.view.level_ref.level.enemies.extend(self.created_enemies)

        self.view.level_ref.level.data_changed.emit()


class RemoveObjects(QUndoCommand):
    def __init__(self, level: Level, objects: list[InLevelObject]):
        super(RemoveObjects, self).__init__(None)

        self.level = level
        self.objects = objects

        self.indexes_before_removal = objects_to_indexed_objects(self.level, self.objects)

        self.setText(f"Remove {object_names(self.objects)}")

    def undo(self):
        self.level.clear_selection()

        move_objects(self.level, self.indexes_before_removal, restore_only=True)

        self.level.data_changed.emit()

    def redo(self):
        for index, obj in reversed(self.indexes_before_removal):
            if isinstance(obj, LevelObject):
                self.level.objects.pop(index)
            else:
                assert isinstance(obj, EnemyItem)
                self.level.enemies.pop(index)

        self.level.data_changed.emit()


class RemoveObject(RemoveObjects):
    def __init__(self, level: Level, in_level_object: InLevelObject):
        super().__init__(level, [in_level_object])


# Could maybe be replaced by a macro of remove and add object?
class ReplaceLevelObject(QUndoCommand):
    def __init__(
        self,
        level: Level,
        to_replace: LevelObject,
        domain: int,
        obj_type: int,
        length: int | None,
    ):
        super(ReplaceLevelObject, self).__init__(None)

        self.level = level
        self.domain = domain
        self.obj_type = obj_type
        self.length = length

        self.to_replace = to_replace
        self.created_object: LevelObject | None = None
        self.index = self.level.objects.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        self.level.objects[self.index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        self.to_replace = self.level.objects.pop(self.index)

        x, y = self.to_replace.get_position()

        if self.created_object is None:
            self.created_object = self.level.add_object(
                self.domain,
                self.obj_type,
                Position.from_xy(x, y),
                self.length,
                self.index,
            )
        else:
            self.level.objects.insert(self.index, self.created_object)

        assert self.created_object is not None
        self.created_object.selected = self.to_replace.selected

        self.level.data_changed.emit()


class ReplaceEnemy(QUndoCommand):
    def __init__(self, level: Level, to_replace: EnemyItem, obj_type: int):
        super(ReplaceEnemy, self).__init__(None)

        self.level = level
        self.obj_type = obj_type

        self.to_replace = to_replace
        self.created_enemy: EnemyItem | None = None
        self.index = self.level.enemies.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        self.level.enemies[self.index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        self.to_replace = self.level.enemies.pop(self.index)

        x, y = self.to_replace.get_position()

        if self.created_enemy is None:
            self.created_enemy = self.level.add_enemy(self.obj_type, Position.from_xy(x, y), self.index)
        else:
            self.level.enemies.insert(self.index, self.created_enemy)

        self.created_enemy.selected = self.to_replace.selected

        self.level.data_changed.emit()


class AddJump(QUndoCommand):
    def __init__(self, level: Level, jump: Jump | None = None, index: int = -1):
        super(AddJump, self).__init__(None)

        self.level = level

        if jump is None:
            self.jump = Jump.from_properties(0, 0, 0, 0)
        else:
            self.jump = jump

        if index == -1:
            self.index = len(level.jumps)
        else:
            self.index = index

        self.setText("Add Jump")

    def undo(self):
        self.level.jumps.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        self.level.jumps.insert(self.index, self.jump)

        self.level.data_changed.emit()


class RemoveJump(QUndoCommand):
    def __init__(self, level: Level, index: int):
        super(RemoveJump, self).__init__(None)

        self.level = level

        self.jump = self.level.jumps[index]
        self.index = index

        self.setText(f"Remove {self.jump}")

    def undo(self):
        self.level.jumps.insert(self.index, self.jump)

        self.level.data_changed.emit()

    def redo(self):
        self.level.jumps.pop(self.index)

        self.level.data_changed.emit()


class UpdatePipeData(QUndoCommand):
    def __init__(self, pipe_data: list[PipeData]):
        super(UpdatePipeData, self).__init__(None)

        self.pipe_data_before = [PipeData(ROM(), index) for index in range(PIPE_PAIR_COUNT)]
        self.pipe_data_after = pipe_data

        self.setText("Updating Pipe Exit Pair Data")

    def undo(self) -> None:
        for pipe_data in self.pipe_data_before:
            pipe_data.write_back()

    def redo(self) -> None:
        for pipe_data in self.pipe_data_after:
            pipe_data.write_back()
