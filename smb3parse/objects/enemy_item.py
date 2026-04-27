"""Decode SMB3 enemy and item records from three-byte level entries.

This module defines :class:`EnemyItem`, the compact in-level object wrapper
used for SMB3 enemy and item streams whose records contain only an identifier
and two coordinates. The class translates that fixed-width byte tuple into the
shared :class:`smb3parse.objects.InLevelObject` fields so higher-level code can
inspect or render enemy placements through the same interface used by other
decoded object families.

The file sits on the object-decoding side of the parser stack: level readers
split enemy data into three-byte records, instantiate :class:`EnemyItem`, and
then pass the normalized object onward to tooling that reasons about level
contents without reinterpreting raw bytes.

See Also
--------
smb3parse.objects.InLevelObject
    Shared base contract for decoded SMB3 objects with normalized coordinates.
"""

from smb3parse.objects import InLevelObject


class EnemyItem(InLevelObject):
    """Represent a decoded SMB3 enemy or item placement record.

    Enemy and item records in SMB3 use a compact three-byte encoding: one byte
    for the enemy or item identifier and one byte each for horizontal and
    vertical placement. This wrapper preserves that decoded state in the common
    :class:`~smb3parse.objects.InLevelObject` fields so downstream consumers can
    treat enemy streams and other object families through a uniform interface.

    Parameters
    ----------
    data : bytes | bytearray | list[int]
        Three-byte enemy or item record ordered as ``(id, x, y)``.

    Attributes
    ----------
    domain : int
        Domain assigned to the decoded record. Enemy and item records always
        normalize to domain ``0`` in this parser.
    id : int
        Decoded enemy or item identifier.
    x : int
        Horizontal level coordinate decoded from the record.
    y : int
        Vertical level coordinate decoded from the record.

    Notes
    -----
    This parser does not reinterpret SMB3-specific subfields inside the
    identifier byte. It only preserves the byte ordering and normalizes the
    values into the shared in-level object contract.

    Raises
    ------
    ValueError
        If the supplied record is not exactly three bytes long.
    """

    def __init__(self, data):
        """Decode a three-byte enemy or item record into shared object fields.

        Level readers call this constructor after splitting the enemy stream
        into fixed-width records. Successful initialization moves one raw
        ``(id, x, y)`` tuple into the normalized ``id``, ``x``, and ``y``
        attributes inherited from :class:`InLevelObject`, which lets later
        editor, inspection, or rendering code consume enemy placements without
        re-reading the backing bytes. The constructor performs that handoff in
        two stages: it first validates that the stream produced exactly one
        enemy-sized record, then it fixes the shared ``domain`` slot to ``0``
        and unpacks the three bytes into the persistent object fields used by
        downstream consumers. Parser code does not revisit ``data`` after this
        step; every later workflow reads the decoded placement state from the
        normalized object attributes populated here.

        Parameters
        ----------
        data : bytes | bytearray | list[int]
            Raw enemy or item bytes ordered as ``(id, x, y)``.

        Raises
        ------
        ValueError
            If ``data`` does not contain exactly three bytes.

        Notes
        -----
        The constructor assigns ``domain`` to ``0`` before unpacking the record
        because SMB3 enemy and item entries in this parser do not carry a
        separate domain byte. Downstream code can therefore treat every
        :class:`EnemyItem` as already normalized into the shared object model.
        That normalization is the only decode step later parser and editor
        layers rely on before they group, render, or rewrite enemy placements.
        """
        super(EnemyItem, self).__init__(data)

        if not len(data) == 3:
            raise ValueError(f"Length of the given data must be 3, was {len(data)}.")

        self.domain = 0

        self._id, self._x, self._y = data
