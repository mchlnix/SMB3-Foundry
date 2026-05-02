"""Build editor-facing level objects from SMB3 object data or form inputs.

This module owns the small conversion layer between compact level-object bytes
and the richer ``LevelObject`` or ``Jump`` instances used by Foundry's lists,
views, and edit commands. It keeps object-set, graphics-set, palette, and
level-orientation state together so repeated decode and creation workflows do
not have to reassemble rendering context each time.

See Also
--------
foundry.game.gfx.objects.in_level.level_object
    Concrete terrain-object model created by this factory.
foundry.game.gfx.objects.in_level.jump
    Jump-pointer model returned when the incoming bytes use the jump domain.
"""

from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.Palette import PaletteGroup, load_palette_group
from smb3parse.levels import LEVEL_SCREEN_HEIGHT, LEVEL_SCREEN_WIDTH
from smb3parse.util import clamp


class LevelObjectFactory:
    """Create level object instances.

    It keeps SMB3 object bytes aligned with editor geometry, rendering, and serialization. Callers use it as the boundary between raw object bytes, editable geometry, and rendered blocks.

    Parameters
    ----------
    object_set : int
        Object set that controls tiles, graphics, or level object behavior.
    graphic_set : int
        Graphics set used to draw object previews.
    palette_group_index : int
        Index of the palette group.
    objects_ref : list[LevelObject]
        Sibling level objects used for rendering and expansion checks.
    vertical_level : bool
        Whether the level uses vertical orientation.
    size_minimal : bool, optional
        Whether object sizes should use minimal bounds.

    Attributes
    ----------
    graphic_set : int
        Graphic set used for level-object parsing, rendering, or serialization.
    graphics_set : GraphicsSet | None
        Graphics set used for level-object parsing, rendering, or serialization.
    object_set : int
        Object set used for level-object parsing, rendering, or serialization.
    objects_ref : Any
        Sibling level objects used for expansion checks and renderer context.
    palette_group : PaletteGroup
        Palette group used for level-object parsing, rendering, or serialization.
    palette_group_index : int
        Palette group index used for level-object parsing, rendering, or serialization.
    size_minimal : Any
        Size minimal used for level-object parsing, rendering, or serialization.
    vertical_level : Any
        Vertical level used for level-object parsing, rendering, or serialization.

    Examples
    --------
    Decode one serialized level-object record with the shared rendering
    context, then reuse the same factory for a property-driven create path::

        factory = LevelObjectFactory(1, 0, 0, objects_ref=[], vertical_level=False)
        decoded = factory.from_data(bytearray([0x00, 0x10, 0x20]), 0)
        created = factory.from_properties(0, 0x20, x=0x10, y=0x00, length=None, index=1)

    Both paths return editor-facing objects that already carry the shared
    object-set, graphics-set, palette, and sibling-object context needed for
    rendering and later serialization.
    """

    object_set: int
    graphic_set: int
    palette_group_index: int

    graphics_set: GraphicsSet | None = None
    palette_group: PaletteGroup

    def __init__(
        self,
        object_set: int,
        graphic_set: int,
        palette_group_index: int,
        objects_ref: list[LevelObject],
        vertical_level: bool,
        size_minimal: bool = False,
    ):
        """Capture the shared decode and render context for level objects.

        Initialization stores the object-set, graphics-set, palette, sibling
        object list, and level-orientation state that later decode and create
        operations reuse. That keeps the conversion workflow focused on one
        object at a time instead of rebuilding shared render context for every
        object record.

        Parameters
        ----------
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        graphic_set : int
            Graphics set used to draw object previews.
        palette_group_index : int
            Index of the palette group.
        objects_ref : list[LevelObject]
            Sibling level objects used for rendering and expansion checks.
        vertical_level : bool
            Whether the level uses vertical orientation.
        size_minimal : bool, optional
            Whether object sizes should use minimal bounds.
        """
        self.set_object_set(object_set)
        self.set_graphic_set(graphic_set)
        self.set_palette_group_index(palette_group_index)
        self.objects_ref = objects_ref
        self.vertical_level = vertical_level

        self.size_minimal = size_minimal

    def set_object_set(self, object_set: int):
        """Update the object-set state used by later decode operations.

        The factory keeps this state so later object creation can resolve the
        correct definitions, palettes, and render behavior without rebuilding
        the rest of the shared context.

        Parameters
        ----------
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        """
        self.object_set = object_set

    def set_graphic_set(self, graphic_set: int):
        """Update the graphics-set state used by later decode operations.

        Changing the graphics set also refreshes the cached ``GraphicsSet``
        instance that later ``LevelObject`` creation reuses during preview and
        render setup.

        Parameters
        ----------
        graphic_set : int
            Graphics set used to draw object previews.
        """
        self.graphic_set = graphic_set
        self.graphics_set = GraphicsSet.from_number(self.graphic_set)

    def set_palette_group_index(self, palette_group_index: int):
        """Update the palette-group state used by later decode operations.

        The palette-group index is stored separately so creation workflows can
        keep the same object-set state while swapping the palette rows used for
        later previews and rendered blocks.

        Parameters
        ----------
        palette_group_index : int
            Index of the palette group.
        """
        self.palette_group_index = palette_group_index
        self.palette_group = load_palette_group(self.object_set, self.palette_group_index)

    def from_data(self, data: bytearray, index: int) -> Jump | LevelObject:
        """Decode serialized level-object bytes into an editor object.

        This is the main decode boundary for loaded level data: jump records
        branch into ``Jump`` objects, while terrain records reuse the stored
        graphics and palette context to build ``LevelObject`` instances.

        Parameters
        ----------
        data : bytearray
            Raw bytes or bytearray being parsed.
        index : int
            Zero-based index of the item to access.

        Returns
        -------
        Jump | LevelObject
            Editor object created from serialized level-object bytes.
        """
        if Jump.is_jump(data):
            return Jump(data)

        assert self.graphics_set is not None

        # todo get rid of index by fixing ground map
        return LevelObject(
            data,
            self.object_set,
            self.palette_group,
            self.graphics_set,
            self.objects_ref,
            self.vertical_level,
            index,
            size_minimal=self.size_minimal,
        )

    def from_properties(
        self,
        domain: int,
        object_index: int,
        x: int,
        y: int,
        length: int | None,
        index: int,
    ):
        """Build an editor object from explicit object properties.

        This helper is the inverse creation path used by forms and commands:
        it packs explicit properties into the SMB3 byte layout first, then
        reuses :meth:`from_data` so property-driven creation and byte-driven
        decode stay on the same workflow path.

        Parameters
        ----------
        domain : int
            Object domain that determines how the object is interpreted.
        object_index : int
            Index of the object.
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.
        length : int | None
            Object length value.
        index : int
            Zero-based index of the item to access.

        Returns
        -------
        Jump | LevelObject
            Editor object created from explicit property values.

        Examples
        --------
        Build a level object from form-style inputs and reuse the same decode
        path as serialized level data::

            factory = LevelObjectFactory(1, 0, 0, objects_ref=[], vertical_level=False)
            obj = factory.from_properties(0, 0x20, x=0x10, y=0x00, length=None, index=1)
            type(obj).__name__
            'LevelObject'
        """
        if self.vertical_level:
            offset = y // LEVEL_SCREEN_HEIGHT
            y %= LEVEL_SCREEN_HEIGHT

            x += offset * LEVEL_SCREEN_WIDTH

        data = bytearray(3)

        data[0] = domain << 5 | y
        # TODO is this the right thing here, or does it break undo/redo
        data[1] = clamp(0, x, 0xFF)
        data[2] = object_index

        if length is not None:
            data.append(length)

        obj = self.from_data(data, index)

        return obj
