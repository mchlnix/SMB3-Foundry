from operator import itemgetter
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint
from PySide6.QtGui import QImage, QUndoCommand

from foundry.game.File import ROM
from foundry.game.gfx import GraphicsSet, change_color
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


class UndoCommand(QUndoCommand):
    MAGIC_VALUE_LEVEL = "LEVEL"
    MAGIC_VALUE_LEVEL_VIEW = "LEVEL_VIEW"

    def to_data(self) -> list:
        raise NotImplementedError("UndoCommand.export() is not implemented")

    @classmethod
    def from_data(cls, *args, **kwargs) -> "UndoCommand":
        raise NotImplementedError("UndoCommand.import_data() is not implemented")


# TODO reference objects only by their index and don't keep references to them
# Only keep references to the level to be replaced?
class SetLevelAddressData(UndoCommand):
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

    def to_data(self) -> list:
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.new_header_offset, self.new_enemy_offset]

    @classmethod
    def from_data(cls, level: Level, header_offset: int, enemy_offset: int) -> "UndoCommand":
        return cls(level, header_offset, enemy_offset)


class AttachLevelToRom(SetLevelAddressData):
    def __init__(self, level: Level, header_offset: int, enemy_offset: int):
        super(AttachLevelToRom, self).__init__(level, header_offset, enemy_offset)

        self.setText(f"Attach Level to {self.new_header_offset:#x} and {self.new_enemy_offset:#x}")


class DetachLevelFromRom(SetLevelAddressData):
    def __init__(self, level: Level):
        super(DetachLevelFromRom, self).__init__(level, 0x0, 0x0)

        self.setText("Detach Level from Rom")


class SetLevelAttribute(UndoCommand):
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

    def id(self):
        return 121

    def mergeWith(self, other):
        if not isinstance(other, SetLevelAttribute):
            return False

        if self.name != other.name:
            return False

        self.new_value = other.new_value

        self.setText(other.text())

        return True

    def to_data(self) -> list:
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.name, self.new_value, self.text()]

    @classmethod
    def from_data(cls, level: LevelRef, attr_name: str, new_value, text: str) -> "UndoCommand":
        command = cls(level, attr_name, new_value)

        command.setText(text)

        return command


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


class ChangeLockIndex(UndoCommand):
    def __init__(self, level: Level, enemy_index: int, new_lock_index: int):
        super(ChangeLockIndex, self).__init__(None)

        self.level = level
        self.enemy_index = enemy_index
        self.old_index = 0

        self.new_lock_index = new_lock_index

        enemy = self.level.enemies[self.enemy_index]
        self.setText(f"Set {enemy.name} to break Lock #{new_lock_index}")

    def undo(self):
        enemy = self.level.enemies[self.enemy_index]
        enemy.lock_index = self.old_index

    def redo(self):
        enemy = self.level.enemies[self.enemy_index]
        self.old_index = enemy.lock_index

        enemy.lock_index = self.new_lock_index

    def to_data(self) -> list:
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.enemy_index, self.new_lock_index]

    @classmethod
    def from_data(cls, level: Level, enemy_index: int, new_lock_index: int) -> "UndoCommand":
        return cls(level, enemy_index, new_lock_index)


class UpdatePalette(UndoCommand):
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

    def to_data(self) -> list:
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.index_in_group, self.index_in_palette, self.new_color_index]

    @classmethod
    def from_data(cls, level: Level, index_in_group: int, index_in_palette: int, new_color_index: int) -> "UndoCommand":
        return cls(level, index_in_group, index_in_palette, new_color_index)


class MoveObjects(UndoCommand):
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

    def to_data(self):
        return [
            UndoCommand.MAGIC_VALUE_LEVEL,
            self.level_object_before_positions,
            self.level_object_after_positions,
            self.enemy_item_before_positions,
            self.enemy_item_after_positions,
        ]

    @classmethod
    def from_data(cls, level, objects_before, objects_after, enemies_before, enemies_after):
        command = cls(level, [], [])

        command.level_object_before_positions = objects_before
        command.level_object_after_positions = objects_after

        command.enemy_item_before_positions = enemies_before
        command.enemy_item_after_positions = enemies_after

        return command

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


