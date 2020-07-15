from typing import List
import numpy as np

from foundry.game.gfx.GraphicsPage import GraphicsPage
from foundry.game.gfx.drawable.Tile import Tile


class Sprite(Tile):
    """Represents sprites inside the game"""
    image_length = 0x08
    image_height = 0x10

    def __init__(self, pixels: bytes) -> None:
        super().__init__(pixels=pixels)

    @classmethod
    def from_attributes(
            cls,
            sprite_index: int,
            palette_group: List[List[int]],
            graphics_set: GraphicsPage,
            palette_index: int
    ):
        """Returns a block directly from rom"""
        image = np.empty((Sprite.image_length, Sprite.image_length * 3), dtype="ubyte")
        tile_offset = 2 * (sprite_index // 2)
        for idx in range(2):
            tile = Tile.from_rom(tile_offset + idx, palette_group, palette_index, graphics_set)
            y_off = idx * Tile.image_height
            image[y_off:y_off + Tile.image_height, 0:3 * Tile.image_length] = tile.numpy_image
        return cls(bytes(image.flatten().tolist()))
