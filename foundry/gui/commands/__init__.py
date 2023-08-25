from operator import itemgetter
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPoint
from PySide6.QtGui import QUndoCommand

from foundry.game.File import ROM
from foundry.game.gfx import change_color
from foundry.game.gfx.objects import EnemyItem, Jump, LevelObject
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.level.Level import Level
from foundry.gui.asm import load_asm_enemy
from smb3parse.constants import PIPE_PAIR_COUNT
from smb3parse.data_points import Position
from smb3parse.data_points.pipe_data import PipeData
from smb3parse.objects.object_set import OBJECT_SET_NAMES

if TYPE_CHECKING:
    from foundry.gui.visualization.level.LevelView import LevelView


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
    def __init__(self, level: Level, name: str, new_value, display_name="", display_value=""):
        super(SetLevelAttribute, self).__init__(None)

        self.level = level

        self.name = name
        self.old_value = getattr(level, name)
        self.new_value = new_value

        if not display_name:
            display_name = f"Level {' '.join(name.split('_')).capitalize()}"

        if not display_value:
            display_value = str(new_value)

        self.setText(f"{display_name} to {display_value}")

    def undo(self):
        setattr(self.level, self.name, self.old_value)

    def redo(self):
        setattr(self.level, self.name, self.new_value)


class SetNextAreaObjectAddress(SetLevelAttribute):
    def __init__(self, level: Level, new_address: int):
        super(SetNextAreaObjectAddress, self).__init__(level, "next_area_objects", new_address)

        self.setText(f"Object Address of Next Area to {new_address:#x}")


class SetNextAreaEnemyAddress(SetLevelAttribute):
    def __init__(self, level: Level, new_address: int):
        super(SetNextAreaEnemyAddress, self).__init__(level, "next_area_enemies", new_address)

        self.setText(f"Enemy Address of Next Area to {new_address:#x}")


class SetNextAreaObjectSet(SetLevelAttribute):
    def __init__(self, level: Level, new_object_set: int):
        super(SetNextAreaObjectSet, self).__init__(level, "next_area_object_set_no", new_object_set)

        self.setText(f"Object Set of Next Area to {OBJECT_SET_NAMES[new_object_set]}")


class ChangeLockIndex(QUndoCommand):
    def __init__(self, enemy: EnemyItem, new_lock_index: int):
        super(ChangeLockIndex, self).__init__(None)

        self.enemy = enemy
        self.old_index = enemy.lock_index

        self.new_index = new_lock_index

        self.setText(f"Set {enemy.name} to break Lock #{new_lock_index}")

    def undo(self):
        self.enemy.lock_index = self.old_index

    def redo(self):
        self.enemy.lock_index = self.new_index


class UpdatePalette(QUndoCommand):
    def __init__(
        self,
        level,
        palette_group: PaletteGroup,
        index_in_group: int,
        index_in_palette: int,
        new_color_index: int,
    ):
        super(UpdatePalette, self).__init__(None)

        self.level = level

        self.palette_group = palette_group
        self.index_in_group = index_in_group

        self.palette_was_changed = PaletteGroup.changed

        self.index_in_palette = index_in_palette

        self.old_color_index = palette_group[index_in_group][index_in_palette]
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
        change_color(
            self.palette_group,
            self.index_in_group,
            self.index_in_palette,
            self.new_color_index,
        )

        self.level.reload()
        PaletteGroup.changed = True


class MoveObjects(QUndoCommand):
    def __init__(
        self,
        level: Level,
        objects_before: list[InLevelObject],
        objects_after: list[InLevelObject],
    ):
        super(MoveObjects, self).__init__(None)

        self.level = level

        self.positions_before = [obj.get_position() for obj in objects_before]
        self.objects = objects_after
        self.positions_after = [obj.get_position() for obj in objects_after]

        self.setText(f"Move {object_names(objects_after)}")

        self.undo()

    def undo(self):
        for obj, orig_pos in zip(self.objects, self.positions_before):
            obj.set_position(*orig_pos)

        self.level.data_changed.emit()

    def redo(self):
        for obj, pos_after in zip(self.objects, self.positions_after):
            obj.set_position(*pos_after)

        self.level.data_changed.emit()


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

        self.objects_after = objects_after

        self.object_data_before = [obj.to_bytes() for obj in objects_before]
        self.object_data_after = [obj.to_bytes() for obj in objects_after]

        self.setText(f"Resize {object_names(objects_after)}")

        # # objects are already resized; undo so the undo stack can redo it, when pushed
        self.undo()

    def undo(self):
        for obj, data in zip(self.objects_after, self.object_data_before):
            if not isinstance(obj, LevelObject):
                continue

            obj.data = bytearray(data)  # copy to not pass by reference

            obj._setup()

        self.level.data_changed.emit()

    def redo(self):
        for obj, data_after in zip(self.objects_after, self.object_data_after):
            if not isinstance(obj, LevelObject):
                continue

            obj.data = bytearray(data_after)  # copy to not pass by reference

            obj._setup()

        self.level.data_changed.emit()


def objects_to_indexed_objects(level: Level, objects: list[InLevelObject]) -> list[tuple[int, InLevelObject]]:
    indexes = []

    for obj in objects:
        if isinstance(obj, LevelObject):
            index = level.objects.index(obj)

        else:
            assert isinstance(obj, EnemyItem), type(obj)
            index = level.enemies.index(obj)

        indexes.append((index, obj))

    indexes.sort(key=itemgetter(0))

    return indexes


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

        self.indexes_before = objects_to_indexed_objects(level, objects)

        self.setText(f"Bring {object_names(objects)} to the foreground")

    def undo(self):
        move_objects(self.level, self.indexes_before)

        self.level.data_changed.emit()

    def redo(self):
        self.level.bring_to_foreground(self.objects)

        self.level.data_changed.emit()


