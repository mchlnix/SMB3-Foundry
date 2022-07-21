from operator import itemgetter
from typing import List, Optional, TYPE_CHECKING, Tuple

from PySide6.QtCore import QPoint
from PySide6.QtGui import QUndoCommand

from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.gfx.objects import EnemyItem, Jump, LevelObject
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.level.Level import Level

if TYPE_CHECKING:
    from foundry.gui.LevelView import LevelView


class SetLevelAddressData(QUndoCommand):
    def __init__(self, level: Level, header_offset: int, enemy_offset: int):
        super(SetLevelAddressData, self).__init__()

        self.level = level

        self.old_header_offset = self.level.header_offset
        self.old_enemy_offset = self.level.enemy_offset

        self.new_header_offset = header_offset
        self.new_enemy_offset = enemy_offset

        self.setText(f"Save Level to {hex(self.new_header_offset)} and {hex(self.new_enemy_offset)}")

    def undo(self):
        self.level.set_addresses(self.old_header_offset, self.old_enemy_offset)

    def redo(self):
        self.level.set_addresses(self.new_header_offset, self.new_enemy_offset)


class AttachLevelToRom(SetLevelAddressData):
    def __init__(self, level: Level, header_offset: int, enemy_offset: int):
        super(AttachLevelToRom, self).__init__(level, header_offset, enemy_offset)

        self.setText(f"Attach Level to {hex(self.new_header_offset)} and {hex(self.new_enemy_offset)}")


class DetachLevelFromRom(SetLevelAddressData):
    def __init__(self, level: Level):
        super(DetachLevelFromRom, self).__init__(level, 0x0, 0x0)

        self.setText("Detach Level from Rom")


class SetLevelAttribute(QUndoCommand):
    def __init__(self, level: Level, name: str, new_value, display_name="", display_value=""):
        super(SetLevelAttribute, self).__init__()

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

        self.setText(f"Object Address of Next Area to {hex(new_address)}")


class SetNextAreaEnemyAddress(SetLevelAttribute):
    def __init__(self, level: Level, new_address: int):
        super(SetNextAreaEnemyAddress, self).__init__(level, "next_area_enemies", new_address)

        self.setText(f"Enemy Address of Next Area to {hex(new_address)}")


class SetNextAreaObjectSet(SetLevelAttribute):
    def __init__(self, level: Level, new_object_set: int):
        super(SetNextAreaObjectSet, self).__init__(level, "next_area_object_set", new_object_set)

        self.setText(f"Object Set of Next Area to {OBJECT_SET_NAMES[new_object_set]}")


def objects_to_indexed_objects(level: Level, objects: List[InLevelObject]) -> List[Tuple[int, InLevelObject]]:
    indexes = []

    for obj in objects:
        if isinstance(obj, LevelObject):
            index = level.objects.index(obj)

        else:
            assert isinstance(obj, EnemyItem)
            index = level.enemies.index(obj)

        indexes.append((index, obj))

    indexes.sort(key=itemgetter(0))

    return indexes


def move_objects(level: Level, indexed_objects: List[Tuple[int, InLevelObject]], restore_only=False):
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


def object_names(objects: List[InLevelObject]) -> str:
    amount = len(objects)

    if amount == 1:
        return f"'{objects[0].name}'"

    if objects and all(isinstance(obj, EnemyItem) for obj in objects):
        return f"{amount} enemies"
    else:
        return f"{amount} objects"


class ToForeground(QUndoCommand):
    def __init__(self, level: Level, objects: List[InLevelObject]):
        super(ToForeground, self).__init__()

        self.level = level
        self.objects = objects

        self.indexes_before = objects_to_indexed_objects(level, objects)

        if len(objects) == 1:
            self.setText(f"Bring {object_names(objects)} to the foreground")

    def undo(self):
        move_objects(self.level, self.indexes_before)

        self.level.data_changed.emit()

    def redo(self):
        self.level.bring_to_foreground(self.objects)


class ToBackground(ToForeground):
    def __init__(self, level: Level, objects: List[InLevelObject]):
        super(ToBackground, self).__init__(level, objects)

        self.indexes_before.reverse()

        if len(self.objects) == 1:
            self.setText(f"Put {object_names(objects)} in the background")

    def redo(self):
        self.level.bring_to_background(self.objects)


class AddObject(QUndoCommand):
    def __init__(self, level: Level, obj: InLevelObject, index=-1):
        super(AddObject, self).__init__()

        self.level = level
        self.obj = obj

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
            self.level.enemies.insert(self.index, self.obj)

        self.level.data_changed.emit()


