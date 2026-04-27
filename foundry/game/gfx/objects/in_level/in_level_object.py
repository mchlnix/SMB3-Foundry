"""Define the shared editor contract for objects that live inside a level.

This module provides the abstract base that lets terrain objects, enemy items,
and jumps participate in one selection, movement, rendering, and serialization
workflow. It is the boundary that hides which SMB3 byte stream owns a concrete
object while keeping the editor-facing geometry and preview APIs consistent.

See Also
--------
foundry.game.gfx.objects.in_level.level_object
    Concrete terrain-object implementation built on this interface.
foundry.game.gfx.objects.in_level.enemy_item
    Enemy-stream object implementation that reuses the same editor contract.
"""

import abc

from foundry.game import EXPANDS_NOT
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.ObjectSet import ObjectSet


class InLevelObject(ObjectLike, abc.ABC):
    """Define the shared interface for editable objects inside a level.

    Level objects, enemies, items, and jumps all participate in selection,
    movement, drawing, and serialization. This base class names the common
    geometry, encoded bytes, and rendering state that the editor can use
    without knowing which ROM data stream owns the concrete object.

    Attributes
    ----------
    _obj_index : int
        Encoded object or enemy type identifier.
    anim_frame : int
        Animation frame used by renderers that draw animated objects.
    data : bytearray
        Encoded bytes backing the object.
    domain : int
        Object domain encoded in level object data.
    is_4byte : bool
        Whether the encoded object uses the four-byte format.
    object_set : ObjectSet
        Object set used to resolve definitions and graphics.
    palette_group : PaletteGroup
        Palette group used when drawing the object.
    rendered_height : int
        Height in blocks after rendering or expansion.
    rendered_width : int
        Width in blocks after rendering or expansion.
    x_position : int
        X coordinate in level space.
    y_position : int
        Y coordinate in level space.

    Notes
    -----
    ``InLevelObject`` is the abstraction that lets level views, undo commands,
    status panels, and selection logic work with terrain objects, enemies, and
    jumps through one editor-facing interface.

    Examples
    --------
    Concrete subclasses expose one consistent geometry and serialization
    surface to the editor, even though they may come from different SMB3 byte
    streams::

        class DemoObject(InLevelObject):
            def render(self):
                return None

            def get_status_info(self):
                return [("type", hex(self.obj_index))]

            def resize_by(self, dx, dy):
                self.rendered_width += dx
                self.rendered_height += dy

            def increment_type(self):
                self.obj_index += 1

            def decrement_type(self):
                self.obj_index -= 1

            def copy(self):
                clone = DemoObject()
                clone.data = self.data[:]
                clone._obj_index = self._obj_index
                clone.rendered_width = self.rendered_width
                clone.rendered_height = self.rendered_height
                return clone

            def to_bytes(self):
                return bytes(self.data)

        obj = DemoObject()
        obj.data = bytearray([0x00, 0x10, 0x20])
        obj._obj_index = 0x10
        obj.rendered_width = 2
        obj.rendered_height = 3

        width, height = obj.display_size(zoom_factor=2)
        payload = obj.to_bytes()

    This shared contract is what lets selection, object lists, and undo
    commands work with terrain objects and jumps without branching on the
    concrete subclass first.
    """

    object_set: ObjectSet
    palette_group: PaletteGroup

    _obj_index: int
    domain: int
    is_4byte: bool

    data: bytearray

    rendered_width: int
    """Width after rendering the object. Only changes for expanding types."""
    rendered_height: int
    """Height after rendering the object. Only changes for expanding types."""

    anim_frame: int = 0

    def __init__(self):
        """Initialize the object and its runtime state.

        The base initializer establishes default level coordinates shared by all concrete in-level
        object types.
        """
        super(InLevelObject, self).__init__()

        # TODO base this on Position, like MapObjects do
        self.x_position = 0
        self.y_position = 0

    def display_size(self, zoom_factor: int = 1):
        """Calculate the Qt display size for the rendered object.

        The result converts rendered block dimensions into pixel dimensions for
        Qt widgets and previews, which lets mixed object types move through the
        same sizing workflow before they reach views or object lists.

        Parameters
        ----------
        zoom_factor : int, optional
            Zoom factor used for display scaling.

        Returns
        -------
        tuple[int, int]
            Display size after applying the zoom factor.

        Examples
        --------
        A concrete in-level object reports its rendered block footprint in Qt
        pixels so object lists and scene previews can size one mixed
        selection consistently::

            class DemoObject(InLevelObject):
                def render(self):
                    return None

                def get_status_info(self):
                    return []

                def resize_by(self, dx, dy):
                    return None

                def increment_type(self):
                    return None

                def decrement_type(self):
                    return None

                def copy(self):
                    return self

                def to_bytes(self):
                    return bytes()

            obj = DemoObject()
            obj.rendered_width = 2
            obj.rendered_height = 3

            assert obj.display_size(zoom_factor=2) == (32, 48)
        """
        return (
            self.rendered_width * Block.SIDE_LENGTH * zoom_factor,
            self.rendered_height * Block.SIDE_LENGTH * zoom_factor,
        )

    @property
    def obj_index(self):
        """Expose the encoded type identifier used by shared editor workflows.

        Concrete subclasses map this identifier back to object definitions,
        sprites, or special editor behavior, so this property is the shared
        type lookup boundary used by mixed selections.

        Returns
        -------
        int
            Object or enemy type identifier.
        """
        return self._obj_index

    @obj_index.setter
    def obj_index(self, value):
        """Store the object or enemy type identifier.

        Subclasses may add richer type-changing behavior when dimensions or rendered blocks need to
        be refreshed.

        Parameters
        ----------
        value : int
            Object or enemy type identifier.
        """
        self._obj_index = value

    @abc.abstractmethod
    def render(self):
        """Render or refresh the object's drawable representation.

        Concrete subclasses decide whether rendering means expanding block indexes, copying sprites,
        or doing nothing for non-visual pseudo-objects.
        """
        pass

    @abc.abstractmethod
    def get_status_info(self):
        """Provide status-bar fields for the selected object state.

        The GUI consumes these label/value pairs for mixed selections without needing subtype
        checks.
        """
        pass

    @abc.abstractmethod
    def resize_by(self, dx, dy):
        """Resize the object by a block offset.

        Concrete subclasses translate the resize into their encoded length
        fields or ignore it when the object type is not resizable, which keeps
        editor resize gestures aligned with serialized object bytes.

        Parameters
        ----------
        dx : int
            Horizontal offset.
        dy : int
            Vertical offset.
        """
        pass

    @abc.abstractmethod
    def increment_type(self):
        """Advance to the next object type.

        Implementations keep editor keyboard actions consistent across object subtypes.
        """
        pass

    @abc.abstractmethod
    def decrement_type(self):
        """Move to the previous object type.

        Implementations keep editor keyboard actions consistent across object subtypes.
        """
        pass

    @abc.abstractmethod
    def copy(self):
        """Create an independent copy for undo, paste, and drag workflows.

        Undo, paste, and drag operations rely on copies that preserve encoded
        state without sharing mutable editor state.
        """
        pass

    @abc.abstractmethod
    def to_bytes(self):
        """Serialize the object back to its ROM data representation.

        Concrete subclasses own the details of their byte layout.
        """
        pass

    def expands(self):
        """Expose expansion mode to shared render and resize code.

        Non-expanding is the shared default for objects that do not override expansion behavior.

        Returns
        -------
        int
            Expansion bitmask described by ``EXPANDS_*`` constants and reused by
            callers that coordinate one expansion contract across object types.
        """
        return EXPANDS_NOT

    def primary_expansion(self):
        """Expose the primary expansion value through the shared object API.

        This default lets callers ask for expansion length without branching on
        object subtype.

        Returns
        -------
        int
            Primary expansion amount for the object, allowing callers to query
            expansion state without branching on the concrete subtype.
        """
        return EXPANDS_NOT