class ToBackground(ToForeground):
    def __init__(self, level: Level, objects: list[InLevelObject]):
        super(ToBackground, self).__init__(level, objects)

        self.indexes_before.reverse()

        self.setText(f"Put {object_names(objects)} in the background")

    def redo(self):
        self.level.bring_to_background(self.objects)

        self.level.data_changed.emit()


class ImportASMEnemies(QUndoCommand):
    def __init__(self, level: Level, path: PathLike):
        super(ImportASMEnemies, self).__init__(None)

        self.level = level

        self.path = path

        self.enemies_before = level.enemies.copy()
        self.enemies_after: list[EnemyItem] = []

        self.setText(f"Importing Enemies from {Path(path).name}")

    def undo(self):
        self.level.enemies = self.enemies_before

        self.level.data_changed.emit()

    def redo(self):
        if not self.enemies_after:
            load_asm_enemy(self.path, self.level)

            self.enemies_after = self.level.enemies.copy()
        else:
            self.level.enemies = self.enemies_after

        self.level.data_changed.emit()


class AddObject(QUndoCommand):
    def __init__(self, level: Level, obj: InLevelObject, index=-1):
        super(AddObject, self).__init__(None)

        self.level = level
        self.obj = obj

        self.setText(f"Add {obj.name}")

        if index == -1:
            if isinstance(obj, LevelObject):
                self.index = len(self.level.objects)
            else:
                assert isinstance(obj, EnemyItem)
                self.index = len(self.level.enemies)
        else:
            self.index = index

    def undo(self):
        if isinstance(self.obj, LevelObject):
            self.level.objects.pop(self.index)
        else:
            self.level.enemies.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        if isinstance(self.obj, LevelObject):
            self.level.objects.insert(self.index, self.obj)
        else:
            assert isinstance(self.obj, EnemyItem)
            self.level.enemies.insert(self.index, self.obj)

        self.level.data_changed.emit()


class AddLevelObjectAt(QUndoCommand):
    def __init__(
        self,
        level_view: "LevelView",
        pos: QPoint,
        domain=0,
        obj_type=0,
        length: Optional[int] = None,
        index=-1,
    ):
        super(AddLevelObjectAt, self).__init__(None)

        self.view = level_view
        self.level = level_view.level_ref.level

        self.pos = pos

        self.domain = domain
        self.obj_type = obj_type
        self.length = length

        self.added_object: Optional[LevelObject] = None

        self.index = index

    def undo(self):
        self.level.objects.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        if self.added_object is None:
            self.view.add_object(self.domain, self.obj_type, self.pos, self.length, self.index)
            self.added_object = self.level.objects[self.index]

            # in case the index was just -1
            self.index = self.level.objects.index(self.added_object)
        else:
            self.level.objects.insert(self.index, self.added_object)

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {self.added_object.name} at {self.added_object.x_position}, {self.added_object.y_position}")

        self.level.data_changed.emit()


class AddEnemyAt(QUndoCommand):
    def __init__(self, level_view: "LevelView", pos: QPoint, enemy_type=0, index=-1):
        super(AddEnemyAt, self).__init__(None)

        self.view = level_view
        self.level = level_view.level_ref.level

        self.pos = pos

        self.enemy_type = enemy_type

        self.added_enemy: Optional[EnemyItem] = None

        self.index = index

    def undo(self):
        self.level.enemies.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        if self.added_enemy is None:
            self.view.add_enemy(self.enemy_type, self.pos, self.index)
            self.added_enemy = self.level.enemies[self.index]

            # in case the index was just -1
            self.index = self.level.enemies.index(self.added_enemy)
        else:
            self.level.enemies.insert(self.index, self.added_enemy)

        enemy = self.level.enemies[self.index]

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {enemy.name} at {enemy.x_position}, {enemy.y_position}")

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

        self.pos = pos
        self.last_mouse_position: Position = self.view.last_mouse_position.copy()

        self.setText(f"Paste {object_names(objects)}")

    def undo(self):
        for _ in range(self.object_count):
            self.view.level_ref.level.objects.pop()

        for _ in range(self.enemy_count):
            self.view.level_ref.level.enemies.pop()

        self.view.level_ref.level.data_changed.emit()

    def redo(self):
        # TODO, replace with the level version, so we don't have to restore the last mouse position?
        # maybe only use indexes into object list, instead of object refs themselves?
        # restore last mouse position, since it is used inside the method as a fallback
        self.view.last_mouse_position = self.last_mouse_position.copy()

        if not self.created_objects and not self.created_enemies:
            self.view.paste_objects_at(self.paste_data, self.pos)

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
        for obj in self.objects:
            if isinstance(obj, LevelObject):
                self.level.objects.remove(obj)
            else:
                assert isinstance(obj, EnemyItem)
                self.level.enemies.remove(obj)

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
        self.created_object: Optional[LevelObject] = None
        self.index = self.level.objects.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        self.level.objects[self.index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        self.level.remove_object(self.to_replace)

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
        self.created_enemy: Optional[EnemyItem] = None
        self.index = self.level.enemies.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        self.level.enemies[self.index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        self.level.remove_object(self.to_replace)

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
        self.level.jumps.remove(self.jump)

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
