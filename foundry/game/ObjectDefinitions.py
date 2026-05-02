"""Parse and expose SMB3 object-definition metadata for Foundry.

``objects.dat`` is the editor-maintained description of how SMB3 objects
should preview and expand. This module turns those rows into symbolic metadata
records that the rest of Foundry can reuse instead of duplicating Workshop-era
tables or ROM-side generator logic in multiple places.

The module is the bridge between static object-definition data and runtime
object rendering. ``ObjectSet`` loads definitions from here, object factories
decode bytes against those definitions, and in-level renderers branch on the
stored generator and ending metadata.

Notes
-----
The commit history around this file reflects a deliberate shift away from older
ROM object tables toward ``objects.dat`` as the editor's source of truth. The
runtime still resolves some block ids against ROM data, but the editor-facing
meaning of an object id is centralized here.

See Also
--------
foundry.game.ObjectSet
    Combines these definitions with ROM-selected object-set metadata.
foundry.game.gfx.objects.in_level.level_object
    Consumes parsed definitions while decoding and rendering in-level objects.
foundry.game.gfx.objects.in_level.object_renderer
    Applies generator and ending metadata when expanding object bytes into
    blocks.
"""

from enum import Enum
from functools import lru_cache

from foundry import data_dir
from smb3parse.constants import ENEMY_ITEM_OBJECT_SET
from smb3parse.util import apply


# TODO put somewhere else
def dollar_hex_to_int(hex_string: str):
    """Parse a decimal or dollar-prefixed hexadecimal integer.

    Parameters
    ----------
    hex_string : str
        Decimal text or hexadecimal text prefixed with ``$``.

    Returns
    -------
    int
        Parsed integer value.
    """
    hex_string = hex_string.strip()

    if hex_string.startswith("$"):
        hex_string = hex_string.removeprefix("$")

        return int(hex_string, 16)
    else:
        return int(hex_string)


class GeneratorType(Enum):
    """Level objects are generated using different methods, depending on their generator type. Some objects extend until
    they hit another object, some extend up to the sky. To identify in what way a specific type of level object is
    constructed, this enum lists the known generator types.

    The enum names the expansion algorithms used by the object renderer when an
    encoded SMB3 level object is turned into a grid of 16x16 blocks.

    The data flow is direct: ``objects.dat`` names a generator,
    ``ObjectDefinition`` stores that symbolic value, and render logic branches
    on it when expanding a compact object record into blocks.

    Notes
    -----
    The data flow is ``objects.dat`` -> ``ObjectDefinition.generator_type`` ->
    renderer branch selection. This enum exists so that path can stay symbolic
    instead of spreading magic strings or integers through rendering code.
    That indirection keeps the editor aligned with the maintained
    ``objects.dat`` metadata: preview generation, object decoding, and in-level
    rendering can all consult one symbolic generator choice instead of
    hard-coding parallel tables in Python.

    See Also
    --------
    ObjectDefinition
        Stores the generator chosen for each parsed object entry.
    EndType
        Describes how generator output should be capped at one or both ends.

    Examples
    --------
    ``ObjectDefinition`` resolves generator names directly from an
    ``objects.dat`` row:

    >>> row = "0, 0, 0, 3, 2, HORIZONTAL, UNIFORM, -, Question Block, <$12, $13>"
    >>> definition = ObjectDefinition(row)
    >>> definition.generator_type is GeneratorType.HORIZONTAL
    True

    Attributes
    ----------
    BRICK_WALL : GeneratorType
        Brick-wall expansion.
    CENTERED : GeneratorType
        Centered expansion, used by objects such as spinning platforms.
    DESERT_PIPE_BOX : GeneratorType
        Desert pipe-box expansion.
    DIAG_DOWN_LEFT : GeneratorType
        Diagonal expansion down and left.
    DIAG_DOWN_RIGHT : GeneratorType
        Diagonal expansion down and right.
    DIAG_STAGGERED : GeneratorType
        Staggered diagonal expansion.
    DIAG_UP_RIGHT : GeneratorType
        Diagonal expansion up and right.
    DIAG_WEIRD : GeneratorType
        Special diagonal expansion used by legacy object definitions.
    ENDING : GeneratorType
        Level-ending object expansion.
    HORIZONTAL : GeneratorType
        Horizontal expansion.
    HORIZONTAL_2 : GeneratorType
        Alternate horizontal expansion for floating boxes and ceilings.
    HORIZ_TO_GROUND : GeneratorType
        Horizontal expansion that continues toward ground.
    PYRAMID_2 : GeneratorType
        Legacy pyramid expansion value.
    PYRAMID_TO_GROUND : GeneratorType
        Pyramid expansion toward ground or the next object.
    SINGLE_BLOCK : GeneratorType
        Single-block object expansion.
    TO_THE_SKY : GeneratorType
        Vertical expansion upward to the top of the level.
    VERTICAL : GeneratorType
        Vertical downward expansion.
    WOODEN_PLATFORM : GeneratorType
        Wooden-platform expansion with length-zero special behavior.
    """

    HORIZONTAL = 0
    VERTICAL = 1  # vertical downward
    DIAG_DOWN_LEFT = 2
    DESERT_PIPE_BOX = 3
    DIAG_DOWN_RIGHT = 4
    DIAG_UP_RIGHT = 5
    HORIZ_TO_GROUND = 6
    HORIZONTAL_2 = 7  # special case of horizontal, floating boxes, ceilings
    DIAG_WEIRD = 8  #
    SINGLE_BLOCK = 9
    CENTERED = 10  # like spinning platforms
    PYRAMID_TO_GROUND = 11  # to the ground or next object
    PYRAMID_2 = 12  # doesn't exist
    TO_THE_SKY = 13
    ENDING = 14
    BRICK_WALL = 15
    DIAG_STAGGERED = 16
    WOODEN_PLATFORM = 17  # special expansion rules and infinite expansion when length 0


