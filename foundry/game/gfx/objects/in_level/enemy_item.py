"""Model SMB3 enemy-stream records as editable Foundry objects.

This module adapts the separate SMB3 enemy/item byte stream into the same
selection, movement, rendering, and serialization workflow used by in-level
terrain objects. It is the bridge between compact enemy bytes, object-set
metadata, and the sprite-sheet previews that Foundry shows in lists and level
views.

See Also
--------
foundry.game.gfx.objects.in_level.enemy_item_factory
    Builds ``EnemyItem`` instances from bytes or explicit editor properties.
foundry.game.gfx.objects.in_level.in_level_object
    Defines the shared editor-facing contract for in-level objects.
"""

from PySide6.QtCore import QRect
from PySide6.QtGui import QImage

from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.ObjectDefinitions import (
    enemy_handle_x,
    enemy_handle_x2,
    enemy_handle_y,
)
from foundry.game.ObjectSet import ObjectSet
from smb3parse.constants import (
    ENEMY_ITEM_GRAPHICS_SET,
    ENEMY_ITEM_OBJECT_SET,
    OBJ_AUTOSCROLL,
    OBJ_BOOMBOOM,
    OBJ_FLYING_BOOMBOOM,
)
from smb3parse.util.rect import Rect


# TODO Get Qt code out of here
class EnemyItem(InLevelObject):
    """Represent an editable enemy or item entry in a level.

    Enemy and item data is stored separately from level object data in SMB3. This class keeps the
    encoded enemy bytes, editor position, object metadata, and preview blocks aligned for editing,
    drawing, and saving.

    Parameters
    ----------
    data : bytearray
        Three-byte enemy or item record read from level enemy data.
    png_data : QImage
        Sprite sheet image used to copy preview blocks for the enemy or item.
    palette_group : PaletteGroup
        Palette group used for drawing the object.

    Attributes
    ----------
    auto_scroll_type : int
        Encoded auto-scroll command value for autoscroll pseudo-enemies.
    data : bytearray
        Current encoded enemy or item bytes.
    domain : int
        Object domain used by shared level-object interfaces.
    graphics_set : GraphicsSet
        Enemy graphics set used for preview rendering.
    is_4byte : bool
        Whether this entry uses the four-byte level-object format.
    is_fixed : bool
        Whether the entry has fixed dimensions for editing.
    length : int
        Length value exposed through shared object interfaces.
    lock_index : int
        Boom Boom lock index encoded into the enemy Y byte.
    obj_index : int
        Enemy or item type identifier.
    object_set : ObjectSet
        Enemy/item object set used to resolve object definitions.
    palette_group : PaletteGroup
        Palette group used when drawing the entry.
    png_data : QImage
        Sprite sheet image used to slice preview blocks.
    rendered_height : int
        Preview height resolved from the enemy definition.
    rendered_width : int
        Preview width resolved from the enemy definition.
    selected : bool
        Whether the entry is currently selected in the editor.
    height : int
        Logical editor height resolved from the enemy definition.
    width : int
        Logical editor width resolved from the enemy definition.

    Notes
    -----
    Enemy items start as three encoded bytes, then ``_setup`` resolves them
    into editor-facing metadata such as display name, dimensions, hit-test
    rectangle, and preview blocks. Special cases like autoscroll and Boom Boom
    locks are decoded before that shared setup step.

    Examples
    --------
    Decode one enemy record into the editor-facing object used by selection and
    preview code::

        enemy = EnemyItem(data, sprite_sheet, palette_group)
        status = enemy.get_status_info()
    """

    def __init__(self, data, png_data: QImage, palette_group: PaletteGroup):
        """Initialize an enemy or item from encoded level data.

        Initialization decodes special cases such as Boom Boom locks and
        autoscroll commands before resolving object definitions and preview
        blocks. The constructor therefore bridges from the three-byte SMB3
        record into the richer editor object that movement, selection, and
        preview code work with. It also establishes the initial editor state
        and serialization boundary that later move, type-change, and save
        workflows reuse.

        Parameters
        ----------
        data : bytearray
            Three-byte enemy or item record read from level enemy data.
        png_data : QImage
            Sprite sheet image used to copy preview blocks.
        palette_group : PaletteGroup
            Palette group used for drawing the object.
        """
        super(EnemyItem, self).__init__()

        self.data = data

        self.is_4byte = False
        self.is_fixed = True
        self.length = 0

        self.obj_index = data[0]

        # boom boom specific
        if self._is_boom_boom():
            # lock index is encoded in high nibble of the y-position
            self.lock_index = max((data[2] >> 4) - 1, 0)
        else:
            self.lock_index = 0

        if self.obj_index == OBJ_AUTOSCROLL:
            self.auto_scroll_type = data[2]
            data[2] = 0
        else:
            self.auto_scroll_type = 0

        x = data[1] - enemy_handle_x2[self.obj_index]
        y = data[2] - self.lock_index * 0x10

        self.set_position(x, y)

        self.domain = 0

        self.graphics_set = GraphicsSet.from_number(ENEMY_ITEM_GRAPHICS_SET)
        self.palette_group = palette_group

        self.object_set = ObjectSet.from_number(ENEMY_ITEM_OBJECT_SET)

        self.png_data = png_data

        self.selected = False

        self._setup()

    @property
    def rect(self):
        """Describe the hit-test rectangle currently occupied by the enemy.

        Enemy handle offsets are included so hit testing follows the same
        editor-space rectangle that drawing and selection use.

        Returns
        -------
        Rect
            Rectangle containing the enemy in level coordinates.
        """
        return Rect(
            self.x_position + enemy_handle_x[self.obj_index],
            self.y_position + enemy_handle_y[self.obj_index],
            self.width,
            self.height,
        )

    @rect.setter
    def rect(self, value):
        """Update the enemy position from an editor rectangle.

        The rectangle setter keeps shared object-editing code working with enemies even though enemy
        data only stores a point and type-specific dimensions.

        Parameters
        ----------
        value : Rect
            Rectangle whose origin becomes the enemy position.
        """
        self.set_position(value.x, value.y)
        self.length = value.width
        self.width = value.height

    def _setup(self):
        """Resolve object metadata and preview blocks.

        This refreshes the display name, dimensions, and block images after initialization or a type
        change.
        """
        obj_def = self.object_set.get_definition_of(self.obj_index)

        self.name = obj_def.description

        self.width = self.rendered_width = obj_def.bmp_width
        self.height = self.rendered_height = obj_def.bmp_height

        self._render(obj_def)

    def _render(self, obj_def):
        """Copy preview blocks for the enemy definition.

        Enemy previews are sliced from the sprite sheet according to the block indexes supplied by
        the object definition.

        Parameters
        ----------
        obj_def : ObjectDefinition
            Object definition used to configure the object.
        """
        self.blocks = []

        block_ids = obj_def.block_indexes

        for block_id in block_ids:
            x = (block_id % 64) * Block.WIDTH
            y = (block_id // 64) * Block.WIDTH

            self.blocks.append(self.png_data.copy(QRect(x, y, Block.WIDTH, Block.HEIGHT)))

    def copy(self):
        """Create a copy of this enemy or item.

        The copy is rebuilt from serialized bytes so undo/redo and paste operations preserve the
        same encoded state.

        Returns
        -------
        EnemyItem
            Copied enemy or item with the same encoded state.
        """
        return EnemyItem(self.to_bytes(), self.png_data, self.palette_group)

    def render(self):
        # nothing to re-render since enemies are just copied over
        """Leave cached enemy preview blocks unchanged.

        Enemy and item blocks are copied from the sprite sheet during setup, so drawing does not
        need a later render pass.
        """
        pass

    def get_status_info(self):
        """Provide status-bar fields for the selected enemy entry.

        The GUI uses these values to show the selected entry name and level coordinates.

        Returns
        -------
        list[tuple[str, str | int]]
            Label/value pairs for status display.
        """
        return [("Name", self.name), ("X", self.x_position), ("Y", self.y_position)]

    def set_position(self, x, y):
        # todo also check for the upper bounds (difficult, since we don't have the level size here)
        """Reposition the enemy and refresh its serialized byte state.

        Coordinates are clamped to the lower bounds, and autoscroll entries keep
        their Y position fixed because their Y byte stores the scroll type
        instead. Updating the position also refreshes the encoded enemy bytes,
        so drag operations keep editor state and serialized enemy data aligned.

        Parameters
        ----------
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.
        """
        x = max(0, x)
        y = max(0, y)

        if self._is_auto_scroll():
            y = 0

        self.x_position = x
        self.y_position = y

        self.data = self.to_bytes()

    def move_by(self, dx, dy):
        """Apply a drag-style offset to the enemy and refresh encoded bytes.

        Movement delegates through ``set_position`` so encoded bytes and
        special-case enemy rules stay synchronized with the editor-visible
        position. This keeps drag workflow state aligned with the byte payload
        that undo, save, and paste paths later consume.

        Parameters
        ----------
        dx : int
            Horizontal offset.
        dy : int
            Vertical offset.
        """
        new_x = self.x_position + dx
        new_y = self.y_position + dy

        self.set_position(new_x, new_y)

    def get_position(self):
        """Report the editor position used for drawing and serialization.

        Callers use this shared object API when moving or selecting mixed level objects and enemies.

        Returns
        -------
        tuple[int, int]
            X and Y coordinates that the editor uses for hit testing, movement,
            and byte updates.
        """
        return self.x_position, self.y_position

    def resize_by(self, dx, dy):
        """Ignore resize requests because enemy records do not store size state.

        Enemy and item entries do not encode editor-controlled dimensions, so
        resize operations are intentionally a no-op for both preview geometry
        and serialized bytes.

        Parameters
        ----------
        dx : int
            Horizontal offset.
        dy : int
            Vertical offset.
        """
        pass

    @property
    def type(self):
        """Expose the encoded enemy type that drives definition lookup.

        The type identifier is the first byte of the encoded enemy record and
        the lookup key that ties editor state to definitions, previews, and
        serialization behavior.

        Returns
        -------
        int
            Enemy or item type identifier used for metadata lookup, preview
            selection, and serialization.
        """
        return self.obj_index

    @type.setter
    def type(self, value):
        """Store the enemy or item type identifier.

        This setter updates the identifier only; callers that need dimensions and preview blocks
        refreshed should use ``change_type``.

        Parameters
        ----------
        value : int
            Enemy or item type identifier.
        """
        self.obj_index = value

    def change_type(self, new_type):
        """Change the enemy type and refresh metadata.

        The setup pass reloads dimensions, display name, and preview blocks for the new type.

        Parameters
        ----------
        new_type : int
            Replacement type identifier.
        """
        self.obj_index = new_type

        self._setup()

    def increment_type(self):
        """Advance to the next enemy or item type.

        The type is clamped to the byte range and serialized back into the enemy data.
        """
        self.obj_index = min(0xFF, self.obj_index + 1)

        self._setup()
        self.data = self.to_bytes()

    def decrement_type(self):
        """Move to the previous enemy or item type.

        The type is clamped to the byte range and serialized back into the enemy data.
        """
        self.obj_index = max(0, self.obj_index - 1)

        self._setup()
        self.data = self.to_bytes()

    def to_bytes(self):
        """Serialize the enemy or item to level enemy data.

        Serialization reapplies handle offsets and special encodings for Boom Boom locks and
        autoscroll commands.

        Returns
        -------
        bytearray
            Three-byte enemy or item record.

        Examples
        --------
        The serialized X byte stores the editor position plus the type-specific
        handle offset, while the Y byte keeps the editor-visible coordinate for
        ordinary enemies:

        >>> enemy = EnemyItem.__new__(EnemyItem)
        >>> enemy.obj_index = 0
        >>> enemy.x_position = 5
        >>> enemy.y_position = 7
        >>> enemy.lock_index = 0
        >>> enemy.auto_scroll_type = 0
        >>> payload = enemy.to_bytes()
        >>> payload[0] == enemy.obj_index
        True
        >>> payload[1] == enemy.x_position + int(enemy_handle_x2[enemy.obj_index])
        True
        >>> payload[2]
        7
        """
        y_position = self.y_position

        if self._is_boom_boom():
            y_position += 0x10 * self.lock_index
        elif self._is_auto_scroll():
            y_position = self.auto_scroll_type

        return bytearray(
            [
                self.obj_index,
                self.x_position + int(enemy_handle_x2[self.obj_index]),
                y_position,
            ]
        )

    def __str__(self):
        """Summarize this enemy for list widgets and debug output.

        The string includes the display name and level coordinates for list and debug output.

        Returns
        -------
        str
            String representation of the object that reflects the decoded
            decoded state.
        """
        return f"{self.name} at {self.x_position}, {self.y_position}"

    def __repr__(self):
        """Summarize encoded enemy state for debugging and logging.

        The representation identifies the value as an enemy object while reusing the user-facing
        description.

        Returns
        -------
        str
            Developer-facing representation of the object, including the
            byte-backed position and type state.
        """
        return f"EnemyObject: {self}"

    def _is_boom_boom(self):
        """Identify whether this enemy uses the Boom Boom lock-state workflow.

        Boom Boom variants encode lock information in the high nibble of the Y
        byte, so this check gates the special-case decoding used during
        initialization and serialization.

        Returns
        -------
        bool
            True when the entry is a Boom Boom or flying Boom Boom.
        """
        return self.type in [OBJ_BOOMBOOM, OBJ_FLYING_BOOMBOOM]

    def _is_auto_scroll(self):
        """Check whether the encoded enemy is an autoscroll command.

        Autoscroll entries use the Y byte as a scroll type rather than as a level coordinate.

        Returns
        -------
        bool
            True when the entry stores an autoscroll command.
        """
        return self.type == OBJ_AUTOSCROLL