class ResizeObjects(UndoCommand):
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

        self.object_data_before: list[tuple[int, bytes]] = [
            (index, bytes(obj.to_bytes())) for index, obj in indexed_lo_before
        ]
        self.object_data_after: list[tuple[int, bytes]] = [
            (index, bytes(obj.to_bytes())) for index, obj in indexed_lo_after
        ]

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

    def to_data(self):
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.object_data_before, self.object_data_after]

    @classmethod
    def from_data(cls, level, objects_before, objects_after):
        new_command = cls(level, [], [])

        new_command.object_data_before = objects_before
        new_command.object_data_after = objects_after

        return new_command


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


class ToForeground(UndoCommand):
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

    def to_data(self):
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.indexes_before]

    @classmethod
    def from_data(cls, level, objects_before):
        command = cls(level, [])

        command.indexes_before = objects_before

        return command


class ToBackground(ToForeground):
    def __init__(self, level: Level, objects: list[InLevelObject]):
        super(ToBackground, self).__init__(level, objects)

        self.indexes_before.reverse()

        self.setText(f"Put {object_names(objects)} in the background")

    def redo(self):
        self._update_object_refs()

        self.level.bring_to_background(self.objects)

        self.level.data_changed.emit()


class ImportASMEnemies(UndoCommand):
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

    def to_data(self):
        return [UndoCommand.MAGIC_VALUE_LEVEL, str(self.path)]

    @classmethod
    def from_data(cls, level, path_str):
        command = cls(level, Path(path_str))

        return command


class AddLevelObjectAt(UndoCommand):
    def __init__(
        self,
        level_view: "LevelView",
        pos: QPoint,
        domain=0,
        obj_type=0,
        length: int | None = None,
        index=-1,
        selected=False,
    ):
        super(AddLevelObjectAt, self).__init__(None)

        self.view = level_view
        self.level = level_view.level_ref

        # convert here, in case there's a zoom change happening between undo and redo
        # TODO why not just take the level point as an argument?
        self.level_point = level_view.to_level_point(pos)

        self.domain = domain
        self.obj_type = obj_type
        self.length = length

        self.index = index

        self.was_selected = selected

    def undo(self):
        self.level.objects.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        added_object = self.level.add_object(self.domain, self.obj_type, self.level_point, self.length, self.index)

        added_object.selected = self.was_selected

        # in case the index was just -1
        self.index = self.level.objects.index(added_object)

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {added_object.name} at {added_object.x_position}, {added_object.y_position}")

        self.level.data_changed.emit()

    def to_data(self) -> list:
        return [
            UndoCommand.MAGIC_VALUE_LEVEL_VIEW,
            self.level_point.xy,
            self.domain,
            self.obj_type,
            self.length,
            self.index,
            self.was_selected,
        ]

    @classmethod
    def from_data(
        cls,
        level_view: "LevelView",
        xy: tuple[int, int],
        domain: int,
        obj_type: int,
        length: int | None,
        index: int,
        was_selected: bool,
    ):
        command = cls(level_view, QPoint(0, 0), domain, obj_type, length, index, selected=was_selected)
        command.level_point = Position.from_tuple(xy)

        return command


class AddEnemyAt(UndoCommand):
    # TODO doesn't need to be a QPoint, I think?
    def __init__(
        self, level_view: "LevelView", pos: QPoint, enemy_type=0, index=-1, /, selected=False, auto_scroll_type=0
    ):
        super(AddEnemyAt, self).__init__(None)

        self.view = level_view
        self.level = level_view.level_ref

        self.auto_scroll_type = auto_scroll_type

        # convert here, in case there's a zoom change happening between undo and redo
        self.level_point = level_view.to_level_point(pos)

        self.enemy_type = enemy_type

        self.index = index
        self.was_selected = selected

    def undo(self):
        self.level.enemies.pop(self.index)

        self.level.data_changed.emit()

    def redo(self):
        added_enemy = self.level.add_enemy(self.enemy_type, self.level_point, self.index)
        added_enemy.auto_scroll_type = self.auto_scroll_type
        added_enemy.selected = self.was_selected

        # in case the index was just -1
        self.index = self.level.enemies.index(added_enemy)

        # TODO use level coordinates, possibly by using level directly, instead of level view
        self.setText(f"Add {added_enemy.name} at {added_enemy.x_position}, {added_enemy.y_position}")

        self.level.data_changed.emit()

    def to_data(self) -> list:
        return [
            UndoCommand.MAGIC_VALUE_LEVEL_VIEW,
            self.level_point.xy,
            self.enemy_type,
            self.index,
            self.was_selected,
            self.auto_scroll_type,
        ]

    @classmethod
    def from_data(
        cls,
        level_view: "LevelView",
        xy: tuple[int, int],
        enemy_type: int,
        index: int,
        was_selected: bool,
        auto_scroll_type: int,
    ) -> "UndoCommand":
        command = cls(
            level_view, QPoint(0, 0), enemy_type, index, selected=was_selected, auto_scroll_type=auto_scroll_type
        )
        command.level_point = Position.from_tuple(xy)

        return command


