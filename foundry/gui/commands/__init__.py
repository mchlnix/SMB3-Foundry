from PySide6.QtGui import QUndoCommand

from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.level.Level import Level


class SetLevelAddressData(QUndoCommand):
    def __init__(self, level: Level, header_offset: int, enemy_offset: int, parent=None):
        super(SetLevelAddressData, self).__init__(parent)

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
    def __init__(self, level: Level, header_offset: int, enemy_offset: int, parent=None):
        super(AttachLevelToRom, self).__init__(level, header_offset, enemy_offset, parent)

        self.setText(f"Attach Level to {hex(self.new_header_offset)} and {hex(self.new_enemy_offset)}")


class DetachLevelFromRom(SetLevelAddressData):
    def __init__(self, level: Level, parent=None):
        super(DetachLevelFromRom, self).__init__(level, 0x0, 0x0, parent)

        self.setText("Detach Level from Rom")


class SetLevelAttribute(QUndoCommand):
    def __init__(self, level: Level, name: str, new_value, display_name="", display_value="", parent=None):
        super(SetLevelAttribute, self).__init__(parent)

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
    def __init__(self, level: Level, new_address: int, parent=None):
        super(SetNextAreaObjectAddress, self).__init__(level, "next_area_objects", new_address, parent)

        self.setText(f"Object Address of Next Area to {hex(new_address)}")


class SetNextAreaEnemyAddress(SetLevelAttribute):
    def __init__(self, level: Level, new_address: int, parent=None):
        super(SetNextAreaEnemyAddress, self).__init__(level, "next_area_enemies", new_address, parent)

        self.setText(f"Enemy Address of Next Area to {hex(new_address)}")


class SetNextAreaObjectSet(SetLevelAttribute):
    def __init__(self, level: Level, new_object_set: int, parent=None):
        super(SetNextAreaObjectSet, self).__init__(level, "next_area_object_set", new_object_set, parent)

        self.setText(f"Object Set of Next Area to {OBJECT_SET_NAMES[new_object_set]}")
