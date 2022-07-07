from typing import Optional

from PySide6.QtCore import QObject, QPoint, QRect, QSize, Signal, SignalInstance

from foundry.game.File import ROM
from foundry.game.gfx.Palette import load_palette_group
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.drawable.Block import Block, get_block
from foundry.game.gfx.objects.MapObject import MapObject
from foundry.game.gfx.objects.level_pointer import LevelPointer
from foundry.game.gfx.objects.sprite import Sprite
from foundry.game.level.LevelLike import LevelLike
from smb3parse.levels.world_map import (
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
    WorldMap as _WorldMap,
    list_world_map_addresses,
)
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET

OVERWORLD_GRAPHIC_SET = 0


class WorldSignaller(QObject):
    needs_redraw: SignalInstance = Signal()
    data_changed: SignalInstance = Signal()
    jumps_changed: SignalInstance = Signal()


class WorldMap(LevelLike):
    def __init__(self, layout_address):
        self.internal_world_map = _WorldMap(layout_address, ROM())

        super(WorldMap, self).__init__(0, self.internal_world_map.layout_address)

        self.name = f"World @ {layout_address} - Overworld"
        self._signal_emitter = WorldSignaller()

        self.graphics_set = GraphicsSet(OVERWORLD_GRAPHIC_SET)
        self.palette_group = load_palette_group(WORLD_MAP_OBJECT_SET, 0)

        self.object_set = WORLD_MAP_OBJECT_SET
        self.tsa_data = ROM.get_tsa_data(self.object_set)

        self.world = 0

        self.objects = []

        self.selected_level_pointers = []
        self.selected_sprites = []

        self._load_objects()

        self._calc_size()

    @staticmethod
    def from_world_number(world_index: int):
        if not 1 <= world_index <= 9:
            raise ValueError(f"World Number of '{world_index} not allowed. Keep it between 1 and 9.")

        return WorldMap(list_world_map_addresses(ROM())[world_index - 1])

    def _load_objects(self):
        self.remove_all_tiles()

        for index, world_position in enumerate(self.internal_world_map.gen_positions()):
            screen_offset = (index // WORLD_MAP_SCREEN_SIZE) * WORLD_MAP_SCREEN_WIDTH

            x = screen_offset + (index % WORLD_MAP_SCREEN_WIDTH)
            y = (index // WORLD_MAP_SCREEN_WIDTH) % WORLD_MAP_HEIGHT

            block = get_block(world_position.tile(), self.palette_group, self.graphics_set, self.tsa_data)

            self.objects.append(MapObject(block, x, y))

        assert len(self.objects) % WORLD_MAP_HEIGHT == 0

        self.sprites: list[Sprite] = []

        for sprite_data in self.internal_world_map.gen_sprites():
            self.sprites.append(Sprite(sprite_data))

        self.level_pointers: list[LevelPointer] = []

        for level_pointer_data in self.internal_world_map.level_pointers:
            self.level_pointers.append(LevelPointer(level_pointer_data))

    def _calc_size(self):
        self.width = len(self.objects) // WORLD_MAP_HEIGHT
        self.height = WORLD_MAP_HEIGHT

        self.size = self.width, self.height

    def add_object(self, obj, _):
        self.objects.append(obj)

        self.objects.sort(key=self._array_index)

    def select_level_pointers(self, indexes: list[int]):
        self.selected_level_pointers = indexes
        self._signal_emitter.needs_redraw.emit()

    def select_sprites(self, indexes: list[int]):
        self.selected_sprites = indexes
        self._signal_emitter.needs_redraw.emit()

    @property
    def q_size(self):
        return QSize(*self.size) * Block.SIDE_LENGTH

    @staticmethod
    def _array_index(obj):
        return obj.y_position * WORLD_MAP_SCREEN_WIDTH + obj.x_position

    @property
    def needs_redraw(self):
        return self._signal_emitter.needs_redraw

    @property
    def data_changed(self):
        return self._signal_emitter.data_changed

    @property
    def jumps_changed(self):
        return self._signal_emitter.jumps_changed

    def get_object_names(self):
        return [obj.name for obj in self.objects]

    def draw(self, dc, zoom, transparency=None, show_expansion=None):
        for obj in self.objects:
            obj.draw(dc, Block.SIDE_LENGTH * zoom, transparency)

    def index_of(self, obj):
        return self.objects.index(obj)

    def get_all_objects(self):
        return self.objects

    def object_at(self, x, y):
        point = QPoint(x, y)

        for obj in reversed(self.objects):
            if obj.rect.contains(point):
                return obj

        return None

    def to_bytes(self):
        return_array = bytearray(len(self.objects))

        for obj in self.objects:
            index = self._array_index(obj)

            return_array[index] = obj.to_bytes()

        return self.layout_address, return_array

    def from_bytes(self, data, _=None):
        offset, obj_bytes = data

        self.layout_address = offset
        self._load_objects()

        self._calc_size()

    def get_object(self, index):
        return self.objects[index]

    def remove_object(self, obj):
        self.objects.remove(obj)

    def remove_all_tiles(self):
        self.objects.clear()

    def remove_all_sprites(self):
        self.internal_world_map.clear_sprites()
        self.data_changed.emit()

    def remove_all_level_pointers(self):
        self.internal_world_map.clear_level_pointers()
        self.data_changed.emit()

    def level_at_position(self, x: int, y: int) -> Optional[LevelPointer]:
        screen = x // WORLD_MAP_SCREEN_WIDTH + 1

        x %= WORLD_MAP_SCREEN_WIDTH

        for level_pointer in self.level_pointers:
            if level_pointer.data.is_at(screen, y, x):
                return level_pointer
        else:
            return None

    def level_name_at_position(self, x: int, y: int) -> str:
        screen = x // WORLD_MAP_SCREEN_WIDTH + 1

        x %= WORLD_MAP_SCREEN_WIDTH

        return self.internal_world_map.level_name_for_position(screen, y, x)

    def sprite_at_position(self, x, y) -> Optional[Sprite]:
        screen = x // WORLD_MAP_SCREEN_WIDTH + 1

        x %= WORLD_MAP_SCREEN_WIDTH

        for sprite in self.sprites:
            if sprite.data.is_at(screen, y, x):
                return sprite
        else:
            return None

    def tile_at(self, x, y):
        screen = x // WORLD_MAP_SCREEN_WIDTH + 1

        x %= WORLD_MAP_SCREEN_WIDTH

        return self.internal_world_map.tile_at(screen, y, x)

    # TODO check if better in parent class
    def get_rect(self, block_length: int = 1):
        width, height = self.size

        return QRect(QPoint(0, 0), QSize(width, height) * block_length)

    @property
    def fully_loaded(self):
        return True

    def save_to_rom(self, rom: Optional[ROM] = None):
        if rom is None:
            rom = ROM()

        # tiles
        rom.bulk_write(bytearray(map_object.to_bytes() for map_object in self.objects), self.layout_address)

        # sprites
        for sprite in self.sprites:
            sprite.data.write_back()

        # level pointers
        for level_pointer in sorted(self.level_pointers):
            level_pointer.data.write_back()
