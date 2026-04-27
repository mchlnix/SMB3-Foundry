"""Shared position-oriented abstractions for world-map editor objects.

This module defines the common editor contract used by heterogeneous overworld
records such as sprites, tiles, locks, level pointers, and airship waypoints.
It normalizes their coordinate access so selection, drag, and drawing tools
can operate without learning each ROM storage format.

See Also
--------
foundry.game.gfx.objects.object_like
    Supplies the broader editor object protocol shared with in-level objects.
foundry.game.level.WorldMap
    Produces the concrete world-map records wrapped by these abstractions.
"""

import abc
from abc import ABC

from foundry.game.gfx.objects.object_like import ObjectLike
from smb3parse.util.rect import Rect


# TODO sort out x_position and y_position
class MapObject(ObjectLike, ABC):
    """Define the shared editor contract for world-map objects.

    Level pointers, sprites, locks, travel points, and tiles all store their
    position differently in SMB3 world-map data. ``MapObject`` hides that
    storage detail behind one position-oriented interface so world-map tools
    can move, select, and draw heterogeneous map objects consistently.

    Attributes
    ----------
    length : int
        Width-like dimension used by subclasses that expose rectangular bounds.
    name : str
        Display name shown by world-map editor UI.
    width : int
        Height-like dimension used by subclasses that expose rectangular bounds.

    Notes
    -----
    The data flow is concrete ROM-backed world-map record -> ``MapObject``
    position API -> shared editor tools for selection, movement, and drawing.

    Examples
    --------
    Concrete world-map objects implement ``get_position()`` and
    ``set_position()`` for their own backing record, while editor tools talk
    only to the normalized ``MapObject`` surface::

        class DemoMapObject(MapObject):
            type = 0x01

            def __init__(self):
                super().__init__()
                self._pos = (4, 7)

            def get_position(self):
                return self._pos

            def set_position(self, x, y):
                self._pos = (x, y)

        obj = DemoMapObject()
        obj.x_position, obj.y_position
        obj.rect

    The important data shape is "subclass storage tuple in, normalized
    selection geometry out": ``get_position()`` supplies tile coordinates and
    ``rect`` turns them into the one-tile pick region shared by world-map
    selection and drag tools.
    """

    def __init__(self):
        """Initialize shared world-map object state."""
        super(MapObject, self).__init__()

        self.name = type(self).__name__

    @property
    def x_position(self):
        """World-map column for the object.

        World-map editors use this property as the common horizontal position
        API even though subclasses store their ROM data differently.

        Returns
        -------
        int
            Horizontal tile coordinate on the world map.
        """
        return self.get_position()[0]

    @x_position.setter
    def x_position(self, value):
        """Update the world-map column while preserving the row.

        Parameters
        ----------
        value : int
            Horizontal tile coordinate on the world map.
        """
        self.set_position(value, self.y_position)

    @property
    def y_position(self):
        """World-map row for the object.

        World-map editors use this property as the common vertical position API
        even though subclasses store their ROM data differently.

        Returns
        -------
        int
            Vertical tile coordinate on the world map.
        """
        return self.get_position()[1]

    @y_position.setter
    def y_position(self, value):
        """Update the world-map row while preserving the column.

        Parameters
        ----------
        value : int
            Vertical tile coordinate on the world map.
        """
        self.set_position(self.x_position, value)

    @abc.abstractmethod
    def set_position(self, x, y):
        """Store a new world-map position in the subclass data record.

        Subclasses map these coordinates back into their ROM-backed data
        structures so shared move and selection tools do not need to know that
        storage format.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.
        """
        pass

    @abc.abstractmethod
    def get_position(self):
        """World-map coordinates for the object."""
        pass

    @property
    def rect(self):
        """One-tile rectangle used for hit testing.

        World-map selection code treats most map objects as tile-aligned picks,
        so the default rectangle mirrors the shared position API and feeds the
        same drag and selection helpers used by rectangular objects. That keeps
        hit-testing state flowing through the same normalized geometry API used
        elsewhere in the world-map workflow.

        Returns
        -------
        Rect
            Rectangle anchored at the object's current map position.
        """
        return Rect(self.x_position, self.y_position, 1, 1)

    @rect.setter
    def rect(self, value):
        """Update position and extents from a moved selection rectangle.

        Parameters
        ----------
        value : Rect
            Rectangle describing the new object bounds.
        """
        self.set_position(value.x, value.y)
        self.length = value.width
        self.width = value.height

    def move_by(self, dx, dy):
        """Offset the object on the world map.

        This helper keeps drag and keyboard nudging workflows expressed in the
        shared coordinate API instead of subclass-specific storage writes.

        Parameters
        ----------
        dx : int
            Horizontal tile offset.
        dy : int
            Vertical tile offset.

        Examples
        --------
        Drag and nudge commands can move any world-map object through the same
        normalized interface::

            obj = DemoMapObject()
            obj.move_by(2, -1)
            obj.get_position()
        """
        self.set_position(self.x_position + dx, self.y_position + dy)

    def point_in(self, x, y):
        """Check whether the supplied coordinate matches this object.

        Single-tile world-map objects use exact tile equality for picking, so
        this helper is the small contract that lets selection workflows test
        heterogeneous world-map objects through one coordinate API.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.

        Returns
        -------
        bool
            ``True`` when the coordinate matches ``get_position()``.
        """
        return x, y == self.get_position()

    def __repr__(self):
        """Compact developer-facing world-map description.

        The representation is mainly used when debugging map-object ordering
        and selection behavior.

        Returns
        -------
        str
            Object type, name, and world-map coordinates.
        """
        return f"MapObject #{self.type:#x}: '{self.name}' at {self.x_position}, {self.y_position}"