class PasteObjectsAt(UndoCommand):
    def __init__(
        self,
        level_view: "LevelView",
        paste_data: tuple[list[InLevelObject], Position],
        pos: QPoint,
    ):
        super(PasteObjectsAt, self).__init__(None)

        self.view = level_view
        self.paste_data = paste_data

        objects, _ = paste_data

        self.object_count = len(list(filter(lambda obj: isinstance(obj, LevelObject), objects)))
        self.enemy_count = len(objects) - self.object_count

        self.level_point = self.view.to_level_point(pos)

        self.setText(f"Paste {object_names(objects)}")

    def undo(self):
        for _ in range(self.object_count):
            self.view.level_ref.level.objects.pop()

        for _ in range(self.enemy_count):
            self.view.level_ref.level.enemies.pop()

        self.view.level_ref.level.data_changed.emit()

    def redo(self):
        # this will create clones of the cached objects, not paste them with their old graphics (in case of ROM reload)
        self.view.paste_objects_at(self.paste_data, self.level_point)

        self.view.level_ref.level.data_changed.emit()

    def to_data(self) -> list:
        in_between_data: list[tuple] = []

        for obj in self.paste_data[0]:
            if isinstance(obj, LevelObject):
                in_between_data.append((obj.domain, obj.obj_index, obj.length, obj.is_4byte, obj.get_data_position()))
            else:
                in_between_data.append((obj.obj_index, obj.get_position()))

        return [UndoCommand.MAGIC_VALUE_LEVEL_VIEW, in_between_data, self.paste_data[1].xy, self.level_point.xy]

    @classmethod
    def from_data(
        cls,
        level_view: "LevelView",
        in_between_data: list,
        paste_position: tuple[int, int],
        level_point: tuple[int, int],
    ) -> "UndoCommand":
        object_count = 0
        enemy_count = 0

        objects: list[InLevelObject] = []

        dummy_data = bytearray([0, 0, 0])
        dummy_palette_group = PaletteGroup(0, 0, 0, [])
        dummy_graphics_set = GraphicsSet.from_number(1)

        for obj_data in in_between_data:
            if len(obj_data) == 2:
                obj_type, (x, y) = obj_data

                enemy = EnemyItem(dummy_data, QImage(), dummy_palette_group)
                enemy.obj_index = obj_type
                enemy.x_position = x
                enemy.y_position = y

                objects.append(enemy)

                enemy_count += 1

            elif len(obj_data) == 5:
                domain, obj_index, length, is_4_byte, (x, y) = obj_data

                level_object = LevelObject(dummy_data, 1, dummy_palette_group, dummy_graphics_set, [], False, 0)
                level_object.domain = domain
                level_object.obj_index = obj_index
                level_object.length = length
                level_object.is_4byte = is_4_byte
                level_object.rendered_base_x = x
                level_object.rendered_base_y = y

                objects.append(level_object)

                object_count += 1

            else:
                raise ValueError(f"Invalid data length: {len(obj_data)}, '{obj_data}'")

        paste_data = (objects, Position.from_tuple(paste_position))

        command = cls(level_view, paste_data, QPoint(0, 0))

        command.level_point = Position.from_tuple(level_point)

        return command


class RemoveObjects(UndoCommand):
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

    def to_data(self):
        level_object_indexes = [index for index, obj in self.indexes_before_removal if isinstance(obj, LevelObject)]
        enemy_indexes = [index for index, obj in self.indexes_before_removal if isinstance(obj, EnemyItem)]

        return [UndoCommand.MAGIC_VALUE_LEVEL, level_object_indexes, enemy_indexes]

    @classmethod
    def from_data(cls, level: Level, level_object_indexes: list[int], enemy_indexes):
        level_objects = [level.objects[index] for index in level_object_indexes]
        enemy_items = [level.enemies[index] for index in enemy_indexes]

        # explicitly use RemoveObjects here, so inheriting classes don't crash
        command = RemoveObjects(level, level_objects + enemy_items)

        return command