class EndType(Enum):
    """Some level objects have blocks designated to be used at their ends. For example, pipes, which can be extended but
    always end at one side with the same couple of blocks. To keep track of where those special blocks are to be placed,
    this enum is used. When the value is TWO_ENDS, they are always on opposite sides, and whether they are left and
    right or top and bottom depends on the generator type of the object.

    The enum tells renderers whether an object's block pattern is uniform or
    needs special cap blocks at one or both ends.

    The data flow is parallel to ``GeneratorType``: ``objects.dat`` names an
    ending rule, ``ObjectDefinition`` stores it, and render logic uses it to
    decide whether special terminal blocks are injected at one side, both
    sides, or not at all.

    Notes
    -----
    The data flow is ``objects.dat`` -> ``ObjectDefinition.ending`` -> render
    logic that decides whether cap tiles are injected at one side, both sides,
    or not at all.
    Keeping this as symbolic metadata lets preview and rendering code share one
    notion of where special terminal tiles belong, rather than scattering
    cap-placement rules across individual object handlers.

    See Also
    --------
    GeneratorType
        Describes the overall block-expansion pattern.
    ObjectDefinition
        Stores the end behavior chosen for each parsed object entry.

    Attributes
    ----------
    BOTTOM_OR_RIGHT : EndType
        End cap belongs on the bottom or right side.
    TOP_OR_LEFT : EndType
        End cap belongs on the top or left side.
    TWO_ENDS : EndType
        End caps belong on opposite sides.
    UNIFORM : EndType
        No special end cap blocks are needed.
    """

    UNIFORM = 0
    TOP_OR_LEFT = 1
    BOTTOM_OR_RIGHT = 2
    TWO_ENDS = 3


