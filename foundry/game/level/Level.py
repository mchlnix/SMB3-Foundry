from typing import List, Optional, Tuple, Union

from PySide6.QtCore import QObject, QPoint, QRect, QSize, Signal, SignalInstance

from foundry.game.File import ROM
from foundry.game.ObjectSet import ObjectSet
from foundry.game.gfx.objects import EnemyItem, EnemyItemFactory, Jump, LevelObject, LevelObjectFactory
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.level import LevelByteData, _load_level_offsets
from foundry.game.level.LevelLike import LevelLike
from smb3parse.constants import BASE_OFFSET, Level_TilesetIdx_ByTileset, OFFSET_SIZE
from smb3parse.data_points import Position
from smb3parse.levels import HEADER_LENGTH, OFFSET_BY_OBJECT_SET_A000, WORLD_MAP_LAYOUT_DELIMITER
from smb3parse.levels.level_header import LevelHeader

LEVEL_POINTER_OFFSET = Level_TilesetIdx_ByTileset

ENEMY_SIZE = 3

TIME_INF = -1

LEVEL_DEFAULT_HEIGHT = 27
LEVEL_DEFAULT_WIDTH = 16


def world_and_level_for_level_address(level_address: int):
    for level in Level.offsets[1:]:
        if level.rom_level_offset == level_address:
            return level.game_world, level.level_in_world
    else:
        return -1, -1


class LevelSignaller(QObject):
    needs_redraw: SignalInstance = Signal()
    data_changed: SignalInstance = Signal()
    jumps_changed: SignalInstance = Signal()


