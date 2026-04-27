"""Shared contracts for SMB3 objects that occupy positions inside a level.

This module defines the common numeric bounds used by in-level object parsers and
the :class:`InLevelObject` base class that stores decoded object state. Concrete
object families populate the shared ``domain``, ``id``, ``x``, ``y``, and
optional ``additional_length`` fields after interpreting their raw byte data.

The module sits near the bottom of the in-level decoding workflow: object
specific parsers read bytes from level data, normalize them into the shared
attributes defined here, and then higher-level tooling consumes those
attributes to inspect, edit, or render level contents.

See Also
--------
InLevelObject
    Base contract shared by parsed level objects.
"""

from abc import ABC

MIN_DOMAIN = 0
MAX_DOMAIN = 7
DOMAIN_COUNT = 8
MIN_Y_VALUE = 0
MAX_Y_VALUE = 27
MIN_ID_VALUE = 0
MAX_ID_VALUE = 0xFF
MIN_X_VALUE = 0
MAX_X_VALUE = 0xFF
MIN_ADDITIONAL_LENGTH = 0
MAX_ADDITIONAL_LENGTH = 0xFF

MAX_ENEMY_ITEM_ID = 0xEC


class InLevelObject(ABC):
    """Represent a decoded SMB3 object anchored to a level position.

    Instances of this base class keep the raw bytes used during decoding
    alongside a normalized set of coordinates and identifiers that subclasses
    fill in. The abstraction is intentionally small: it gives callers one place
    to read object identity, domain placement, and optional length metadata
    without caring which concrete object family produced those values.

    Parameters
    ----------
    data : bytearray
        Raw object bytes owned by the concrete decoder.

    Attributes
    ----------
    _data : bytearray
        Raw bytes backing the decoded object record.
    _domain : int
        Domain index associated with the object's placement in the level data.
    _id : int
        Object identifier decoded from the backing bytes.
    _x : int
        Horizontal position of the object within the level.
    _y : int
        Vertical position of the object within the level.
    _length : int | None
        Optional extra length value for object formats that encode one.

    Notes
    -----
    The base class does not validate ranges when attributes are assigned.
    Callers and concrete decoders are responsible for honoring the constants in
    this module when interpreting SMB3 level data.
    """

    def __init__(self, data: bytearray):
        """Initialize shared storage for a decoded in-level object.

        Parameters
        ----------
        data : bytearray
            Raw bytes from which a concrete object parser will derive the shared
            object fields.
        """
        self._data: bytearray = data
        self._domain: int = 0
        self._id: int = 0
        self._x: int = 0
        self._y: int = 0
        self._length: int | None = None

    @property
    def id(self):
        """Normalized identifier for this decoded object.

        Consumers use this property after object-specific parsing has mapped raw
        bytes into a stable identifier that can drive lookup, rendering, or
        editing workflows.

        Returns
        -------
        int
            Identifier assigned by the concrete decoder.
        """
        return self._id

    @id.setter
    def id(self, value):
        """Store the decoded object identifier.

        Parameters
        ----------
        value : int
            Identifier derived from the object's backing bytes.
        """
        self._id = value

    @property
    def domain(self):
        """Domain bucket assigned during decoding.

        The domain value lets higher-level level tooling preserve how SMB3
        grouped this object inside the original object stream.

        Returns
        -------
        int
            Domain value used to group the object inside SMB3 level data.
        """
        return self._domain

    @domain.setter
    def domain(self, value):
        """Store the decoded domain index for the object.

        Parameters
        ----------
        value : int
            Domain value assigned by the concrete decoder.
        """
        self._domain = value

    @property
    def x(self):
        """Shared horizontal coordinate for downstream object consumers.

        Parsers normalize object-family specific position bytes into this shared
        coordinate so downstream code can place every object through one API.

        Returns
        -------
        int
            Horizontal object coordinate.
        """
        return self._x

    @x.setter
    def x(self, value):
        """Store the decoded horizontal level position.

        Parameters
        ----------
        value : int
            Horizontal object coordinate.
        """
        self._x = value

    @property
    def y(self):
        """Shared vertical coordinate for downstream object consumers.

        Parsers normalize object-family specific position bytes into this shared
        coordinate so downstream code can place every object through one API.

        Returns
        -------
        int
            Vertical object coordinate.
        """
        return self._y

    @y.setter
    def y(self, value):
        """Store the decoded vertical level position.

        Parameters
        ----------
        value : int
            Vertical object coordinate.
        """
        self._y = value

    @property
    def additional_length(self):
        """Optional decoded length extension for this object.

        Some object encodings carry an extra length byte in addition to their
        core identifier and coordinates. Callers use this shared property to
        detect and consume that extra span information consistently.

        Returns
        -------
        int | None
            Extra length value for object formats that encode one, otherwise
            ``None``.
        """
        return self._length

    @additional_length.setter
    def additional_length(self, value):
        """Store the optional extra length encoded for the object.

        Parameters
        ----------
        value : int | None
            Extra length value, or ``None`` for object formats without one.
        """
        self._length = value

    @property
    def has_additional_length(self):
        """Whether decoding populated the shared length slot for this record.

        This convenience property gives callers a format-agnostic way to branch
        between fixed-size object records and records that extend across an
        additional encoded span after parsing has filled the shared state.

        Returns
        -------
        bool
            ``True`` when :attr:`additional_length` contains a decoded value.
        """
        return self.additional_length is not None
