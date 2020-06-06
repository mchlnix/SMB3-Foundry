from typing import Optional

from smb3parse.levels.WorldMapPosition import WorldMapPosition
from smb3parse.levels.world_map import get_all_world_maps
from smb3parse.util.rom import Rom


def find_world_position(rom: Rom, layout_address: int) -> Optional[WorldMapPosition]:
    for world in get_all_world_maps(rom):
        for _level in world.gen_levels():
            if _level.layout_address == layout_address:
                return _level.world_map_position
    else:
        return None