class AddLevelObjectAt(QUndoCommand):
    def __init__(
        self, level_view: "LevelView", pos: QPoint, domain=0, obj_type=0, length: Optional[int] = None, index=-1
    ):
        super(AddLevelObjectAt, self).__init__()

        self.view = level_view
        self.level = level_view.level_ref.level

        self.pos = pos

        self.domain = domain
        self.obj_type = obj_type
        self.length = length

        self.index = index

    def undo(self):
        self.level.objects.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        self.view.add_object(self.domain, self.obj_type, self.pos, self.length, self.index)

        self.index = len(self.level.objects) - 1

        level_obj = self.level.objects[-1]

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {level_obj.name} at {level_obj.x_position}, {level_obj.y_position}")


class AddEnemyAt(QUndoCommand):
    def __init__(self, level_view: "LevelView", pos: QPoint, enemy_type=0, index=-1):
        super(AddEnemyAt, self).__init__()

        self.view = level_view
        self.level = level_view.level_ref.level

        self.pos = pos

        self.enemy_type = enemy_type

        self.index = index

    def undo(self):
        self.level.enemies.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        self.view.add_enemy(self.enemy_type, self.pos, self.index)

        if self.index == -1:
            self.index = len(self.level.enemies) - 1

        enemy = self.level.enemies[self.index]

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {enemy.name} at {enemy.x_position}, {enemy.y_position}")


class PasteObjectsAt(QUndoCommand):
    def __init__(
        self, level_view: "LevelView", paste_data: Tuple[List[InLevelObject], Tuple[int, int]], pos: QPoint = None
    ):
        super(PasteObjectsAt, self).__init__()

        self.view = level_view
        self.paste_data = paste_data

        objects, _ = paste_data

        self.object_count = len(list(filter(lambda obj: isinstance(obj, LevelObject), objects)))
        self.enemy_count = len(objects) - self.object_count

        self.pos = pos
        self.last_mouse_position = self.view.last_mouse_position

        self.setText(f"Paste {object_names(objects)}")

    def undo(self):
        for _ in range(self.object_count):
            self.view.level_ref.level.objects.pop()

        for _ in range(self.enemy_count):
            self.view.level_ref.level.enemies.pop()

    def redo(self):
        # TODO, replace with the level version, so we don't have to restore the last mouse position?
        # restore last mouse position, since it is used inside the method as a fallback
        self.view.last_mouse_position = self.last_mouse_position
        self.view.paste_objects_at(self.paste_data, self.pos)


class RemoveObjects(QUndoCommand):
    def __init__(self, level: Level, objects: List[InLevelObject]):
        super(RemoveObjects, self).__init__()

        self.level = level
        self.objects = objects

        self.indexes_before_removal = objects_to_indexed_objects(self.level, self.objects)

        self.setText(f"Remove {object_names(self.objects)}")

    def undo(self):
        self.level.clear_selection()

        move_objects(self.level, self.indexes_before_removal, restore_only=True)

        self.level.data_changed.emit()

    def redo(self):
        self.level.remove_selected_objects()


# Could maybe be replaced by a macro of remove and add object?
class ReplaceLevelObject(QUndoCommand):
    def __init__(self, level: Level, to_replace: LevelObject, domain: int, obj_type: int, length: int):
        super(ReplaceLevelObject, self).__init__()

        self.level = level
        self.domain = domain
        self.obj_type = obj_type
        self.length = length

        self.to_replace = to_replace
        self.index = self.level.objects.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        self.level.objects[self.index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        self.level.remove_object(self.to_replace)

        x, y = self.to_replace.get_position()

        new_object = self.level.add_object(self.domain, self.obj_type, x, y, self.length, self.index)
        new_object.selected = self.to_replace.selected


class ReplaceEnemy(QUndoCommand):
    def __init__(self, level: Level, to_replace: EnemyItem, obj_type: int):
        super(ReplaceEnemy, self).__init__()

        self.level = level
        self.obj_type = obj_type

        self.to_replace = to_replace
        self.index = self.level.enemies.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        self.level.enemies[self.index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        self.level.remove_object(self.to_replace)

        x, y = self.to_replace.get_position()

        new_object = self.level.add_enemy(self.obj_type, x, y, self.index)
        new_object.selected = self.to_replace.selected


class AddJump(QUndoCommand):
    def __init__(self, level: Level, jump: Jump = None, index: int = -1):
        super(AddJump, self).__init__()

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
        super(RemoveJump, self).__init__()

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
