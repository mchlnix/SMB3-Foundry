"""Represent parsed SMB3 level and enemy records before model construction.

This module holds the lightweight dataclasses that the parser package uses
while scanning raw object and enemy byte streams. Each instance preserves the
object-set context, the source bytes, and the ROM offset that later parser
steps use to build richer level structures or editor-facing diagnostics.

See Also
--------
smb3parse.util.parser
    Higher-level parsing helpers that produce these records while walking ROM
    pointer tables and level payloads.
smb3parse.objects.level_object
    Structured object model that consumes decoded object bytes after this
    parser-stage recordkeeping.
"""

from dataclasses import dataclass, field

from smb3parse.util import apply


@dataclass
class ParsedObject:
    """Store one decoded level-object record from the object byte stream.

    ``ParsedObject`` is the handoff shape between the byte-walking parser and
    the higher-level object decoding layer. It keeps enough ROM-facing detail
    intact that later code can choose an object-set rule, reconstruct geometry,
    and report where the source record came from.

    Parameters
    ----------
    object_set_num : int
        Object-set identifier that selects the SMB3 decoding tables for this
        record.
    obj_bytes : list[int]
        Raw bytes copied from the level object stream for one parsed object.
    pos_in_mem : int
        Absolute ROM position where the parser found the first object byte.
    tiles_in_level : list[tuple[int, int]], optional
        Tile coordinates that this record occupies after parser-side expansion.

    Attributes
    ----------
    object_set_num : int
        Object-set number that downstream object factories use to interpret
        ``obj_bytes``.
    obj_bytes : list[int]
        Parsed object's raw byte payload, preserved for later structural
        decoding.
    pos_in_mem : int
        ROM offset of the object record, used by diagnostics and serializer
        paths that need to point back to the source stream.
    tiles_in_level : list[tuple[int, int]]
        Tile positions touched by the parsed object within the level grid.

    Notes
    -----
    This class intentionally stays close to the byte layout. It is a parser
    staging record, not the richer gameplay or editor model.
    """

    object_set_num: int

    obj_bytes: list[int]
    pos_in_mem: int

    tiles_in_level: list[tuple[int, int]] = field(default_factory=list)

    def __str__(self):
        """Render the parsed record for parser diagnostics.

        The parser and editor tooling use this string when they need to inspect
        a record before it has been promoted into a richer object model.

        Returns
        -------
        str
            Human-readable summary containing the ROM offset, raw bytes, and
            any tile coordinates already associated with the object.
        """

        return f"Obj @ {self.pos_in_mem:#x}: {apply(hex, self.obj_bytes)}, {self.tiles_in_level}"

    @property
    def domain(self):
        """Expose the object-family selector encoded in the header byte.

        The parser-level handoff keeps this property separate from
        :attr:`obj_id` so downstream code can branch in the same order as the
        SMB3 object stream itself: first choose the object family, then choose
        the concrete object rule inside that family. Object factories and
        diagnostics both read this value before they commit to a later decode
        path, which makes it part of the parser's cross-stage routing contract.

        Returns
        -------
        int
            High three bits from ``obj_bytes[0]`` that the object parser uses
            to separate object families while expanding the stream.
        """

        return self.obj_bytes[0] >> 5

    @property
    def obj_id(self):
        """Expose the object identifier used for shape-specific decoding.

        Parser consumers pair this identifier with :attr:`domain` and
        ``object_set_num`` to select the concrete object behavior table.

        Returns
        -------
        int
            Third byte of the object payload, preserved as the object ID that
            object-set lookup code uses to select shape and behavior rules.
        """

        return self.obj_bytes[2]

    @property
    def is_fixed(self):
        """Report whether the object uses the fixed-object decoding path.

        Higher-level object parsers branch on this property before they decide
        how many follow-up bytes belong to the record and whether tile coverage
        can be derived immediately or only after variable-size expansion. That
        means this flag is part of the boundary between raw byte walking in the
        parser and the later geometry-building stage that fills
        ``tiles_in_level``.

        Returns
        -------
        bool
            ``True`` when the object ID falls in the fixed-object range that
            SMB3 decodes without variable-size layout rules.
        """

        return self.obj_id < 0x10

    @property
    def x(self):
        """Expose the parsed horizontal tile coordinate for this record.

        Geometry-building code reads this value together with :attr:`y` when it
        maps the raw object stream into level-space positions.

        Returns
        -------
        int
            Horizontal tile coordinate byte that later object-model code maps
            into level geometry.
        """

        return self.obj_bytes[1]

    @property
    def y(self):
        """Expose the parsed vertical tile coordinate from the header byte.

        The parser keeps the Y bits folded into the header byte until this
        property is queried, which mirrors SMB3's packed object-stream format.

        Returns
        -------
        int
            Lower five bits of ``obj_bytes[0]``, which SMB3 uses as the
            vertical tile coordinate for the parsed object record.
        """

        return self.obj_bytes[0] & 0b1_1111


