"""Decode SMB3 terrain-object bytes into editable Foundry level objects.

This module is the main bridge between compact level-object records in SMB3's
object stream and the richer geometry, rendering, and serialization state that
Foundry edits in memory. It keeps object-set metadata, encoded positions,
generator behavior, and rendered block footprints aligned so selection, drag,
resize, and save workflows can all operate on one editor-facing object model.

See Also
--------
foundry.game.gfx.objects.in_level.level_object_factory
    Builds ``LevelObject`` instances from bytes or explicit editor properties.
foundry.game.gfx.objects.in_level.object_renderer
    Expands the decoded object state into rendered block geometry.
"""

from warnings import warn

from foundry.game import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, GROUND
from foundry.game.File import ROM
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.object_renderer import (
    LevelObjectRenderWarning,
    ObjectRenderer,
)
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.ObjectDefinitions import EndType, GeneratorType
from foundry.game.ObjectSet import ObjectSet
from smb3parse.levels import LEVEL_SCREEN_HEIGHT, LEVEL_SCREEN_WIDTH
from smb3parse.util import clamp
from smb3parse.util.rect import Rect

ENDING_STR = {
    EndType.UNIFORM: "Uniform",
    EndType.TOP_OR_LEFT: "Top or Left",
    EndType.BOTTOM_OR_RIGHT: "Bottom or Right",
    EndType.TWO_ENDS: "Top & Bottom/Left & Right",
}

GENERATOR_TYPE_TO_STR = {
    GeneratorType.HORIZONTAL: "Horizontal",
    GeneratorType.VERTICAL: "Vertical",
    GeneratorType.DIAG_DOWN_LEFT: "Diagonal ↙",
    GeneratorType.DESERT_PIPE_BOX: "Desert Pipe Box",
    GeneratorType.DIAG_DOWN_RIGHT: "Diagonal ↘",
    GeneratorType.DIAG_UP_RIGHT: "Diagonal ↗",
    GeneratorType.HORIZ_TO_GROUND: "Horizontal to the Ground",
    GeneratorType.HORIZONTAL_2: "Horizontal Alternative",
    GeneratorType.DIAG_WEIRD: "Diagonal Weird",  # up left?
    GeneratorType.SINGLE_BLOCK: "Single Block",
    GeneratorType.CENTERED: "Centered",
    GeneratorType.PYRAMID_TO_GROUND: "Pyramid to Ground",
    GeneratorType.PYRAMID_2: "Pyramid Alternative",
    GeneratorType.TO_THE_SKY: "To the Sky",
    GeneratorType.ENDING: "Ending",
    GeneratorType.BRICK_WALL: "Brick Wall",
    GeneratorType.WOODEN_PLATFORM: "Wooden Platform",
}


