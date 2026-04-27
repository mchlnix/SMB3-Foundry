"""Define the minimal geometry contract shared by Foundry editor objects.

This module provides the small shared API that lets level objects, enemies,
jumps, and world-map objects participate in one selection, movement, and
hit-testing workflow. It keeps common geometry and type access in one place so
editor tools can work with heterogeneous objects without branching on the
concrete ROM record they came from.

See Also
--------
foundry.game.gfx.objects.in_level.in_level_object
    Extends this contract for objects that live inside level data streams.
foundry.game.gfx.objects.world_map.map_object
    World-map object implementation that reuses the same geometry surface.
"""

import abc

from smb3parse.util.rect import Rect


class ObjectLike(abc.ABC):
    # TODO too ambiguous to be part of an API?
    # This whole thing with everything needing to be a property to be type consistent kinda blows...
    """Define the minimal geometry contract shared by editor objects.

    Concrete level objects, enemies, jumps, and world-map objects all need a
    name, a type id, a position, selection state, and a rectangle for hit
    testing. This base class centralizes that shared surface so editor tools
    can move, inspect, and select heterogeneous objects through one API.

    Attributes
    ----------
    _name : str
        Display name used by editor-facing UI.
    _type : int
        Type id used by concrete subclasses.
    _x_position : int
        Horizontal coordinate in object space.
    _y_position : int
        Vertical coordinate in object space.
    rect : Rect
        Rectangle used for hit testing and selection.
    selected : bool
        Whether the object is selected in the editor.

    Examples
    --------
    Shared editor tools can move heterogeneous objects through one geometry
    surface::

        x, y = obj.get_position()
        obj.move_by(1, 0)
    """
    selected: bool

    rect: Rect

    def __init__(self):
        """Initialize common editor-facing object state."""
        self.selected = False
        self._name = ""
        self._type = 0

        self._x_position = 0
        self._y_position = 0

    @property
    def name(self):
        """Display name shown by editor UI.

        Concrete objects expose this property so object lists, tooltips, and
        status panels can label heterogeneous selections through one shared API
        while subclasses keep their own storage details private. The property is
        therefore the label boundary between concrete object state and shared UI
        workflow.

        Returns
        -------
        str
            Human-readable object name.
        """
        return self._name

    @name.setter
    def name(self, value):
        """Store the display name used by editor UI.

        Parameters
        ----------
        value : str
            Human-readable object name.
        """
        self._name = value

    @property
    def x_position(self):
        """Horizontal coordinate in object space.

        Shared movement and selection tools read this property instead of
        reaching into subclass-specific ROM records.

        Returns
        -------
        int
            Horizontal coordinate used for selection and movement.
        """
        return self._x_position

    @x_position.setter
    def x_position(self, value):
        """Store the object's horizontal position in object space.

        Parameters
        ----------
        value : int
            Horizontal coordinate used for selection and movement.
        """
        self._x_position = value

    @property
    def y_position(self):
        """Vertical coordinate in object space.

        Shared movement and selection tools read this property instead of
        reaching into subclass-specific ROM records.

        Returns
        -------
        int
            Vertical coordinate used for selection and movement.
        """
        return self._y_position

    @y_position.setter
    def y_position(self, value):
        """Store the object's vertical position in object space.

        Parameters
        ----------
        value : int
            Vertical coordinate used for selection and movement.
        """
        self._y_position = value

    @property
    def type(self):
        """Subclass-specific type identifier.

        Concrete implementations map this value to SMB3 object, enemy, jump,
        or world-map records, and editor tools use it when cycling or replacing
        types through the shared object interface. The property is the shared
        type-state boundary used by replace, cycle, and serialization
        workflows.

        Returns
        -------
        int
            Type id interpreted by the concrete object implementation.
        """
        return self._type

    @type.setter
    def type(self, value):
        """Store the subclass-specific type identifier.

        Parameters
        ----------
        value : int
            Type id interpreted by the concrete object implementation.
        """
        self._type = value

    def copy(self):
        """Create a duplicate of the object.

        Concrete subclasses implement this for clipboard, drag-preview, and
        undo workflows that duplicate editor objects.
        """
        pass

    def set_position(self, x, y):
        """Update the object's position in one operation.

        Keeping the position update centralized lets subclasses maintain any
        coordinate-dependent state behind one shared mutating call.

        Parameters
        ----------
        x : int
            New horizontal coordinate.
        y : int
            New vertical coordinate.
        """
        self.x_position = x
        self.y_position = y

    def move_by(self, dx, dy):
        """Offset the object's position by the supplied delta.

        This helper keeps nudge and drag code in terms of deltas while letting
        subclasses centralize the actual position write in ``set_position``. It
        is the small workflow adapter that turns movement deltas into one
        shared position-update path across object types.

        Parameters
        ----------
        dx : int
            Horizontal offset.
        dy : int
            Vertical offset.
        """
        x, y = self.get_position()
        new_x = x + dx
        new_y = y + dy

        self.set_position(new_x, new_y)

    def get_position(self) -> tuple[int, int]:
        """Object-space position used by shared editor tools.

        The pair is the geometry contract consumed by selection, movement, and
        serialization helpers that operate on mixed object types.

        Returns
        -------
        tuple[int, int]
            Horizontal and vertical coordinates.
        """
        return self.x_position, self.y_position

    def point_in(self, x, y):
        """Check whether a point falls inside the object's hit box.

        The shared selection workflow uses this helper so each object can rely
        on its rectangle instead of reimplementing point testing.

        Parameters
        ----------
        x : int
            Horizontal coordinate in object space.
        y : int
            Vertical coordinate in object space.

        Returns
        -------
        bool
            ``True`` when the point is inside ``rect``.
        """
        return self.rect.point_in(x, y, include_borders=False)

    def get_rect(self, block_length=1) -> Rect:
        """Rectangle scaled for drawing.

        Rendering and selection overlays use the scaled rectangle to bridge
        object-space coordinates into pixel-space geometry.

        Parameters
        ----------
        block_length : int, optional
            Pixel size of one object-space unit.

        Returns
        -------
        Rect
            Rectangle scaled into draw-space units.

        Examples
        --------
        Concrete objects supply ``rect`` in object-space units, and
        ``get_rect`` scales that geometry into draw-space coordinates:

        >>> class DemoObject(ObjectLike):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.rect = Rect(2, 3, 4, 5)
        ...     def copy(self):
        ...         return self
        ...     def change_type(self, new_type):
        ...         self.type = new_type
        >>> demo = DemoObject()
        >>> demo.get_rect(16)
        Rect(32, 48, 64, 80)
        """
        return self.rect * block_length

    @abc.abstractmethod
    def change_type(self, new_type):
        """Change the object's type identifier.

        Parameters
        ----------
        new_type : int
            Replacement type identifier understood by the subclass.
        """
        pass
