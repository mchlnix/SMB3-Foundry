from PySide6.QtCore import QRect

from foundry.game.gfx.objects.ObjectLike import ObjectLike

map_object_names = {
    0x00: "Mario Clear (Blue)",
    0x01: "Luigi Clear (Blue)",
    0x02: "Black Square",
    0x03: "Level 1",
    0x04: "Level 2",
    0x05: "Level 3",
    0x06: "Level 4",
    0x07: "Level 5",
    0x08: "Level 6",
    0x09: "Level 7",
    0x0A: "Level 8",
    0x0B: "Level 9",
    0x0C: "Level 10",
    0x0D: "Level 1 (Broken)",
    0x0E: "Level 2 (Broken)",
    0x0F: "Level 3 (Broken)",
    0x10: "Level 4 (Broken)",
    0x11: "Level 5 (Broken)",
    0x12: "Level 6 (Broken)",
    0x13: "Level 7 (Broken)",
    0x14: "Level 8 (Broken)",
    0x15: "Level 9 (Broken)",
    0x40: "Mario Clear (Orange)",
    0x41: "Luigi Clear (Orange)",
    0x42: "Desert Background",
    0x43: "Sand",
    0x44: "Path Upper Left",
    0x45: "Path Horizontal",
    0x46: "Path Vertical",
    0x47: "Path Upper Right",
    0x48: "Path Lower Left",
    0x49: "Path Horizontal 2",
    0x4A: "Path Lower Right",
    0x4B: "Pier",
    0x4C: "I's",
    0x4D: "Z's",
    0x4E: "? 1",
    0x4F: "? 2",
    0x50: "Mushroom House (Orange)",
    0x51: "Rock 1",
    0x52: "Rock 2",
    0x53: "Rock 3",
    0x54: "Key Door 1",
    0x55: "Star",
    0x56: "Key Door 2",
    0x57: "Miniature Path Lower Right",
    0x58: "Miniature Path Lower Left",
    0x59: "Miniature Path Horizontal",
    0x5A: "Miniature Tower",
    0x5B: "Miniature Path Point Horizontal",
    0x5C: "Miniature Path Lower Left 2",
    0x5D: "Miniature Cacti",
    0x5E: "Miniature Cacti 2",
    0x5F: "Tower",
    0x60: "Fortress Ruins",
    0x61: "Bowsers Castle Wall Tower",
    0x62: "Bowsers Castle Wall Side",
    0x63: "Bowsers Castle Wall Top 1",
    0x64: "Bowsers Castle Wall",
    0x65: "Bowsers Castle Wall Top 2",
    0x66: "Path Upper Right 2",
    0x67: "Fortress",
    0x68: "Quicksand",
    0x69: "Pyramid",
    0x6A: "Barracks",
    0x80: "Mario Clear (Green)",
    0x81: "Luigi Clear (Green)",
    0x82: "Water Three-Way Up",
    0x83: "Water Three-Way Down",
    # TODO continue
    0xB1: "Switchable Bridge Vertical",
    0xB2: "Switchable Bridge Horizontal",
    0xB3: "Round Bridge",
    0xB4: "Bushes",
    # TODO continue
    0xBB: "Palm Tree",
    0xBC: "Pipe",
    0xBD: "Fire Flower",
    0xBE: "Piranha Plant",
    0xBF: "Pond",
    0xC0: "Mario Clear (Red)",
    0xC1: "Luigi Clear (Red)",
    0xC2: "Cloud Upper Left",
    0xC3: "Cloud Top Left",
    0xC4: "Cloud Top Right",
    0xC5: "Cloud Upper Right",
    0xC6: "? 3",
    0xC7: "? 4",
    0xC8: "End Castle Top",
    0xC9: "End Castle Bottom",
    0xCA: "Bowsers Lair Top Left",
    0xCB: "Bowsers Lair Top Right",
    0xCC: "Bowsers Lair Bottom Left",
    0xCD: "Bowsers Lair Bottom Right",
    0xCE: "Cloud Left 1",
    0xCF: "? 5",
    0xD0: "Cloud Diagnoal",
    0xD1: "Flame",
    0xD2: "Cloud Left 2",
    0xD3: "Cloud Bottom",
    0xD4: "Cloud Lower Right",
    0xD5: "I's 2",
    0xD6: "Red Background ?",
    0xD7: "Desert Background 2 ?",
    0xD8: "Black Square",
    0xD9: "Path Upper Left 2",
    0xDA: "Path Horizontal 3",
    0xDB: "Path Vertical 2",
    0xDC: "Path Upper Right 2",
    0xDD: "Path Lower Left 2",
    0xDE: "Path Lower Right 2",
    0xDF: "Tower 2",
    0xE0: "Mushroom House 2",
    0xE1: "Mushroom",
    0xE2: "Skull",
    0xE3: "Fortress Ruins 2",
    0xE4: "Key Door 3",
    0xE5: "Start Field",
    0xE6: "Hand Field",
    0xE7: "? 6",
    0xE8: "Spade Bonus",
    0xE9: "Star 2",
    0xEA: "Rock Alternative",
    0xEB: "Fortress 2",
}


class MapObject(ObjectLike):
    def __init__(self, block, x, y):
        self.x_position = x
        self.y_position = y

        self.block = block

        self.rect = QRect(self.x_position, self.y_position, 1, 1)

        if self.block.index in map_object_names:
            self.name = map_object_names[self.block.index]
        else:
            self.name = str(hex(self.block.index))

        self.selected = False

    def set_position(self, x, y):
        x = int(x)
        y = int(y)

        self.rect = QRect(x, y, 1, 1)

        self.x_position = x
        self.y_position = y

    def get_position(self):
        return self.x_position, self.y_position

    def render(self):
        pass

    def draw(self, dc, block_length, _=None):
        self.block.draw(
            dc,
            self.x_position * block_length,
            self.y_position * block_length,
            block_length=block_length,
            selected=self.selected,
            transparent=False,
        )

    def get_status_info(self):
        return ("x", self.x_position), ("y", self.y_position), ("Block Type", self.name)

    def to_bytes(self):
        return self.block.index

    def move_by(self, dx, dy):
        self.set_position(self.x_position + dx, self.y_position + dy)

    def resize_to(self, x, y):
        return

    def resize_by(self, dx, dy):
        return

    def point_in(self, x, y):
        return self.rect.contains(x, y)

    def change_type(self, new_type):
        pass

    def get_rect(self):
        return self.rect

    def __contains__(self, point):
        pass