@dataclass
class ParsedEnemy:
    """Store one decoded enemy record from the enemy byte stream.

    ``ParsedEnemy`` preserves the compact enemy-stream record after the parser
    has located it in ROM but before the editor or game-facing code turns it
    into a richer enemy model.

    Parameters
    ----------
    object_set_num : int
        Object-set identifier that keeps enemy records aligned with the level
        context that produced them.
    obj_bytes : list[int]
        Raw bytes copied from the enemy stream for one parsed enemy entry.
    pos_in_mem : int
        Absolute ROM position where the parser found the enemy record.

    Attributes
    ----------
    object_set_num : int
        Object-set number carried forward with the enemy record for later
        decoding and editor correlation.
    obj_bytes : list[int]
        Raw bytes that describe the enemy type and placement in the ROM stream.
    pos_in_mem : int
        ROM offset of the enemy record inside the parsed level payload.

    Notes
    -----
    Enemy parsing is simpler than level-object parsing in this package, so the
    parser exposes a narrower view: type byte plus decoded coordinates.
    """

    object_set_num: int

    obj_bytes: list[int]
    pos_in_mem: int

    def __str__(self):
        """Render the parsed enemy record for debugging output.

        Parser-side callers use this string at the point where they still have
        only a staging record but need to emit a readable trace line or error
        message. Keeping the ROM offset and raw bytes together in one string
        lets the parser hand a partially decoded enemy record straight to
        diagnostics without first constructing a richer enemy model.

        Returns
        -------
        str
            Human-readable summary containing the ROM offset and enemy bytes.
        """

        return f"Enemy @ {self.pos_in_mem:#x}: {apply(hex, self.obj_bytes)}"

    @property
    def domain(self):
        """Expose the fixed parser domain used for enemy records.

        Mixed parser consumers read ``domain`` immediately after record
        creation, before they decide whether to keep processing a parsed item
        through object-style helpers or enemy-specific helpers. Returning a
        stable value here preserves the shared parsed-record interface even
        though enemy records skip the domain split that level objects encode in
        their header byte.

        Returns
        -------
        int
            Always ``0`` because enemy entries in this parser path do not use
            the level-object domain bit split.
        """

        return 0

    @property
    def obj_id(self):
        """Expose the enemy identifier byte for later model construction.

        Downstream enemy factories read this value when they leave parser
        staging and choose the concrete enemy definition that will replace this
        record. Parser-side inspection helpers also combine it with :attr:`x`
        and :attr:`y` to report what the byte stream just produced, so this
        property carries the enemy identity through the parser-to-model and
        parser-to-diagnostics handoffs.

        Returns
        -------
        int
            First enemy-stream byte, used by downstream code as the enemy
            identifier.
        """

        return self.obj_bytes[0]

    @property
    def is_fixed(self):
        """Report whether enemy decoding uses a fixed-layout record.

        This lets shared parser consumers treat enemy records and object records
        through a similar interface while still acknowledging that enemies do
        not have a variable-size decoding branch here, so no later parser step
        needs to reinterpret the byte count for this record. In workflow terms,
        a true result tells mixed object/enemy tooling that enemy bytes can
        move straight from parser staging into placement or diagnostics without
        a second shape-expansion phase.

        Returns
        -------
        bool
            Always ``True`` because enemy records in this parser format have a
            fixed byte layout.
        """

        return True

    @property
    def x(self):
        """Expose the parsed horizontal coordinate for the enemy record.

        Later editor and model code reads this value directly when reconstructing
        enemy placement from the raw byte stream.

        Returns
        -------
        int
            Horizontal coordinate byte from the enemy stream.
        """

        return self.obj_bytes[1]

    @property
    def y(self):
        """Expose the parsed vertical coordinate for the enemy record.

        This value travels with :attr:`x` and :attr:`obj_id` into the next
        parser stage that builds richer enemy objects or diagnostics.

        Returns
        -------
        int
            Vertical coordinate byte from the enemy stream.
        """

        return self.obj_bytes[2]
