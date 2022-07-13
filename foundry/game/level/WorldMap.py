from typing import Optional

from PySide6.QtCore import QObject, QPoint, QRect, QSize, Signal, SignalInstance

from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import load_palette_group
from foundry.game.gfx.drawable.Block import Block, get_block
from foundry.game.gfx.objects.MapObject import MapObject
from foundry.game.gfx.objects.airship_point import AirshipTravelPoint
from foundry.game.gfx.objects.level_pointer import LevelPointer
from foundry.game.gfx.objects.locks import Lock
from foundry.game.gfx.objects.sprite import Sprite
from foundry.game.level.LevelLike import LevelLike
from smb3parse.data_points import Position
from smb3parse.levels import WORLD_MAP_BLANK_TILE_ID
from smb3parse.levels.world_map import (
    WORLD_MAP_HEIGHT,
    WorldMap as _WorldMap,
    list_world_map_addresses,
)
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET

OVERWORLD_GRAPHIC_SET = 0


class WorldSignaller(QObject):
    needs_redraw: SignalInstance = Signal()
    data_changed: SignalInstance = Signal()
    dimensions_changed: SignalInstance = Signal()
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

        self.size = 0, 0

        self.world = 0

        self.objects: list[MapObject] = []

        self.selected_level_pointers = []
        self.selected_sprites = []

        self._load_objects()
        self._load_sprites()
        self._load_level_pointers()
        self._load_airship_points()
        self._load_locks_and_bridges()

        self._calc_size()

    @property
    def data(self):
        return self.internal_world_map.data

    @staticmethod
    def from_world_number(world_index: int):
        if not 1 <= world_index <= 9:
            raise ValueError(f"World Number of '{world_index} not allowed. Keep it between 1 and 9.")

        return WorldMap(list_world_map_addresses(ROM())[world_index - 1])

    def _load_objects(self):
        self.objects.clear()

        for index, tile in enumerate(self.data.tile_data):
            pos = Position.from_tile_data_index(index)

            block = get_block(tile, self.palette_group, self.graphics_set, self.tsa_data)

            self.objects.append(MapObject(block, pos))

        assert len(self.objects) % WORLD_MAP_HEIGHT == 0

        self._calc_size()

    def _load_sprites(self):
        self.sprites: list[Sprite] = []

        for sprite_data in self.internal_world_map.gen_sprites():
            self.sprites.append(Sprite(sprite_data))

    def _load_level_pointers(self):
        self.level_pointers: list[LevelPointer] = []

        for level_pointer_data in self.internal_world_map.level_pointers:
            self.level_pointers.append(LevelPointer(level_pointer_data))

    def _load_airship_points(self):
        self.airship_travel_sets: list[list[AirshipTravelPoint]] = []

        for airship_travel_set in self.data.airship_travel_sets:
            self.airship_travel_sets.append(
                [AirshipTravelPoint(pos, index) for index, pos in enumerate(airship_travel_set)]
            )

    def _load_locks_and_bridges(self):
        self.locks_and_bridges: list[Lock] = []

        for fortress_fx in self.data.fortress_fx:
            self.locks_and_bridges.append(Lock(fortress_fx))

    def _calc_size(self):
        old_size = self.size

        self.width = len(self.objects) // WORLD_MAP_HEIGHT
        self.height = WORLD_MAP_HEIGHT

        self.size = self.width, self.height

        if self.size != old_size:
            self.dimensions_changed.emit()

    def add_object(self, obj, _):
        self.objects.append(obj)

        self.objects.sort(key=self._array_index)

    def select_level_pointers(self, indexes: list[int]):
        self.selected_level_pointers = indexes
        self._signal_emitter.needs_redraw.emit()

    def move_level_pointers(self, source_index: int, target_index: int):
        if source_index == target_index:
            return

        moved_level_pointer = self.level_pointers.pop(source_index)
        self.level_pointers.insert(target_index, moved_level_pointer)

        for index, level_pointer in enumerate(self.level_pointers):
            level_pointer.data.change_index(index)

    def select_sprites(self, indexes: list[int]):
        self.selected_sprites = indexes
        self._signal_emitter.needs_redraw.emit()

    def move_sprites(self, source_index: int, target_index: int):
        if source_index == target_index:
            return

        moved_sprite = self.sprites.pop(source_index)
        self.sprites.insert(target_index, moved_sprite)

        for index, sprite in enumerate(self.sprites):
            sprite.data.change_index(index)

    def move_tile(self, source_index: int, target_index: int, obj_index: int):
        if source_index == target_index:
            return

        source_obj = self.objects[source_index]
        target_obj = self.objects[target_index]

        target_obj.change_type(obj_index)
        source_obj.change_type(WORLD_MAP_BLANK_TILE_ID)

    @property
    def q_size(self):
        return QSize(*self.size) * Block.SIDE_LENGTH

    @property
    def needs_redraw(self):
        return self._signal_emitter.needs_redraw

    @property
    def dimensions_changed(self):
        return self._signal_emitter.dimensions_changed

    @property
    def data_changed(self):
        return self._signal_emitter.data_changed

    @property
    def jumps_changed(self):
        return self._signal_emitter.jumps_changed

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
            index = obj.pos.tile_data_index

            return_array[index] = obj.to_bytes()

        return self.layout_address, return_array

    def from_bytes(self, data, _=None):
        offset, obj_bytes = data

        self.layout_address = offset
        self._load_objects()

        self._calc_size()

    def get_object(self, index):
        return self.objects[index]

    # TODO: not remove, clear the tile data
    def remove_object(self, obj):
        self.objects.remove(obj)

    def _write_tile_data(self):
        world_data = self.data
        old_tile_data = bytearray([obj.type for obj in sorted(self.objects)])

        if len(world_data.tile_data) < len(old_tile_data):
            world_data.tile_data = old_tile_data[: len(world_data.tile_data)]
        else:
            world_data.tile_data[: len(old_tile_data)] = old_tile_data

    def reread_tiles(self):
        self._write_tile_data()

        self._load_objects()

        self.data_changed.emit()

    def remove_all_tiles(self):
        for obj in self.objects:
            obj.change_type(0xFE)

    def remove_all_sprites(self):
        self.internal_world_map.clear_sprites()
        self.data_changed.emit()

    def remove_all_level_pointers(self):
        self.internal_world_map.clear_level_pointers()
        self.data_changed.emit()

    def level_pointer_at(self, x: int, y: int) -> Optional[LevelPointer]:
        pos = Position.from_xy(x, y)

        for level_pointer in self.level_pointers:
            if level_pointer.data.is_at(pos):
                return level_pointer
        else:
            return None

    def level_name_at_position(self, x: int, y: int) -> str:
        pos = Position.from_xy(x, y)

        return self.internal_world_map.level_name_for_position(pos)

    def sprite_at(self, x, y) -> Optional[Sprite]:
        pos = Position.from_xy(x, y)

        for sprite in self.sprites:
            if sprite.data.is_at(pos):
                return sprite
        else:
            return

    def airship_point_at(self, x, y, airship_travel_set_visibility=0):
        pos = Position.from_xy(x, y)

        for index, airship_travel_set in reversed(list(enumerate(self.airship_travel_sets))):
            if airship_travel_set_visibility & 2**index != 2**index:
                continue

            for airship_point in reversed(airship_travel_set):
                if airship_point.pos == pos:
                    return airship_point

        return None

    def tile_at(self, x, y):
        pos = Position.from_xy(x, y)

        return self.internal_world_map.tile_at(pos)

    def locks_at(self, x, y):
        return None

    def pipe_at(self, x, y):
        return None

    # TODO check if better in parent class
    def get_rect(self, block_length: int = 1):
        width, height = self.size

        return QRect(QPoint(0, 0), QSize(width, height) * block_length)

    @property
    def fully_loaded(self):
        return True

    def save_to_rom(self, rom: Optional[ROM] = None):
        self._write_tile_data()

        self.data.write_back()

        # sprites
        for sprite in self.sprites:
            sprite.data.calculate_addresses()
            sprite.data.write_back()