class RemoveObject(RemoveObjects):
    def __init__(self, level: Level, in_level_object: InLevelObject):
        super().__init__(level, [in_level_object])


# Could maybe be replaced by a macro of remove and add object?
class ReplaceLevelObject(UndoCommand):
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
        self.to_replace_index = self.level.objects.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        self.level.objects[self.to_replace_index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        self.to_replace = self.level.objects.pop(self.to_replace_index)

        x, y = self.to_replace.get_position()

        created_object = self.level.add_object(
            self.domain,
            self.obj_type,
            Position.from_xy(x, y),
            self.length,
            self.to_replace_index,
        )

        assert created_object is not None

        created_object.selected = self.to_replace.selected

        self.level.data_changed.emit()

    def id(self):
        return 123

    def mergeWith(self, other):
        if not isinstance(other, ReplaceLevelObject):
            return False

        if self.to_replace_index != other.to_replace_index:
            return False

        self.domain = other.domain
        self.obj_type = other.obj_type
        self.length = other.length

        return True

    def to_data(self) -> list:
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.to_replace_index, self.domain, self.obj_type, self.length]

    @classmethod
    def from_data(cls, level, object_index: int, domain: int, obj_type: int, length: int) -> "UndoCommand":
        level_object = level.objects[object_index]

        return cls(level, level_object, domain, obj_type, length)


class ReplaceEnemy(UndoCommand):
    def __init__(self, level: Level, to_replace: EnemyItem, new_enemy_type: int):
        super(ReplaceEnemy, self).__init__(None)

        self.level = level
        self.new_enemy_type = new_enemy_type

        self.to_replace = to_replace
        self.to_replace_index = self.level.enemies.index(self.to_replace)

        self.setText(f"Replacing {self.to_replace.name}")

    def undo(self):
        self.level.enemies[self.to_replace_index] = self.to_replace

        self.level.data_changed.emit()

    def redo(self):
        self.to_replace = self.level.enemies.pop(self.to_replace_index)

        x, y = self.to_replace.get_position()

        created_enemy = self.level.add_enemy(self.new_enemy_type, Position.from_xy(x, y), self.to_replace_index)

        created_enemy.selected = self.to_replace.selected

        self.level.data_changed.emit()

    def id(self):
        return 122

    def mergeWith(self, other):
        if not isinstance(other, ReplaceEnemy):
            return False

        if self.to_replace_index != other.to_replace_index:
            return False

        self.new_enemy_type = other.new_enemy_type

        return True

    def to_data(self) -> list:
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.to_replace_index, self.new_enemy_type]

    @classmethod
    def from_data(cls, level, enemy_index: int, new_enemy_type: int) -> "UndoCommand":
        enemy = level.enemies[enemy_index]

        return cls(level, enemy, new_enemy_type)


class AddJump(UndoCommand):
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

    def to_data(self) -> list:
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.index, self.jump.data]

    @classmethod
    def from_data(cls, level, index: int, jump_data: bytes) -> "UndoCommand":
        jump = Jump(jump_data)

        return cls(level, jump, index=index)


class RemoveJump(UndoCommand):
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

    def to_data(self) -> list:
        return [UndoCommand.MAGIC_VALUE_LEVEL, self.index]

    @classmethod
    def from_data(cls, level: Level, index: int) -> "UndoCommand":
        return cls(level, index=index)


class UpdatePipeData(UndoCommand):
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

    def to_data(self):
        return [[_pipe_data_to_dict(pipe_data) for pipe_data in self.pipe_data_after]]

    @classmethod
    def from_data(cls, pipe_data_list) -> "UndoCommand":
        current_pipe_data = [PipeData(ROM(), index) for index in range(PIPE_PAIR_COUNT)]

        for pipe_data, pipe_data_dict in zip(current_pipe_data, pipe_data_list):
            for attr, value in pipe_data_dict.items():
                setattr(pipe_data, attr, value)

        return cls(current_pipe_data)


def _pipe_data_to_dict(pipe_data: PipeData) -> dict:
    pipe_dict = {}

    for attr in dir(pipe_data):
        if attr.startswith("_"):
            continue

        if attr == "rom":
            continue

        if callable(getattr(pipe_data, attr)):
            continue

        pipe_dict[attr] = getattr(pipe_data, attr)

    return pipe_dict