class Level(LevelLike):
    MIN_LENGTH = 0x10

    offsets, world_indexes = _load_level_offsets()
    sorted_offsets = sorted(offsets, key=lambda level: level.rom_level_offset)

    WORLDS = len(world_indexes)

    def __init__(
        self, level_name: str = "", layout_address: int = 0, enemy_data_offset: int = 0, object_set_number: int = 1
    ):
        super(Level, self).__init__(object_set_number, layout_address)

        self._signal_emitter = LevelSignaller()

        self.object_set = ObjectSet(object_set_number)

        self.name = level_name
        self.world = 0
        """
        In which world map this level is situated. 0 means don't know. Might not always be known or level might be
        accessible from multiple worlds, so we only set it, if we know.
        """

        self.header_offset = layout_address
        self.object_offset = self.header_offset + HEADER_LENGTH
        self.enemy_offset = enemy_data_offset

        self.objects: List[LevelObject] = []
        self.header_bytes: bytearray = bytearray()
        self.jumps: List[Jump] = []
        self.enemies: List[EnemyItem] = []

        if self.layout_address == self.enemy_offset == 0:
            # probably loaded to become an m3l
            self.size = (0, 0)
            self.header_bytes = bytearray(9)
            self.header = LevelHeader(self.header_bytes, self.object_set.number)
            self.object_factory = None
            self.enemy_factory = None
            return

        rom = ROM()

        self.header_bytes = rom.bulk_read(HEADER_LENGTH, self.header_offset)
        self._parse_header()

        object_data = ROM.rom_data[self.object_offset :]
        enemy_data = ROM.rom_data[self.enemy_offset :]

        self._load_level_data(object_data, enemy_data)

    def _load_level_data(self, object_data: bytearray, enemy_data: bytearray, new_level: bool = True):
        self._load_objects(object_data)
        self._load_enemies(enemy_data)

        if new_level:
            self._update_level_size()

            self.data_changed.emit()

    @property
    def fully_loaded(self):
        """Whether this object represents a fully loaded Level, meaning it was either loaded from a ROM or from an m3l
        file. If this is false, it is probably just a place holder to use either from_bytes or from_m3l later."""
        # objects, enemies and jumps could be empty, but there are always 9 header bytes, when a level is loaded
        return bool(self.header_bytes)

    @property
    def attached_to_rom(self):
        """Whether the current level has a place in the ROM yet. If not this level is likely a m3l file."""
        return not (self.header_offset == self.enemy_offset == 0)

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def needs_redraw(self):
        return self._signal_emitter.needs_redraw

    @property
    def data_changed(self):
        return self._signal_emitter.data_changed

    @property
    def jumps_changed(self):
        return self._signal_emitter.jumps_changed

    def reload(self):
        (_, header_and_object_data), (_, enemy_data) = self.to_bytes()

        self.header_bytes = header_and_object_data[:HEADER_LENGTH]

        object_data = header_and_object_data[HEADER_LENGTH:]

        self._parse_header()
        self._load_level_data(object_data, enemy_data, new_level=False)

        self.data_changed.emit()

    def current_object_size(self):
        size = 0

        for obj in self.objects:
            if obj.is_4byte:
                size += 4
            else:
                size += 3

        size += Jump.SIZE * len(self.jumps)

        return size

    def current_enemies_size(self):
        return len(self.enemies) * ENEMY_SIZE

    def _parse_header(self, should_emit=True):
        self.header = LevelHeader(self.header_bytes, self.object_set_number)

        self.object_factory = LevelObjectFactory(
            self.object_set_number,
            self.header.graphic_set_index,
            self.header.object_palette_index,
            self.objects,
            bool(self.header.is_vertical),
        )
        self.enemy_item_factory = EnemyItemFactory(self.object_set_number, self.header.enemy_palette_index)

        self.size = self.header.width, self.header.height

        if should_emit:
            self.data_changed.emit()

    def _load_enemies(self, data: bytearray):
        self.enemies.clear()

        def data_left(_data: bytearray):
            # the commented out code seems to hold for the stock ROM, but if the ROM was already edited with another
            # editor, it might not, since they only wrote the 0xFF to end the enemy data

            return _data and not _data[0] == 0xFF  # and _data[1] in [0x00, 0x01]

        enemy_data, data = data[0:ENEMY_SIZE], data[ENEMY_SIZE:]

        while data_left(enemy_data):
            enemy = self.enemy_item_factory.from_data(enemy_data, 0)

            self.enemies.append(enemy)

            enemy_data, data = data[0:ENEMY_SIZE], data[ENEMY_SIZE:]

    def _load_objects(self, data: bytearray):
        if self.object_factory is None:
            return

        self.objects.clear()
        self.jumps.clear()

        if not data or data[0] == 0xFF:
            return

        while True:
            obj_data, data = data[0:3], data[3:]

            domain = (obj_data[0] & 0b1110_0000) >> 5

            obj_id = obj_data[2]
            has_length_byte = self.object_set.object_length(domain, obj_id) == 4

            if has_length_byte:
                fourth_byte, data = data[0], data[1:]
                obj_data.append(fourth_byte)

            level_object = self.object_factory.from_data(obj_data, len(self.objects))

            if isinstance(level_object, LevelObject):
                self.objects.append(level_object)
            elif isinstance(level_object, Jump):
                self.jumps.append(level_object)

            if data[0] == 0xFF:
                break

    def _update_level_size(self):
        self.object_size_on_disk = self.current_object_size()
        self.enemy_size_on_disk = self.current_enemies_size()

    @property
    def size_on_disk(self):
        return self.object_size_on_disk + self.enemy_size_on_disk

    def get_rect(self, block_length: int = 1):
        width, height = self.size

        return QRect(QPoint(0, 0), QSize(width, height) * block_length)

    def set_addresses(self, header_offset: int, enemy_item_offset: int):
        self.header_offset = header_offset
        self.object_offset = self.header_offset + HEADER_LENGTH
        self.enemy_offset = enemy_item_offset

    def was_saved(self):
        self._update_level_size()

    @property
    def objects_end(self):
        return (
            self.header_offset + HEADER_LENGTH + self.current_object_size() + len(WORLD_MAP_LAYOUT_DELIMITER)
        )  # the delimiter

    @property
    def enemies_end(self):
        return self.enemy_offset + self.current_enemies_size() + len(b"\xFF\x00")  # the delimiter

    @property
    def next_area_objects(self):
        return self.header.jump_level_address

    @next_area_objects.setter
    def next_area_objects(self, value):
        if value == self.header.jump_level_address:
            return

        value -= LEVEL_POINTER_OFFSET + self.header.jump_object_set.level_offset

        self.header_bytes[0] = 0x00FF & value
        self.header_bytes[1] = value >> 8

        self._parse_header()

    @property
    def has_next_area(self):
        return self.header_bytes[0] + self.header_bytes[1] != 0

    @property
    def next_area_enemies(self):
        return self.header.jump_enemy_address

    @next_area_enemies.setter
    def next_area_enemies(self, value):
        if value == self.header.jump_enemy_address:
            return

        value -= BASE_OFFSET

        self.header_bytes[2] = 0x00FF & value
        self.header_bytes[3] = value >> 8

        self._parse_header()

    @property
    def start_y_index(self):
        return self.header.start_y_index

    @start_y_index.setter
    def start_y_index(self, index):
        if index == self.header.start_y_index:
            return

        self.header_bytes[4] &= 0b0001_1111
        self.header_bytes[4] |= index << 5

        self._parse_header()

    # bit 4 unused

    @property
    def length(self):
        return self.header.length

    @length.setter
    def length(self, length):
        """
        Sets the length of the level in "screens".

        :param length: amount of screens the level should have
        :return:
        """

        if length == self.header.length:
            return

        # screens are 0 indexed, minimum is 1
        self.header_bytes[4] &= 0b1111_0000
        self.header_bytes[4] |= (length // 0x10) - 1

        self._parse_header()

    # bit 1 unused

    @property
    def start_x_index(self):
        return self.header.start_x_index

    @start_x_index.setter
    def start_x_index(self, index):
        if index == self.header.start_x_index:
            return

        self.header_bytes[5] &= 0b1001_1111
        self.header_bytes[5] |= index << 5

        self._parse_header()

    @property
    def enemy_palette_index(self):
        return self.header.enemy_palette_index

    @enemy_palette_index.setter
    def enemy_palette_index(self, index):
        if index == self.header.enemy_palette_index:
            return

        self.header_bytes[5] &= 0b1110_0111
        self.header_bytes[5] |= index << 3

        self._parse_header()

    @property
    def object_palette_index(self):
        return self.header.object_palette_index

    @object_palette_index.setter
    def object_palette_index(self, index):
        if index == self.header.object_palette_index:
            return

        self.header_bytes[5] &= 0b1111_1000
        self.header_bytes[5] |= index

        self._parse_header()

        self.reload()

    @property
    def pipe_ends_level(self):
        return self.header.pipe_ends_level

    @pipe_ends_level.setter
    def pipe_ends_level(self, truth_value):
        if truth_value == self.header.pipe_ends_level:
            return

        self.header_bytes[6] &= 0b0111_1111
        self.header_bytes[6] |= int(not truth_value) << 7

        self._parse_header()

    @property
    def scroll_type(self):
        return self.header.scroll_type_index

    @scroll_type.setter
    def scroll_type(self, index):
        if index == self.header.scroll_type_index:
            return

        self.header_bytes[6] &= 0b1001_1111
        self.header_bytes[6] |= index << 5

        self._parse_header()

    @property
    def is_vertical(self):
        return bool(self.header.is_vertical)

    @is_vertical.setter
    def is_vertical(self, truth_value):
        if truth_value == self.header.is_vertical:
            return

        self.header_bytes[6] &= 0b1110_1111
        self.header_bytes[6] |= int(truth_value) << 4

        self._parse_header()

    @property
    def next_area_object_set(self):
        return self.header.jump_object_set_number

    @next_area_object_set.setter
    def next_area_object_set(self, index):
        if index == self.header.jump_object_set_number:
            return

        self.header_bytes[6] &= 0b1111_0000
        self.header_bytes[6] |= index

        self._parse_header()

    @property
    def start_action(self):
        return self.header.start_action

    @start_action.setter
    def start_action(self, index):
        if index == self.header.start_action:
            return

        self.header_bytes[7] &= 0b0001_1111
        self.header_bytes[7] |= index << 5

        self._parse_header()

    @property
    def graphic_set(self):
        return self.header.graphic_set_index

    @graphic_set.setter
    def graphic_set(self, index):
        if index == self.header.graphic_set_index:
            return

        self.header_bytes[7] &= 0b1110_0000
        self.header_bytes[7] |= index

        self._parse_header()

        self.reload()

    @property
    def time_index(self):
        return self.header.time_index

    @time_index.setter
    def time_index(self, index):
        if index == self.header.time_index:
            return

        self.header_bytes[8] &= 0b0011_1111
        self.header_bytes[8] |= index << 6

        self._parse_header()

    # bit 3 and 4 unused

    @property
    def music_index(self):
        return self.header.music_index

    @music_index.setter
    def music_index(self, index):
        if index == self.header.music_index:
            return

        self.header_bytes[8] &= 0b1111_0000
        self.header_bytes[8] |= index

        self._parse_header()

    def is_too_big(self):
        return self.too_many_level_objects() or self.too_many_enemies_or_items()

    def too_many_level_objects(self):
        return self.current_object_size() > self.object_size_on_disk

    def too_many_enemies_or_items(self):
        return self.current_enemies_size() > self.enemy_size_on_disk

    def get_all_objects(self) -> List[InLevelObject]:
        return self.objects + self.enemies

    def object_at(self, x: int, y: int) -> Optional[InLevelObject]:
        for obj in reversed(self.get_all_objects()):
            if obj.point_in(x, y):
                return obj
        else:
            return None

    def bring_to_foreground(self, objects: List[InLevelObject]):
        for obj in objects:
            intersecting_objects = self.get_intersecting_objects(obj)

            object_currently_in_the_foreground: InLevelObject = intersecting_objects[-1]

            if obj is object_currently_in_the_foreground:
                continue

            if isinstance(obj, LevelObject):
                other_objects = self.objects
            elif isinstance(obj, EnemyItem):
                other_objects = self.enemies
            else:
                raise TypeError(f"How did you select an object of type: {type(obj)}")

            other_objects.remove(obj)

            index = other_objects.index(object_currently_in_the_foreground) + 1

            other_objects.insert(index, obj)

        self.data_changed.emit()

    def bring_to_background(self, level_objects: List[InLevelObject]):
        for obj in level_objects:
            intersecting_objects = self.get_intersecting_objects(obj)

            object_currently_in_the_background: InLevelObject = intersecting_objects[0]

            if obj is object_currently_in_the_background:
                continue

            if isinstance(obj, LevelObject):
                objects = self.objects
            elif isinstance(obj, EnemyItem):
                objects = self.enemies
            else:
                raise TypeError()

            objects.remove(obj)

            index = objects.index(object_currently_in_the_background)

            objects.insert(index, obj)

    def get_intersecting_objects(self, obj: InLevelObject) -> List[InLevelObject]:
        """
        Returns all objects of the same type, that overlap the rectangle of the given object, including itself. The
        objects are in the order, that they appear in, in memory, meaning back to front.

        :param obj: The object to check overlaps for.
        :return:
        """
        if isinstance(obj, LevelObject):
            objects_to_check = self.objects
        elif isinstance(obj, EnemyItem):
            objects_to_check = self.enemies
        else:
            raise TypeError()

        intersecting_objects: List[InLevelObject] = []

        for other_object in objects_to_check:
            if obj.get_rect().intersects(other_object.get_rect()):
                intersecting_objects.append(other_object)

        return intersecting_objects

    def draw(self, *_):
        pass

    def paste_object_at(self, pos: Position, obj: ObjectLike) -> Optional[ObjectLike]:
        if isinstance(obj, EnemyItem):
            return self.add_enemy(obj.obj_index, pos)

        elif isinstance(obj, LevelObject):
            if obj.is_4byte:
                length: Optional[int] = obj.data[3]
            else:
                length = None

            return self.add_object(obj.domain, obj.obj_index, pos, length)

        return None

    def add_object(
        self, domain: int, object_index: int, pos: Position, length: Optional[int], index: int = -1
    ) -> Optional[ObjectLike]:
        if index == -1:
            index = len(self.objects)

        if self.object_factory:
            obj = self.object_factory.from_properties(domain, object_index, *pos.xy, length, index)
            self.objects.insert(index, obj)

            return obj

        return None

    def add_enemy(self, object_index: int, pos: Position, index: int = -1) -> EnemyItem:
        if index == -1:
            index = len(self.enemies)
        else:
            index %= len(self.objects)

        enemy = self.enemy_item_factory.from_data([object_index, *pos.xy], -1)

        self.enemies.insert(index, enemy)

        return enemy

    def index_of(self, obj: InLevelObject) -> int:
        if isinstance(obj, LevelObject):
            return self.objects.index(obj)
        elif isinstance(obj, EnemyItem):
            return len(self.objects) + self.enemies.index(obj)
        else:
            raise TypeError("Given Object was not EnemyObject or LevelObject.")

    def get_object(self, index: int):
        if index < len(self.objects):
            return self.objects[index]
        else:
            return self.enemies[index % len(self.objects)]

    def clear_selection(self):
        for obj in self.get_all_objects():
            obj.selected = False

        self.data_changed.emit()

    def remove_object(self, obj: InLevelObject):
        if obj is None:
            return

        if isinstance(obj, LevelObject):
            self.objects.remove(obj)
        elif isinstance(obj, EnemyItem):
            self.enemies.remove(obj)

    def to_m3l(self) -> bytearray:
        world_number = level_number = 1

        m3l_bytes = bytearray()

        m3l_bytes.append(world_number)
        m3l_bytes.append(level_number)
        m3l_bytes.append(self.object_set_number)

        m3l_bytes.extend(self.header_bytes)

        for obj in self.objects:
            m3l_bytes.extend(obj.to_bytes())

        for jump in self.jumps:
            m3l_bytes.extend(jump.to_bytes())

        # only write 0xFF, even though the stock ROM would use 0xFF00 or 0xFF01
        # this is done to keep compatibility to older editors
        m3l_bytes.append(0xFF)
        m3l_bytes.append(0x01)

        for enemy in sorted(self.enemies, key=lambda _enemy: _enemy.x_position):
            m3l_bytes.extend(enemy.to_bytes())

        m3l_bytes.append(0xFF)

        return m3l_bytes

    def bytes_as_asm(self, data: Union[bytearray, int]) -> str:
        if isinstance(data, int):
            hex_data = f"${data:02X}"
        else:
            assert isinstance(data, bytearray)
            hex_data = ", ".join([f"${byte:02X}" for byte in data])

        return hex_data.replace("0x", "$").upper()

    def to_asm(self) -> str:
        return self._level_asm(), self._enemy_asm()

    def _enemy_asm(self):
        ret_lines: List[str] = []

        ret_lines.append(f"\t.byte {self.bytes_as_asm(1)}\t\t\t; Unused byte, set to $01")

        for enemy in self.enemies:
            ret_lines.append(f"\t.byte {self.bytes_as_asm(enemy.to_bytes())}\t; {enemy.name} @ {enemy.get_position()}")

        return "\n".join(ret_lines)

    def _level_asm(self):
        ret_lines: List[str] = []

        object_set_offset = (ROM().int(OFFSET_BY_OBJECT_SET_A000 + self.object_set.number) * OFFSET_SIZE - 10) * 0x1000

        level_offset = (self.layout_address - BASE_OFFSET - object_set_offset) & 0xFFFF

        ret_lines.append(f"; Original address was ${level_offset:04X}")
        ret_lines.append(f"; {self.name}'s layout data")

        ret_lines.append(f"\t.byte {self.bytes_as_asm(self.header_bytes[0:2])}\t\t\t ; Next Area Layout Offset")
        ret_lines.append(f"\t.byte {self.bytes_as_asm(self.header_bytes[2:4])}\t\t\t ; Next Area Enemy & Item Offset")
        ret_lines.append(
            f"\t.byte {self.bytes_as_asm(self.header_bytes[4])}\t\t\t\t ; Level Size Index | Y-Start Index"
        )
        ret_lines.append(
            f"\t.byte {self.bytes_as_asm(self.header_bytes[5])}\t\t\t\t ; BG Pal | Enemy Pal | X-Start Index | Unused"
        )
        ret_lines.append(
            f"\t.byte {self.bytes_as_asm(self.header_bytes[6])}"
            "\t\t\t\t ; Pipe Ends Level | VScroll Index | Vertical Flag | Next Area Object Set"
        )
        ret_lines.append(
            f"\t.byte {self.bytes_as_asm(self.header_bytes[7])}\t\t\t\t ; Level Entry Action | Graphic Set"
        )
        ret_lines.append(
            f"\t.byte {self.bytes_as_asm(self.header_bytes[8])}\t\t\t\t ; Time Index | Unused | Music Index"
        )
        ret_lines.append("")

        for obj in self.objects + self.jumps:
            if obj.is_4byte:
                indent = ""
            else:
                indent = "\t\t"

            ret_lines.append(f"\t.byte {self.bytes_as_asm(obj.to_bytes())}{indent} ; {obj.name} @ {obj.get_position()}")

        return "\n".join(ret_lines)

    def from_m3l(self, m3l_bytes: bytearray):
        world_number, level_number, self.object_set_number = m3l_bytes[:3]
        self.object_set = ObjectSet(self.object_set_number)

        self.header_offset = self.enemy_offset = 0

        # block signals, so it will only be emitted, once we are fully set up
        self._signal_emitter.blockSignals(True)

        # update the level_object_factory
        self._load_level_data(bytearray(), bytearray(), new_level=False)

        m3l_bytes = m3l_bytes[3:]

        self.header_bytes = m3l_bytes[:HEADER_LENGTH]
        self._parse_header()

        m3l_bytes = m3l_bytes[HEADER_LENGTH:]

        # figure out how many bytes are the objects
        self._load_objects(m3l_bytes)
        object_size = self.current_object_size() + len(WORLD_MAP_LAYOUT_DELIMITER)  # delimiter

        object_bytes = m3l_bytes[:object_size]
        enemy_bytes = m3l_bytes[object_size:]

        if len(enemy_bytes) % 3 - len(WORLD_MAP_LAYOUT_DELIMITER) == 1:
            # compatibility with workshop
            enemy_bytes = enemy_bytes[1:]

        self._signal_emitter.blockSignals(False)

        self._load_level_data(object_bytes, enemy_bytes)

    def save_to_rom(self):
        for offset, data in self.to_bytes():
            ROM().bulk_write(data, offset)

    def to_bytes(self) -> LevelByteData:
        data = bytearray()

        data.extend(self.header_bytes)

        for obj in self.objects:
            data.extend(obj.to_bytes())

        for jump in self.jumps:
            data.extend(jump.to_bytes())

        data.append(0xFF)

        enemies = bytearray()

        if self.is_vertical:
            enemies_objects = sorted(self.enemies, key=lambda _enemy: _enemy.y_position)
        else:
            enemies_objects = sorted(self.enemies, key=lambda _enemy: _enemy.x_position)

        for enemy in enemies_objects:
            enemies.extend(enemy.to_bytes())

        enemies.append(0xFF)

        return (self.header_offset, data), (self.enemy_offset, enemies)

    def from_bytes(self, object_data: Tuple[int, bytearray], enemy_data: Tuple[int, bytearray], new_level=True):

        self.header_offset, object_bytes = object_data
        self.enemy_offset, enemies = enemy_data

        self.header_bytes = object_bytes[0:HEADER_LENGTH]
        objects = object_bytes[HEADER_LENGTH:]

        self._parse_header(should_emit=False)
        self._load_level_data(objects, enemies, new_level)
