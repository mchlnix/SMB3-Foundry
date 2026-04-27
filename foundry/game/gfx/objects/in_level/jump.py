"""Represent SMB3 jump pointers inside Foundry's object-editing workflow.

This module adapts the compact jump-pointer records embedded in level object
data into an editor-facing object that can be listed, copied, serialized, and
selected alongside visible level objects. It keeps exit metadata in the same
workflow even though jump pointers do not render as terrain blocks.

See Also
--------
foundry.gui.dialogs.JumpEditor
    Dedicated UI used to inspect and edit jump-specific fields.
foundry.game.gfx.objects.in_level.in_level_object
    Shared editor-facing interface implemented by jump pointers.
"""

from PySide6.QtGui import QImage, QPainter

from foundry.game import GROUND
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from smb3parse.levels import LEVEL_SCREEN_HEIGHT, LEVEL_SCREEN_WIDTH
from smb3parse.util.rect import Rect


class Jump(InLevelObject):
    """Represent a level jump pointer object.

    Jump objects are encoded in level object data but describe where Mario exits rather than a
    drawable object. The editor keeps them in the shared object flow so they can be listed, copied,
    serialized, and edited alongside visible level objects. That keeps exit
    metadata inside the same undo, copy, and serialization boundaries as the
    rest of the level object stream without pretending that a jump pointer is a
    drawable terrain block.

    Parameters
    ----------
    data : bytearray
        Three-byte jump pointer record.

    Attributes
    ----------
    POINTER_DOMAIN : int
        Domain value that identifies jump pointer objects.
    SIZE : int
        Number of bytes in a jump pointer record.
    blocks : list
        Empty block list kept for compatibility with visible objects.
    data : bytearray
        Encoded jump pointer bytes.
    exit_action : int
        Qt action for exit.
    exit_horizontal : int
        Horizontal exit coordinate encoded in the pointer.
    exit_vertical : int
        Vertical exit coordinate encoded in the pointer.
    is_4byte : bool
        Whether the pointer uses the four-byte level-object format.
    name : str
        Display name shown in editor lists.
    screen_index : int
        Level screen containing the jump pointer.

    Examples
    --------
    Build a jump from explicit editor fields and serialize it back to bytes::

        jump = Jump.from_properties(0, 0, 4, 2)
        payload = jump.to_bytes()

    Copy-based workflows preserve the encoded pointer contract by rebuilding
    from serialized bytes instead of cloning transient editor state::

        copied_jump = jump.copy()
        assert copied_jump.to_bytes() == jump.to_bytes()
    """

    POINTER_DOMAIN = 0b111

    SIZE = 3  # bytes

    def __init__(self, data):
        """Initialize a jump pointer from encoded bytes.

        Initialization decodes the screen index, exit action, and exit coordinates from the compact
        three-byte pointer format. This is the decode boundary that turns the
        serialized exit record embedded in level object data into the editor's
        logical jump object, which can then participate in selection, copy, and
        serialization workflows without pretending to be a drawable terrain
        block.

        Parameters
        ----------
        data : bytearray
            Three-byte jump pointer record.
        """
        super(Jump, self).__init__()

        self.data = data[0 : Jump.SIZE]

        # domain: 0b1110
        # unused: 0b0001

        self.blocks = []
        self.is_4byte = False
        self.name = "Jump object"

        assert self.is_jump(data)

        self.screen_index = data[0] & 0x0F
        self.exit_vertical = (data[1] & 0xF0) >> 4
        self.exit_action = data[1] & 0x0F
        # for some reason those are flipped, meaning 5678, 1234
        self.exit_horizontal = ((data[2] & 0xF) << 4) + (data[2] >> 4)

    def copy(self):
        """Create a copy of the jump pointer.

        The copy is rebuilt from serialized bytes so undo/redo and paste workflows preserve the
        encoded pointer. Rehydrating from bytes keeps copied jumps on the same
        serialization path as pasted or reloaded jumps instead of cloning
        transient editor-only state.

        Returns
        -------
        Jump
            Copied jump pointer.
        """
        return Jump(self.to_bytes())

    def draw(self, painter: QPainter, block_length, transparent):
        """Ignore drawing for a non-visual jump pointer.

        Jump pointers are represented in lists and editors rather than drawn as
        level blocks, so the rendering path is intentionally a no-op inside the
        shared object-drawing workflow.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        block_length : int
            Rendered block size in pixels.
        transparent : bool
            Whether the object should be drawn transparently.
        """
        pass

    def change_type(self, new_type):
        """Ignore type changes for jump pointers.

        Jump pointer type is fixed by its domain bits, so level-object type
        cycling does not apply. The no-op preserves the shared in-level object
        API without allowing a jump to drift into the terrain-object workflow.

        Parameters
        ----------
        new_type : int
            Replacement type identifier.

        Examples
        --------
        Generic type-cycling tools can call this safely without changing the
        jump's encoded pointer domain::

            jump = Jump.from_properties(0, 0, 4, 2)
            jump.change_type(99)
            payload = jump.to_bytes()
        """
        pass

    def render(self):
        """Ignore render requests for a non-visual jump pointer.

        There are no block images to refresh for jump pointers, so the shared
        render hook becomes an explicit no-op that keeps jump editing in the
        logical-object path rather than the tile-rendering path.
        """
        pass

    def get_status_info(self):
        """Report that jump pointers do not populate the object status surface.

        Jump details are edited through the jump editor instead of the object
        status bar, so mixed-selection workflows treat this object as having no
        status payload. This keeps status-bar updates reserved for drawable
        level objects while jump editing stays on the dedicated jump workflow.
        """
        pass

    def resize_by(self, dx, dy):
        """Ignore resize requests for jump pointers.

        Jump pointers do not encode drawable dimensions, so resize gestures do
        not affect their serialized byte layout. Keeping resize as a no-op
        preserves the shared object API without inventing width or height
        semantics for exit metadata.

        Parameters
        ----------
        dx : int
            Horizontal offset.
        dy : int
            Vertical offset.
        """
        pass

    def increment_type(self):
        """Ignore type increment requests for jump pointers.

        Jump pointer type is fixed by its domain bits, so incrementing is a
        no-op that preserves the pointer's serialized domain.
        """
        pass

    def decrement_type(self):
        """Ignore type decrement requests for jump pointers.

        Jump pointer type is fixed by its domain bits, so decrementing is a
        no-op that preserves the pointer's serialized domain.
        """
        pass

    def as_image(self) -> QImage:
        """Reject image rendering for jump pointers.

        Jump pointers are logical exits, so the object toolbar and dropdown
        should not request a drawable preview from the shared preview workflow.

        Raises
        ------
        NotImplementedError
            Because jump pointers do not have a drawable preview image.
        """
        raise NotImplementedError("Jumps don't have any image to display.")

    def to_bytes(self):
        """Serialize the jump pointer to level object data.

        The pointer preserves the original compact byte layout so copy, undo,
        save, and export workflows hand the same three-byte record back to the
        level serializer that the decoder originally consumed.

        Returns
        -------
        bytearray
            Three-byte jump pointer record.
        """
        return self.data

    def __repr__(self):
        """Summarize jump pointer fields for debugging and logging.

        The representation includes screen, exit coordinate, and action fields useful while
        debugging pointer data.

        Returns
        -------
        str
            Developer-facing representation of the object.
        """
        return (
            f"Jump: Screen #{self.screen_index}, "
            + f"Exit ({self.exit_horizontal}, {self.exit_vertical}), "
            + f"Action #{self.exit_action}"
        )

    def __str__(self):
        """Summarize this jump for editor lists and selection readouts.

        The string identifies the source screen in list displays and other UI
        workflow surfaces that need a compact jump label.

        Returns
        -------
        str
            String representation of the object.
        """
        return f"Jump on screen #{self.screen_index}"

    @staticmethod
    def is_jump(data):
        """Identify whether raw level bytes belong to the jump-pointer domain.

        The check looks at the high domain bits used by SMB3 jump pointer objects.

        Parameters
        ----------
        data : bytearray
            Candidate object bytes.

        Returns
        -------
        bool
            True when the bytes use the jump pointer domain and should enter the
            jump decode workflow rather than terrain-object decoding.
        """
        return data[0] >> 5 == Jump.POINTER_DOMAIN

    @staticmethod
    def from_properties(screen_index, action, horiz, vert):
        """Create a jump pointer from editor fields.

        The helper packs screen, action, and exit coordinates into the same byte layout used by ROM
        object data, making it the encode boundary used when the jump editor
        turns form fields back into serialized level-object bytes.

        Parameters
        ----------
        screen_index : int
            Index of the screen.
        action : int
            Exit action identifier.
        horiz : int
            Horizontal exit coordinate.
        vert : int
            Vertical exit coordinate.

        Returns
        -------
        Jump
            Jump pointer created from explicit property values.
        """
        data = bytearray(3)

        data[0] |= 0b1110_0000
        data[0] |= screen_index

        data[1] |= vert << 4
        data[1] |= action

        data[2] |= ((horiz & 0xF) << 4) + (horiz >> 4)

        return Jump(data)

    def get_rect(self, block_length=1, vertical=False) -> Rect:
        """Describe the source-screen rectangle occupied by this jump pointer.

        The rectangle covers the source screen so selection overlays can mark
        where the jump lives in horizontal and vertical level layouts. This is
        the geometry boundary used when jump metadata participates in the same
        selection and navigation workflow as visible level objects.

        Parameters
        ----------
        block_length : int, optional
            Rendered block size in pixels.
        vertical : bool, optional
            Whether to use vertical level screen layout.

        Returns
        -------
        Rect
            Screen rectangle covered by the jump pointer.
        """
        if vertical:
            return Rect(
                0,
                block_length * (1 + LEVEL_SCREEN_HEIGHT * self.screen_index),
                block_length * LEVEL_SCREEN_WIDTH,
                block_length * LEVEL_SCREEN_HEIGHT,
            )
        else:
            return Rect(
                block_length * LEVEL_SCREEN_WIDTH * self.screen_index,
                0,
                block_length * LEVEL_SCREEN_WIDTH,
                block_length * GROUND,
            )