# TODO: Get all the graphic information out of here. It makes testing and pickling these objects a pain
class LevelObject(InLevelObject):
    """Model one editable SMB3 terrain object from the level object stream.

    ``LevelObject`` is the bridge between raw object bytes and the editor's
    geometry-driven view of a level. It decodes position, generator metadata,
    dimensions, and four-byte length fields from the object stream, then keeps
    those values synchronized with rendered blocks, hit-test bounds, and
    serialization back to ROM bytes.

    Parameters
    ----------
    data : bytearray
        Raw bytes or bytearray being parsed.
    object_set : int
        Object set that controls tiles, graphics, or level object behavior.
    palette_group : PaletteGroup
        Palette group used for drawing the object.
    graphics_set : GraphicsSet
        Graphics set used to draw object previews.
    objects_ref : list['LevelObject']
        Sibling level objects used for rendering and expansion checks.
    is_vertical : bool
        Whether the object belongs to a vertical level layout.
    index : int
        Zero-based index of the item to access.
    size_minimal : bool, optional
        Whether object sizes should use minimal bounds.

    Attributes
    ----------
    _bytes : bytearray
        Cached byte representation written back to the object stream.
    _bytes_dirty : bool
        Whether the cached serialized bytes need to be rebuilt.
    _domain : int
        Domain value decoded from the first object byte.
    _is_4byte : bool
        Whether the object uses SMB3's four-byte encoding.
    _length : int
        Primary expansion length stored by the encoding.
    _rendered_base_x : int
        Leftmost rendered x coordinate after expansion offsets.
    _rendered_width : int
        Rendered width in blocks after expansion.
    _x_position : int
        Encoded x coordinate before rendered offsets are applied.
    _y_position : int
        Encoded y coordinate before rendered offsets are applied.
    block_cache : dict[int, Block]
        Lazily created block images keyed by block index.
    blocks : list[int]
        Base block indexes from the object definition.
    data : bytearray
        Raw object bytes backing this editable level object.
    ending : EndType
        End-cap behavior from the object definition.
    generator_type : GeneratorType
        Expansion rule from the object definition.
    graphics_set : GraphicsSet
        Graphics set used to resolve rendered blocks and object previews.
    ground_level : int
        Ground row used by expansion rules that extend objects downward.
    height : int
        Nominal preview height from the object definition.
    index_in_level : int
        Position of this object in the level object list.
    is_fixed : bool
        Whether the object is constrained by fixed placement or sizing rules.
    name : str
        Human-readable object name from the definition file.
    object_set : foundry.game.ObjectSet.ObjectSet
        Object set that supplies definitions, graphics, and expansion rules.
    objects_ref : list[foundry.game.gfx.objects.in_level.level_object.LevelObject]
        Sibling level objects used for expansion checks and renderer context.
    palette_group : PaletteGroup
        Palette group used when drawing this object.
    rect : Rect
        Rendered bounds used for hit testing and selection.
    rendered_base_y : int
        Y coordinate of the rendered block origin after expansion adjustments.
    rendered_blocks : list[int]
        Block indexes produced by the renderer for drawing and inspection.
    rendered_height : int
        Rendered height in blocks after expansion.
    secondary_length : int
        Additional length value used by object types with two dimensions.
    selected : bool
        Whether the object is currently selected in the editor.
    size_minimal : bool
        Whether size calculations use the minimal object bounds.
    tsa_data : bytes
        Tile set assembly data used to translate block indexes into graphics.
    type : int
        Type id exposed to generic editor code.
    vertical_level : bool
        Whether coordinates are interpreted with vertical level layout rules.
    width : int
        Nominal preview width from the object definition.

    Notes
    -----
    ``LevelObject`` exists so the rest of the editor can work in terms of
    object geometry and rendered blocks while still preserving the original
    SMB3 byte encoding. Factories decode bytes once, this object owns the
    editable state, and ``ObjectRenderer`` recalculates the visual footprint
    when that state changes.

    Examples
    --------
    Most editor workflows decode bytes once, mutate the in-memory object, then
    serialize the updated state back into the level stream::

        factory = LevelObjectFactory(1, palette_group, graphics_set, objects_ref=[], vertical_level=False)
        obj = factory.from_data(bytearray([0x00, 0x10, 0x20]), index=0)

        start_xy = obj.get_rendered_position()
        obj.move_by(1, 0)
        end_xy = obj.get_rendered_position()
        payload = obj.to_bytes()

    The example uses :class:`LevelObjectFactory` because most editor workflows
    do not construct ``LevelObject`` directly; they decode bytes once with the
    shared object-set, graphics-set, and palette context, then mutate the
    returned object through move, resize, and save commands.
    """

    def __init__(
        self,
        data: bytearray,
        object_set: int,
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        objects_ref: list["LevelObject"],
        is_vertical: bool,
        index: int,
        size_minimal: bool = False,
    ):
        """Decode one SMB3 object stream entry into editable state.

        The constructor turns raw level-object bytes into geometry, generator
        metadata, and renderer inputs that the rest of the editor can mutate
        without directly manipulating the object stream. It establishes the
        shared editor state first, then hands control to ``_setup`` to decode
        object-specific byte fields, normalize length state, build cached byte
        state, and trigger the first rendered-footprint calculation that later
        selection, resize, and save workflows reuse.

        Parameters
        ----------
        data : bytearray
            Raw bytes or bytearray being parsed.
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        palette_group : PaletteGroup
            Palette group used for drawing the object.
        graphics_set : GraphicsSet
            Graphics set used to draw object previews.
        objects_ref : list['LevelObject']
            Sibling level objects used for rendering and expansion checks.
        is_vertical : bool
            Whether the object belongs to a vertical level layout.
        index : int
            Zero-based index of the item to access.
        size_minimal : bool, optional
            Whether object sizes should use minimal bounds.
        """
        super(LevelObject, self).__init__()

        self.object_set = ObjectSet.from_number(object_set)

        self.graphics_set = graphics_set
        self.tsa_data = ROM.get_tsa_data(object_set)

        self._rendered_base_x = 0
        """Top left x position of the visual object after rendering. Might change for expanding types, like pyramids."""
        self.rendered_base_y = 0
        """Top left y position of the visual object after rendering. Might change for expanding types, like pyramids."""

        self.rendered_blocks: list[int] = []

        self.is_fixed = False

        self.palette_group = palette_group

        self.index_in_level = index
        self.objects_ref = objects_ref
        self.vertical_level = is_vertical

        self.data = data

        self.selected = False

        self.size_minimal = size_minimal

        if self.size_minimal:
            self.ground_level = 0
        else:
            self.ground_level = GROUND

        self._length = 0
        self.secondary_length = 0

        self._bytes = bytearray()
        self._bytes_dirty = True
        """Whether the object data has changed and we need to re-calculate the bytes representation."""

        self._setup()

    def _setup(self):
        """Decode the raw object bytes into geometry, type, and render state.

        This is the main byte-to-editor translation step used during initial
        construction and after type changes rebuild the object definition. The
        method decodes domain and position bytes, resolves the matching object
        definition, normalizes three-byte versus four-byte length state, and
        finishes by rerendering so geometry, cached bytes, and rendered bounds
        all describe the same object state.
        """
        data = self.data

        # where to look for the graphic data?
        self._domain = (data[0] & 0b1110_0000) >> 5

        # position relative to the start of the level (top)
        self._y_position = data[0] & 0b0001_1111

        # position relative to the start of the level (left)
        self._x_position = data[1]

        if self.vertical_level:
            offset = (self.x_position // LEVEL_SCREEN_WIDTH) * LEVEL_SCREEN_HEIGHT

            self.y_position += offset
            self.x_position %= LEVEL_SCREEN_WIDTH

        # describes what object it is
        self._obj_index = 0x00

        self.obj_index = data[2]

        object_data = self.object_set.get_definition_of(self.type)

        self.width: int = object_data.bmp_width
        self.height: int = object_data.bmp_height
        self.generator_type: GeneratorType = GeneratorType(object_data.generator_type)
        self.ending: EndType = EndType(object_data.ending)
        self.name = object_data.description

        self._rendered_width = self.width
        self.rendered_height = self.height

        # the building blocks, not necessarily all the blocks that need to be drawn
        self.blocks: list[int] = object_data.block_indexes.copy()

        self.block_cache: dict[int, Block] = {}

        self._is_4byte = object_data.is_4byte

        if self.is_4byte and len(self.data) == 3:
            self.data.append(0)
        elif not self.is_4byte and len(data) == 4:
            del self.data[3]

        self._length = 0
        self.secondary_length = 0

        self._calculate_lengths()

        self.rect = Rect()

        self._render()

    # Most of these properties enable us to cache the to_bytes result, since it gets called a lot
    @property
    def x_position(self):
        """Encoded object-stream x coordinate.

        The renderer and serializer both derive their horizontal state from
        this stored coordinate.

        Returns
        -------
        int
            Horizontal coordinate before rendered offsets are applied.
        """
        return self._x_position

    @x_position.setter
    def x_position(self, value):
        """Store the encoded object-stream x coordinate.

        Parameters
        ----------
        value : int
            Horizontal coordinate before rendered offsets are applied.
        """
        self._x_position = value
        self._bytes_dirty = True

    @property
    def y_position(self):
        """Encoded object-stream y coordinate.

        The renderer and serializer both derive their vertical state from this
        stored coordinate.

        Returns
        -------
        int
            Vertical coordinate before rendered offsets are applied.
        """
        return self._y_position

    @y_position.setter
    def y_position(self, value):
        """Store the encoded object-stream y coordinate.

        Parameters
        ----------
        value : int
            Vertical coordinate before rendered offsets are applied.
        """
        self._y_position = value
        self._bytes_dirty = True

    @property
    def rendered_base_x(self):
        """Left edge of the rendered object footprint.

        Expansion rules can shift the rendered origin away from the encoded
        coordinate, so selection and dragging use this value instead.

        Returns
        -------
        int
            Horizontal coordinate used for drawing and hit testing.
        """
        return self._rendered_base_x

    @rendered_base_x.setter
    def rendered_base_x(self, value):
        """Store the left edge of the rendered object footprint.

        Parameters
        ----------
        value : int
            Horizontal coordinate used for drawing and hit testing.
        """
        self._rendered_base_x = value
        self._bytes_dirty = True

    @property
    def rendered_width(self):
        """Width of the rendered footprint in blocks.

        The rendered width may differ from the definition preview width after
        generator rules expand the object, so editor selection, hit testing,
        and drawing use this rendered value rather than the raw definition
        width stored earlier in the decode workflow.

        Returns
        -------
        int
            Rendered width in block units.
        """
        return self._rendered_width

    @rendered_width.setter
    def rendered_width(self, value):
        """Store the rendered footprint width.

        Parameters
        ----------
        value : int
            Rendered width in block units.
        """
        self._rendered_width = value
        self._bytes_dirty = True

    @property
    def is_4byte(self):
        """Whether the object uses SMB3's four-byte encoding.

        This flag controls whether a separate length byte is preserved during
        editing and serialization.

        Returns
        -------
        bool
            ``True`` when the object stores an additional length byte.
        """
        return self._is_4byte

    @is_4byte.setter
    def is_4byte(self, value):
        """Store whether the object uses SMB3's four-byte encoding.

        Parameters
        ----------
        value : bool
            Whether the object stores an additional length byte.
        """
        self._is_4byte = value
        self._bytes_dirty = True

    @property
    def domain(self):
        """SMB3 object domain decoded from the first byte.

        Domain changes retarget object-definition lookup and therefore affect
        rendering, resizing, and serialization throughout the editor pipeline.
        It is the first piece of decoded state that redirects later type,
        definition, and generator lookups.

        Returns
        -------
        int
            Domain used to derive the effective object type.
        """
        return self._domain

    @domain.setter
    def domain(self, value):
        """Store the SMB3 object domain.

        Parameters
        ----------
        value : int
            Domain used to derive the effective object type.
        """
        self._domain = value
        self._bytes_dirty = True

    @property
    def obj_index(self):
        """Raw object-stream type byte.

        Combined with ``domain``, this byte determines which object definition
        and generator rules apply when the object is rendered or rewritten. It
        is the byte-level input that the setup and type-change workflow convert
        into the effective editor-visible object type.

        Returns
        -------
        int
            Encoded object index before domain expansion.
        """
        return self._obj_index

    @obj_index.setter
    def obj_index(self, value):
        """Store the raw object-stream type byte and refresh derived state.

        Parameters
        ----------
        value : int
            Encoded object index before domain expansion.
        """
        self._obj_index = value

        self.is_fixed = self.obj_index <= 0x0F

        domain_offset = self.domain * 0x1F

        if self.is_fixed:
            self.type = self.obj_index + domain_offset
        else:
            self.type = (self.obj_index >> 4) + domain_offset + 16 - 1

        self._bytes_dirty = True

    @property
    def object_info(self):
        """Tuple identifying the object's definition lookup.

        Inspector and debug tooling use this condensed identifier instead of
        reaching into several separate properties, and renderer helpers use it
        for special-case SMB3 object handling. The tuple is the compact
        handoff that carries lookup state between decoded object metadata and
        downstream renderer or inspector workflows.

        Returns
        -------
        tuple[int, int, int]
            Object-set number, domain, and raw object index.
        """
        return self.object_set.number, self.domain, self.obj_index

    @property
    def length(self):
        """Primary encoded expansion length.

        This value is serialized back into the object stream and also drives
        renderer expansion for many generator types.

        Returns
        -------
        int
            Length value used by the object's primary expansion rule.
        """
        return self._length

    @length.setter
    def length(self, value):
        """Store the primary encoded expansion length.

        Parameters
        ----------
        value : int
            Length value used by the object's primary expansion rule.
        """
        if not self.is_4byte and not self.is_fixed:
            self._obj_index &= 0xF0
            self._obj_index |= value & 0x0F

        self._length = value

        self._bytes_dirty = True

    def copy(self):
        """Create a duplicate from the object's serialized state.

        Copying through ``to_bytes`` preserves the exact encoded form rather
        than duplicating only the derived geometry.

        Returns
        -------
        LevelObject
            Duplicate with the same bytes and rendering context.
        """
        return LevelObject(
            self.to_bytes(),
            self.object_set.number,
            self.palette_group,
            self.graphics_set,
            self.objects_ref,
            self.vertical_level,
            self.index_in_level,
            self.size_minimal,
        )

    def _calculate_lengths(self):
        """Derive editable length fields from the encoded bytes.

        Fixed, three-byte, and four-byte objects expose their size differently,
        so this helper normalizes those encodings into editable attributes.
        """
        if self.is_fixed:
            self._length = 1
        else:
            self._length = self.obj_index & 0b0000_1111

        if self.is_4byte:
            self.secondary_length = self.length
            self.length = self.data[3]

    def render(self):
        """Recalculate rendered blocks and bounds for the object.

        Editor workflows call this after geometry-affecting edits when they
        need the visual footprint refreshed immediately.
        """
        self._render()

    def _render(self):
        """Ask ``ObjectRenderer`` to rebuild the object's footprint.

        Rendering warnings are downgraded to Python warnings so bad objects can
        still stay visible in the editor.
        """
        try:
            ObjectRenderer(self).render()
        except LevelObjectRenderWarning as lorw:
            warn(lorw)

    def set_position(self, x, y):
        # todo also check for the upper bounds
        """Move the object to a rendered position and re-render it.

        Movement starts from rendered coordinates because many SMB3 generators
        shift their visible footprint away from the raw encoded origin. The
        method translates that rendered move back into encoded coordinates, then
        rerenders to refresh the object's footprint.

        Parameters
        ----------
        x : int
            Target rendered x coordinate.
        y : int
            Target rendered y coordinate.
        """
        x = max(0, x)

        if self.generator_type == GeneratorType.TO_THE_SKY:
            y = self.rendered_base_y + y
        else:
            y = max(0, y)

        # we move the rendered objects, so get the diff and apply it to the data position
        dx = int(x) - self.rendered_base_x
        dy = int(y) - self.rendered_base_y

        self.x_position += dx
        self.y_position += dy

        self._render()

        if self.generator_type in (GeneratorType.PYRAMID_TO_GROUND, GeneratorType.PYRAMID_2):
            # rendered_base_x is dependent on the height, so after the initial render we need to adjust it based on that

            dx = int(x) - self.rendered_base_x
            self.x_position += dx

            self._render()

    def move_by(self, dx: int, dy: int):
        """Offset the rendered object position by the supplied delta.

        Dragging and keyboard nudging operate on the rendered origin, then
        delegate the actual byte-aligned move through ``set_position``. That
        keeps the movement workflow expressed in rendered coordinates while the
        underlying byte state and rerender step stay centralized in one place.

        Parameters
        ----------
        dx : int
            Horizontal offset.
        dy : int
            Vertical offset.

        Examples
        --------
        Dragging tools usually work in rendered coordinates rather than raw
        object-stream coordinates:

        >>> start_x, start_y = obj.get_rendered_position()  # doctest: +SKIP
        >>> obj.move_by(2, 1)  # doctest: +SKIP
        >>> obj.get_rendered_position() == (start_x + 2, start_y + 1)  # doctest: +SKIP
        True
        """
        new_x = self.rendered_base_x + dx
        new_y = self.rendered_base_y + dy

        if dx == dy == 0:
            return

        self.set_position(new_x, new_y)

    def get_position(self):
        """Rendered position used by selection and drag workflows.

        This mirrors the generic object API expected by the rest of the editor
        rather than exposing the raw encoded coordinates.

        Returns
        -------
        tuple[int, int]
            Rendered x and y coordinates.
        """
        return self.rendered_base_x, self.rendered_base_y

    def get_rendered_position(self):
        """Rendered top-left draw position.

        The method is explicit for callers that want draw-space coordinates
        without depending on the generic ``get_position`` contract.

        Returns
        -------
        tuple[int, int]
            Rendered x and y coordinates.
        """
        return self.rendered_base_x, self.rendered_base_y

    def get_data_position(self):
        """Encoded position stored in the object stream.

        This is the coordinate pair that will be written back into ROM bytes.

        Returns
        -------
        tuple[int, int]
            Serialized x and y coordinates before rendered offsets.
        """
        return self.x_position, self.y_position

    def expands(self):
        """Describe which expansion workflow axes apply to this object.

        Expansion depends on the generator type and whether the object uses
        the extended four-byte encoding. Callers use this shared result to
        decide which resize gestures and length fields should stay active for
        this object state.

        Returns
        -------
        int
            Expansion bitmask composed from ``EXPANDS_*`` constants.
        """
        expands = EXPANDS_NOT

        if self.is_fixed:
            return expands

        if self.is_4byte:
            expands |= EXPANDS_BOTH

        elif (
            self.generator_type
            in [
                GeneratorType.HORIZONTAL,
                GeneratorType.HORIZONTAL_2,
                GeneratorType.HORIZ_TO_GROUND,
                GeneratorType.WOODEN_PLATFORM,
            ]
            or self.generator_type
            in [
                GeneratorType.DIAG_DOWN_LEFT,
                GeneratorType.DIAG_DOWN_RIGHT,
                GeneratorType.DIAG_UP_RIGHT,
                GeneratorType.DIAG_WEIRD,
            ]
            or self.generator_type == GeneratorType.DESERT_PIPE_BOX
        ):
            expands |= EXPANDS_HORIZ

        elif self.generator_type in [GeneratorType.VERTICAL, GeneratorType.DIAG_WEIRD]:
            expands |= EXPANDS_VERT

        return expands

    def primary_expansion(self):
        """Describe which axis owns the object's primary length state.

        Some generators switch their primary axis when encoded as four-byte
        objects, so the answer is not purely definition-driven. Resize code
        uses this decision point to route editor drag state into the correct
        encoded length field before rerendering.

        Returns
        -------
        int
            Expansion flag describing the primary resize direction.
        """
        if (
            self.generator_type
            in [
                GeneratorType.HORIZONTAL,
                GeneratorType.HORIZONTAL_2,
                GeneratorType.HORIZ_TO_GROUND,
                GeneratorType.WOODEN_PLATFORM,
            ]
            or self.generator_type
            in [
                GeneratorType.DIAG_DOWN_LEFT,
                GeneratorType.DIAG_DOWN_RIGHT,
                GeneratorType.DIAG_UP_RIGHT,
                GeneratorType.DIAG_WEIRD,
            ]
            or self.generator_type == GeneratorType.DESERT_PIPE_BOX
        ):
            if self.is_4byte:
                return EXPANDS_VERT
            else:
                return EXPANDS_HORIZ
        elif self.generator_type == GeneratorType.VERTICAL:
            if self.is_4byte:
                return EXPANDS_HORIZ
            else:
                return EXPANDS_VERT
        else:
            return EXPANDS_BOTH

    def resize_x(self, x: int):
        """Resize the object from an x coordinate and re-render it.

        Horizontal resizing updates either the packed nibble in byte three or
        the dedicated fourth-byte length, depending on the object's encoding.

        Parameters
        ----------
        x : int
            Horizontal coordinate.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if self.expands() & EXPANDS_HORIZ == 0:
            return

        if self.primary_expansion() == EXPANDS_HORIZ:
            length = x - self.x_position

            length = clamp(0, length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.data[2] = self.obj_index
        else:
            length = clamp(0, x - self.x_position, 0xFF)

            if self.is_4byte:
                self.data[3] = length
            else:
                raise ValueError("Resize impossible", self)

        self._calculate_lengths()

        self._render()

    def resize_y(self, y: int):
        """Resize the object from a y coordinate and re-render it.

        Vertical resizing updates either the packed nibble in byte three or the
        dedicated fourth-byte length, depending on the object's encoding.

        Parameters
        ----------
        y : int
            Vertical coordinate.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if self.expands() & EXPANDS_VERT == 0:
            return

        if self.primary_expansion() == EXPANDS_VERT:
            length = y - self.y_position

            length = clamp(0, length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.data[2] = self.obj_index
        else:
            length = clamp(0, y - self.y_position, 0xFF)

            if self.is_4byte:
                self.data[3] = length
            else:
                raise ValueError("Resize impossible", self)

        self._calculate_lengths()

        self._render()

    def resize_by(self, dx: int, dy: int):
        """Resize the object by rendered-coordinate deltas.

        Special-case generators such as desert pipe boxes translate cursor
        movement into coarser encoded growth steps before resizing.

        Parameters
        ----------
        dx : int
            Horizontal offset.
        dy : int
            Vertical offset.
        """
        if self.generator_type == GeneratorType.DESERT_PIPE_BOX:
            # pipe boxes are really wide.
            # if we use the normal code, for every one block the cursor moves, a whole segment is added.
            # divide the movement by the width of a segment, so you need to move that many blocks, before one is added.
            is_pipe_box_type_b = self.obj_index // 0x10 == 4

            if is_pipe_box_type_b:
                dx = (dx // 14) - 1
            else:
                dx = (dx // 16) - 1

        if dx:
            self.resize_x(self.x_position + dx)

        if dy:
            self.resize_y(self.y_position + dy)

    def increment_type(self):
        """Advance to the next object type in domain order."""
        self.change_type(True)

    def decrement_type(self):
        """Move to the previous object type in domain order."""
        self.change_type(False)

    def change_type(self, increment: bool):
        """Cycle the object type forward or backward and re-decode it.

        The operation wraps across domains when needed and then reruns
        ``_setup`` so the new definition refreshes geometry and render state.

        Parameters
        ----------
        increment : bool
            ``True`` to move forward, ``False`` to move backward.
        """
        if self.obj_index < 0x10 or self.obj_index == 0x10 and not increment:
            value = 1
        else:
            self.obj_index = self.obj_index // 0x10 * 0x10
            value = 0x10

        if not increment:
            value *= -1

        new_type = self.obj_index + value

        if new_type < 0 and self.domain > 0:
            new_domain = self.domain - 1
            new_type = 0xF0
        elif new_type > 0xFF and self.domain < 7:
            new_domain = self.domain + 1
            new_type = 0x00
        else:
            new_type = clamp(0, new_type, 0xFF)

            new_domain = self.domain

        self.data[0] &= 0b0001_1111
        self.data[0] |= new_domain << 5

        self.data[2] = new_type

        self._setup()

    def get_status_info(self) -> list[tuple]:
        """Build the status rows shown by inspector-style UI.

        The list mirrors the compact geometry and generator summary shown in
        selection status surfaces, giving the Qt status workflow one place to
        read rendered geometry and SMB3 generator metadata from the object.

        Returns
        -------
        list[tuple]
            Label-value pairs summarizing geometry and generator metadata.
        """
        return [
            ("x", self.rendered_base_x),
            ("y", self.rendered_base_y),
            ("Width", self.rendered_width),
            ("Height", self.rendered_height),
            ("GeneratorType", GENERATOR_TYPE_TO_STR[self.generator_type]),
            ("Ending", ENDING_STR[self.ending]),
        ]

    def to_bytes(self) -> bytearray:
        """Serialize the object back into SMB3 object-stream bytes.

        Serialization is cached because the editor queries object bytes
        frequently during save, export, and undo workflows.

        Returns
        -------
        bytearray
            Cached SMB3 object-stream payload for this object's current state.

        Examples
        --------
        After an edit updates the object's decoded geometry, ``to_bytes``
        produces the byte payload that save and undo systems persist:

        >>> payload_before = bytes(obj.to_bytes())  # doctest: +SKIP
        >>> obj.resize_by(1, 0)  # doctest: +SKIP
        >>> payload_after = bytes(obj.to_bytes())  # doctest: +SKIP
        >>> payload_before != payload_after  # doctest: +SKIP
        True
        """
        if self._bytes_dirty:
            self._update_bytes()

        return self._bytes

    def _update_bytes(self):
        """Rebuild the cached object-stream bytes from editable state.

        The helper folds rendered-origin adjustments and vertical-level address
        rules back into the encoded byte layout used by SMB3.
        """
        data = bytearray()

        if self.vertical_level:
            # todo from vertical to non-vertical is bugged, because it
            # seems like you can't convert the coordinates 1:1
            # there seems to be ambiguity

            offset = self.y_position // LEVEL_SCREEN_HEIGHT

            x_position = self.x_position + offset * LEVEL_SCREEN_WIDTH
            y_position = self.y_position % LEVEL_SCREEN_HEIGHT
        else:
            x_position = self.x_position
            y_position = self.y_position

        if self.generator_type in [
            GeneratorType.PYRAMID_TO_GROUND,
            GeneratorType.PYRAMID_2,
        ]:
            x_position = self.rendered_base_x - 1 + self.rendered_width // 2

        data.append((self.domain << 5) | y_position)
        data.append(x_position)

        if not self.is_4byte and not self.is_fixed:
            third_byte = (self.obj_index & 0xF0) + self.length
        else:
            third_byte = self.obj_index

        data.append(third_byte)

        if self.is_4byte:
            data.append(self.length)

        self._bytes = data
        self._bytes_dirty = False

    def __repr__(self) -> str:
        """Developer-facing summary of the object's bytes and position.

        The representation is mainly used while debugging decoding and
        selection problems in the level object stream.

        Returns
        -------
        str
            Object name, serialized bytes, and encoded position.
        """
        return f"LevelObject '{self.name}'/0x{self.data.hex()} at ({self.x_position}, {self.y_position})"

    def __eq__(self, other):
        """Compare whether another object has the same bytes and list index.

        Equality uses serialized bytes plus list position so duplicate objects
        in different slots do not collapse into one identity.

        Parameters
        ----------
        other : object
            Object compared against this level object.

        Returns
        -------
        bool
            ``True`` when serialized bytes and level index both match.
        """
        if not isinstance(other, LevelObject):
            return False
        else:
            return self.to_bytes() == other.to_bytes() and self.index_in_level == other.index_in_level

    def __lt__(self, other):
        """Compare whether this object sorts before another object.

        Ordering follows the object's position in the level object list so draw
        order and serialization order stay aligned. This keeps list ordering,
        draw order, and object-stream data flow synchronized through one shared
        comparison rule.

        Parameters
        ----------
        other : LevelObject
            Level object compared against this one.

        Returns
        -------
        bool
            ``True`` when this object appears earlier in the level object list.
        """
        return self.index_in_level < other.index_in_level
