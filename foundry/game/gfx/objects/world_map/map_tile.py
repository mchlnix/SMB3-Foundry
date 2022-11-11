from foundry.game.gfx.drawable.Block import Block, get_worldmap_tile
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.constants import TILE_NAMES
from smb3parse.data_points import Position
from smb3parse.levels import WORLD_MAP_SCREEN_SIZE, WORLD_MAP_SCREEN_WIDTH


class MapTile(MapObject):
    def __init__(self, block: Block, pos: Position):
        super(MapTile, self).__init__()

        self.pos = pos

        self.block = block
        self.type = self.block.index

    @property
    def name(self):
        if self.type in TILE_NAMES:
            name = TILE_NAMES[self.type]
        else:
            name = str(hex(self.type))

        return name

    @name.setter
    def name(self, value):
        pass

    def copy(self):
        return MapTile(self.block, self.pos.copy())

    def draw(self, dc, block_length, _=None, anim_frame=0):
        self.block.graphics_set.anim_frame = anim_frame

        self.block.rerender()

        self.block.draw(
            dc,
            self.x_position * block_length,
            self.y_position * block_length,
            block_length=block_length,
            selected=self.selected,
            transparent=False,
        )

    def set_position(self, x, y):
        self.pos = Position.from_xy(x, y)

    def get_position(self) -> tuple[int, int]:
        return self.pos.xy

    def change_type(self, new_type):
        self.block = get_worldmap_tile(new_type, self.block.palette_group.index)

        self.type = self.block.index

        if self.type in TILE_NAMES:
            self.name = TILE_NAMES[self.type]
        else:
            self.name = str(hex(self.type))

    def __lt__(self, other):
        screen = self.x_position // WORLD_MAP_SCREEN_WIDTH
        x = self.x_position % WORLD_MAP_SCREEN_WIDTH
        y = self.y_position

        result = screen * WORLD_MAP_SCREEN_SIZE + y * WORLD_MAP_SCREEN_WIDTH + x

        screen = other.x_position // WORLD_MAP_SCREEN_WIDTH
        x = other.x_position % WORLD_MAP_SCREEN_WIDTH
        y = other.y_position

        other_result = screen * WORLD_MAP_SCREEN_SIZE + y * WORLD_MAP_SCREEN_WIDTH + x

        return result < other_result

    def __repr__(self):
        return f"MapTile #{self.type:#x}: '{self.name}' at {self.x_position}, {self.y_position}"