class ObjectDefinition:
    """An object's data, like height, width, and which blocks it uses are information that is not stored in any look-up
    tables in the ROM, rather it is the result of generator code, written for many dozen different objects.

    To make this easier to emulate, we have the objects.dat (formerly data.dat) file from Workshop, listing all objects
    and their properties, which we can use to abstract away the drawing.

    The object definition bundles this information so Foundry can render,
    preview, and edit objects without reimplementing every ROM-side generator
    routine from scratch.

    One instance becomes the stable metadata record for an object id: object
    sets load it, factories consult it while decoding bytes, and renderers use
    it to choose dimensions, generator behavior, and preview blocks.

    Parameters
    ----------
    string : str
        One comma-separated object definition line from ``objects.dat``.

    Attributes
    ----------
    block_indexes : list[int]
        Block ids listed by ``objects.dat`` for preview rendering.
    bmp_height : int
        Nominal preview height in blocks.
    bmp_width : int
        Nominal preview width in blocks.
    description : str
        Human-readable object name.
    ending : EndType
        End-cap placement rule.
    generator_type : GeneratorType
        Expansion rule used by the renderer.
    is_4byte : bool
        Whether this object uses SMB3's four-byte object encoding.
    object_design_length : int
        Number of block ids in the object design.
    rom_block_indexes : list[int]
        ROM-resolved block ids filled by object rendering code.

    Notes
    -----
    One ``ObjectDefinition`` starts as a parsed ``objects.dat`` row, then flows
    through ``ObjectSet``, object factories, and renderers as the stable
    metadata description for that SMB3 object id. It is the point where
    generator semantics, end-cap semantics, dimensions, and preview block ids
    are unified into one editor-facing record.
    This class intentionally stays as parsed metadata. Once one row has been
    normalized here, the rest of the editor can ask one object for "how should
    this id expand, how large is the preview, and which blocks represent it"
    without caring how those answers were encoded in the source file.
    Its workflow value is that object-set loading performs the parsing once,
    after which decoding and rendering can share the same normalized state.

    See Also
    --------
    GeneratorType
        Expansion rule stored on each definition.
    EndType
        End-cap behavior stored on each definition.

    Examples
    --------
    A parsed row becomes typed metadata that preserves the source-file data
    shape while removing string parsing from downstream renderers:

    >>> row = "0, 0, 0, 2, 1, SINGLE_BLOCK, UNIFORM, 4byte, Brick, <$12, $13>"
    >>> definition = ObjectDefinition(row)
    >>> (
    ...     definition.bmp_width,
    ...     definition.bmp_height,
    ...     definition.generator_type.name,
    ...     definition.ending.name,
    ...     definition.is_4byte,
    ...     definition.block_indexes,
    ... )
    (2, 1, 'SINGLE_BLOCK', 'UNIFORM', True, [18, 19])
    """

    def __init__(self, string):
        """Parse one ``objects.dat`` definition line.

        The source file describes object dimensions, generator behavior,
        four-byte encoding, display text, and block ids in a compact
        comma-separated format. Parsing happens once when this module is loaded,
        after which the resulting metadata record is reused by object sets,
        factories, and renderers as the editor's stable description of that
        object id. The constructor is therefore the normalization step that
        turns Workshop-style source text into typed metadata fields the rest of
        Foundry can safely branch on without reparsing or string matching. It
        fills the cached dimensions, generator metadata, end-cap metadata, and
        preview block ids that downstream decode and render paths expect to be
        ready immediately after module load.

        Parameters
        ----------
        string : str
            One comma-separated object definition line from ``objects.dat``.

        Examples
        --------
        The constructor normalizes one source row into typed fields that the
        rest of the editor can consume without reparsing:

        >>> row = "0, 0, 0, 1, 2, VERTICAL, TOP_OR_LEFT, -, Pipe Top|0 1 0, <$24>"
        >>> definition = ObjectDefinition(row)
        >>> (
        ...     definition.description,
        ...     definition.generator_type is GeneratorType.VERTICAL,
        ...     definition.ending is EndType.TOP_OR_LEFT,
        ...     definition.block_indexes,
        ... )
        ('Pipe Top', True, True, [36])
        """
        string = string.rstrip().replace("<", "").replace(">", "")

        (
            _domain,  # unused
            _min_value,  # unused
            _max_value,  # unused
            bmp_width,
            bmp_height,
            generator_name,
            ending_name,
            is_4byte_str,
            description,
            *png_block_indexes_str,
        ) = apply(str.strip, string.split(","))

        self.bmp_width = int(bmp_width)
        self.bmp_height = int(bmp_height)
        self.generator_type = GeneratorType[generator_name]
        self.ending = EndType[ending_name]
        self.is_4byte = is_4byte_str == "4byte"
        self.description = description.replace(";;", ",")

        self.block_indexes = apply(dollar_hex_to_int, png_block_indexes_str)

        self.object_design_length = len(self.block_indexes)
        self.rom_block_indexes = [0] * self.object_design_length

        self.description = self.description.split("|")[0]

    def __repr__(self):
        """Expose the object name in a compact debug string.

        The representation stays intentionally compact because it is used as a
        developer hint when inspecting definition tables, not as a serialized
        or user-facing description.

        Returns
        -------
        str
            Short debug label containing the object description.
        """
        return f"ObjectDefinition: {self.description}"


object_def_tables: list[list[ObjectDefinition]] = [[]]
# TODO Why x and x2?
enemy_handle_x = []
enemy_handle_x2 = []
enemy_handle_y = []

# TODO make into a function and reloadable?
with open(data_dir.joinpath("objects.dat"), "r") as f:
    bank_index = 0
    obj_index = 0

    for line in f.readlines():
        if line.startswith(";"):  # is a comment
            continue

        if line.rstrip() == "":
            # a new "bank" of objects starts
            object_def_tables.append([])

            bank_index += 1
            obj_index = 0
            continue

        object_def_tables[bank_index].append(ObjectDefinition(line))

        # enemies can have additional offsets, so they are shown in the expected position in the editor
        if bank_index == ENEMY_ITEM_OBJECT_SET:

            if "|" in line:
                after_bar = line.split("|")[1]
                before_block_indexes = after_bar.split(", <")[0]
                x, y, x2 = apply(int, before_block_indexes.split(" "))

            else:
                x = y = x2 = 0

            enemy_handle_x.append(x)
            enemy_handle_x2.append(x2)
            enemy_handle_y.append(y)

        obj_index += 1

    while len(enemy_handle_x) < 0xFF:
        enemy_handle_x.append(0)
        enemy_handle_x2.append(0)
        enemy_handle_y.append(0)


# TODO: After deduplicating the definitions and the object sets, can probably be removed
@lru_cache(2**4)
def load_object_definitions(object_set_number):
    """Return object definitions for an object set.

    Definitions are parsed from ``objects.dat`` at module load time and grouped
    by object-set bank.

    Parameters
    ----------
    object_set_number : int
        Object set number that selects graphics and object definitions.

    Returns
    -------
    list[ObjectDefinition]
        Definitions indexed by object id.
    """
    global object_def_tables

    object_def_table = object_def_tables[object_set_number]

    return object_def_table
