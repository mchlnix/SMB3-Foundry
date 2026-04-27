"""Create editable enemy objects from SMB3 enemy-stream data.

This module owns the shared sprite-sheet and palette preparation needed to turn
raw enemy bytes or explicit editor properties into ``EnemyItem`` instances. It
is the factory boundary between serialized enemy data and the richer object
model consumed by selection, rendering, and paste workflows.

See Also
--------
foundry.game.gfx.objects.in_level.enemy_item
    Concrete editor object built by this factory.
foundry.game.gfx.objects.in_level.in_level_object
    Shared contract implemented by the resulting in-level objects.
"""

from PySide6.QtCore import QRect
from PySide6.QtGui import QImage

from foundry import data_dir
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.Palette import load_palette_group

ENEMY_ITEM_SPRITE_SHEET = QImage(str(data_dir.joinpath("gfx.png")))

ENEMY_ITEM_SPRITE_SHEET.convertTo(QImage.Format_RGB888)


class EnemyItemFactory:
    """Create enemy item instances.

    It keeps SMB3 object bytes aligned with editor geometry, rendering, and
    serialization. Callers use it as the boundary between raw enemy-stream
    bytes, shared rendering assets, and the richer ``EnemyItem`` objects that
    the editor can select, move, copy, and save. That boundary is part of the
    editor's consistency contract: ROM decode, paste reconstruction, and
    editor-created enemies should all emerge with the same sprite sheet,
    palette state, and byte interpretation so later rendering and save-back
    behavior stay aligned. The class therefore protects a maintenance-sensitive
    seam: enemy creation rules stay centralized here instead of being
    reimplemented piecemeal in loaders, palette tools, and command code.

    Parameters
    ----------
    object_set : int
        Object set that controls tiles, graphics, or level object behavior.
    palette_index : int, optional
        Palette-group index used for enemy rendering.

    Attributes
    ----------
    definitions : list
        Shared definition cache consulted by enemy parsing helpers.
    graphic_set : int
        Graphic-set identifier paired with this factory's object-set rules.
    object_set : int
        Object set whose enemy tables and rendering rules are in effect.
    palette_group : PaletteGroup
        Palette rows shared by every created ``EnemyItem``.
    png_data : QImage
        Cropped sprite-sheet image used when constructing editor objects.

    Examples
    --------
    Build an editor object directly from three enemy-stream bytes::

        factory = EnemyItemFactory(object_set=0, palette_index=0)
        enemy = factory.from_data(bytearray([0x01, 0x10, 0x20]), 0)

    Notes
    -----
    The factory exists so level loading, paste flows, and "add enemy" tools all
    share the same decode and asset-preparation path. Sprite-sheet slicing and
    palette resolution happen once here, and every resulting ``EnemyItem``
    inherits that same rendering context. That architectural constraint matters
    because ROM decode, paste reconstruction, and editor-created enemies all
    need to produce objects that render, move, and serialize the same way even
    when they entered the editor through different workflows. In practice, this
    class is the place that keeps "enemy bytes became an editor object" stable
    across all entry points, so future creation flows should be routed through
    it instead of reconstructing ``EnemyItem`` state ad hoc.
    """

    object_set: int
    graphic_set: int

    definitions: list = []

    def __init__(self, object_set: int, palette_index: int = 0):
        """Prepare shared rendering inputs for enemy-item creation.

        The factory slices the enemy/item sprite sheet once and loads the
        matching palette group once, so later conversions from bytes or
        explicit properties can build ``EnemyItem`` instances without
        reloading shared assets.

        Parameters
        ----------
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        palette_index : int, optional
            Palette-group index used for enemy rendering.
        """
        rows_per_object_set = 256 // 64

        y_offset = 12 * rows_per_object_set * Block.HEIGHT

        self.png_data = ENEMY_ITEM_SPRITE_SHEET.copy(
            QRect(
                0,
                y_offset,
                ENEMY_ITEM_SPRITE_SHEET.width(),
                ENEMY_ITEM_SPRITE_SHEET.height() - y_offset,
            )
        )

        self.palette_group = load_palette_group(object_set, palette_index)

    def from_data(self, data: bytearray, _: int):
        """Create an enemy item from encoded enemy-stream bytes.

        This is the decode boundary used by level loading and paste workflows:
        once the shared sprite sheet and palette state are prepared, the method
        turns one serialized enemy record into the richer editor object model.

        Parameters
        ----------
        data : bytearray
            Three-byte enemy or item record from the level enemy stream.
        _ : int
            Unused compatibility argument from shared factory callers.

        Returns
        -------
        EnemyItem
            Enemy item decoded from the supplied bytes.
        """
        return EnemyItem(data, self.png_data, self.palette_group)

    def from_properties(self, enemy_item_id: int, x: int = 0, y: int = 0):
        """Create an enemy item from explicit editor properties.

        This helper mirrors the editor path where a palette-selected enemy type
        and coordinates must be packed into temporary bytes before reusing the
        normal enemy decode workflow.

        Parameters
        ----------
        enemy_item_id : int
            Identifier of the enemy item.
        x : int, optional
            Horizontal coordinate.
        y : int, optional
            Vertical coordinate.

        Returns
        -------
        EnemyItem
            Enemy item built from the supplied type and coordinates.
        """
        data = bytearray(3)

        data[0] = enemy_item_id
        data[1] = x
        data[2] = y

        obj = self.from_data(data, 0)

        return obj
