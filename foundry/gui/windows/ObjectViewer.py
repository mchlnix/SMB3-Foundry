"""Object-definition inspection window for SMB3 level objects.

This module groups the object viewer window, preview canvas, decoded block
list, and per-block widgets used to inspect one generated level object at a
time. The workflow is staged object bytes and render context ->
``ObjectDrawArea`` decode -> preview canvas and block widgets rebuilt from the
same decoded object so maintainers can inspect object definitions without
modifying live level data.

See Also
--------
foundry.game.gfx.objects.in_level.level_object_factory
    Decodes the raw object bytes staged by the viewer controls.
foundry.gui.windows.BlockViewer
    Companion inspection surface for the decoded 16x16 blocks used by object
    previews.
"""

from typing import cast

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLayout,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from foundry.game.gfx.block_cache import draw_level_object, get_block
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GRAPHIC_SET_NAMES
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.in_level.level_object_factory import LevelObjectFactory
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.util import clear_layout
from foundry.gui.widgets.Spinner import Spinner
from foundry.gui.windows.CustomChildWindow import CustomChildWindow

ID_SPIN_DOMAIN = 1
ID_SPIN_TYPE = 2
ID_SPIN_LENGTH = 3
ID_OBJECT_SET_DROPDOWN = 4
ID_GFX_SET_DROPDOWN = 5

MAX_DOMAIN = 7
MAX_TYPE = 0xFF
MAX_LENGTH = 0xFF


class ObjectViewer(CustomChildWindow):
    """Inspect a single generated level object and its source blocks.

    The viewer lets maintainers vary the SMB3 domain, object id, optional
    fourth byte, object set, and graphics set, then renders the resulting object
    alongside the block ids used to compose it. Spinner and dropdown changes
    are normalized into raw object bytes, ``ObjectDrawArea`` decodes those
    bytes into a ``LevelObject``, and ``BlockArray`` rebuilds from that decoded
    object so the visual preview and block list stay in sync. In practice this
    is a small decoding lab for SMB3 objects: change one field, see the
    resulting shape and backing block sequence immediately. The class owns the
    full interaction loop: controls stage bytes and render context, the draw
    area decodes them, the block row mirrors the decoded object, and the status
    bar reports the resolved object name. The value created here is rapid
    feedback while exploring object definitions, without needing to place test
    objects into a real level first. In other words, it turns SMB3 object bytes
    into an interactive edit-preview-inspect loop.

    Notes
    -----
    This window is a sandbox for object-definition and block-cache behavior.
    Controls stage raw bytes and render context, ``ObjectDrawArea`` decodes
    them into one ``LevelObject``, and every visible output in the window is
    rebuilt from that decoded object so maintainers can inspect object semantics
    without touching live level data.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.

    Attributes
    ----------
    block_list : BlockArray
        Row of blocks used by the decoded preview object.
    drawing_area : ObjectDrawArea
        Canvas that renders the generated object.
    graphic_set_dropdown : QComboBox
        Graphics set selector.
    object_set_dropdown : QComboBox
        Object set selector.
    spin_domain : Spinner
        SMB3 object domain spinner.
    spin_length : Spinner
        Optional fourth-byte length spinner.
    spin_type : Spinner
        SMB3 object id spinner.
    status_bar : QStatusBar
        Status bar showing the decoded object's name.

    See Also
    --------
    ObjectDrawArea
        Decodes raw object bytes and renders the preview canvas.
    BlockArray
        Rebuilds the list of source blocks for the decoded preview object.
    """

    def __init__(self, parent):
        """Create the object viewer window.

        The window wires spinner controls, object and graphics-set selectors,
        the rendered preview, and the decoded block list into one inspection
        tool for SMB3 object definitions. Construction proceeds in phases:
        build the staged byte and render-context controls, create the preview
        canvas that decodes those staged values, attach the block list that
        mirrors the decoded object, then route the resolved object name into
        the status bar so every surface in the window reflects one shared
        decode result. This gives the window one staged-input -> decode ->
        preview/block/status loop that stays consistent as each control
        changes. In practice the method establishes the full feedback loop for
        the tool: controls own staged bytes, the draw area turns them into a
        decoded object, the block row mirrors that object, and the status bar
        exposes the decoded name that came out of the same pass. That is the
        lifecycle this constructor locks in: initialize one canonical render
        context, decode one starting object from it, and wire every visible
        surface to refresh from that same decode path instead of managing
        independent preview state.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        """
        super(ObjectViewer, self).__init__(parent, title="Object Viewer")

        self.spin_domain = Spinner(self, MAX_DOMAIN)
        self.spin_domain.valueChanged.connect(self.on_spin)

        self.spin_type = Spinner(self, MAX_TYPE)
        self.spin_type.valueChanged.connect(self.on_spin)

        self.spin_length = Spinner(self, MAX_LENGTH)
        self.spin_length.setDisabled(True)
        self.spin_length.valueChanged.connect(self.on_spin)

        _toolbar = QToolBar(self)

        _toolbar.addWidget(self.spin_domain)
        _toolbar.addWidget(self.spin_type)
        _toolbar.addWidget(self.spin_length)

        self.object_set_dropdown = QComboBox(_toolbar)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS[1:])
        self.object_set_dropdown.setCurrentIndex(0)

        self.graphic_set_dropdown = QComboBox(_toolbar)
        self.graphic_set_dropdown.addItems(GRAPHIC_SET_NAMES)
        self.graphic_set_dropdown.setCurrentIndex(1)

        self.object_set_dropdown.currentIndexChanged.connect(self.on_object_set)
        self.graphic_set_dropdown.currentIndexChanged.connect(self.on_graphic_set)

        _toolbar.addWidget(self.object_set_dropdown)
        _toolbar.addWidget(self.graphic_set_dropdown)

        self.addToolBar(_toolbar)

        self.drawing_area = ObjectDrawArea(self, 1)

        self.status_bar = QStatusBar(parent=self)
        self.status_bar.showMessage(self.drawing_area.current_object.name)

        self.setStatusBar(self.status_bar)

        self.drawing_area.update()

        self.block_list = BlockArray(self, self.drawing_area.current_object)

        central_widget = QWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(self.drawing_area)
        central_widget.layout().addWidget(self.block_list)

        self.setCentralWidget(central_widget)

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

    def set_object_and_graphic_set(self, object_set: int, graphics_set: int):
        """Apply object and graphics set changes to the preview.

        This keeps the combo boxes, rendered preview, block list, and status
        label aligned whenever the caller changes the render context. The
        method is the synchronization point that pushes one render-context
        change through every dependent surface in the window, from factory
        state to decoded preview object to block list and resolved name text.

        Parameters
        ----------
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        graphics_set : int
            Graphics set used to draw object previews.
        """
        self.object_set_dropdown.setCurrentIndex(object_set - 1)
        self.graphic_set_dropdown.setCurrentIndex(graphics_set)

        self.drawing_area.change_object_set(object_set)
        self.drawing_area.change_graphic_set(graphics_set)

        self.block_list.update_object(self.drawing_area.current_object)
        self.status_bar.showMessage(self.drawing_area.current_object.name)

    def on_object_set(self):
        """Use the selected object set and matching graphics set."""
        object_set = self.object_set_dropdown.currentIndex() + 1
        graphics_set = object_set

        self.set_object_and_graphic_set(object_set, graphics_set)

    def on_graphic_set(self):
        """Apply the selected graphics set to the loaded object-set preview.

        The object set stays fixed while only the CHR/TSA context changes, so
        the preview can show how one logical object decodes under different
        graphics data.
        """
        object_set = self.object_set_dropdown.currentIndex() + 1
        graphics_set = self.graphic_set_dropdown.currentIndex()

        self.set_object_and_graphic_set(object_set, graphics_set)

    def set_object(self, domain: int, obj_index: int, secondary_length: int):
        """Build object bytes and refresh the preview.

        The viewer works from raw SMB3 object bytes, so spinner changes are
        first packed into the canonical byte layout and then decoded through
        the preview canvas. The resulting decoded object is then propagated to
        the block list, optional fourth-byte control state, repaint cycle, and
        status text so the whole window continues to reflect one byte payload.

        Parameters
        ----------
        domain : int
            Object domain that determines how the object is interpreted.
        obj_index : int
            SMB3 object id.
        secondary_length : int
            Secondary length value used by the object.
        """
        object_data = bytearray(4)

        object_data[0] = domain << 5
        object_data[1] = 0
        object_data[2] = obj_index
        object_data[3] = secondary_length

        self.spin_domain.setValue(domain)
        self.spin_type.setValue(obj_index)
        self.spin_length.setValue(secondary_length)

        self.drawing_area.update_object(object_data)
        self.block_list.update_object(self.drawing_area.current_object)

        if self.drawing_area.current_object.is_4byte:
            self.spin_length.setEnabled(True)
        else:
            self.spin_length.setValue(0)
            self.spin_length.setEnabled(False)

        self.drawing_area.update()

        self.status_bar.showMessage(self.drawing_area.current_object.name)

    def on_spin(self, _):
        """Refresh the preview from spinner values.

        Parameters
        ----------
        _ : int
            Spinner value emitted by Qt.
        """
        domain = self.spin_domain.value()
        obj_index = self.spin_type.value()
        secondary_length = self.spin_length.value()

        self.set_object(domain, obj_index, secondary_length)


class ObjectDrawArea(QWidget):
    """Canvas that renders the selected generated level object.

    The draw area owns a ``LevelObjectFactory`` and keeps the rendered preview
    synchronized with the selected object, object set, and graphics set. It is
    the boundary between raw object bytes in the controls and the decoded
    ``LevelObject`` used for preview and block inspection.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    object_set : int
        Object set that controls tiles, graphics, or level object behavior.
    graphic_set : int, optional
        Graphics set used to draw object previews.
    palette_index : int, optional
        Index of the palette.

    Attributes
    ----------
    current_object : foundry.game.gfx.objects.in_level.level_object.LevelObject
        Object currently rendered by the preview.
    object_factory : LevelObjectFactory
        Factory used to decode object bytes.

    See Also
    --------
    ObjectViewer
        Owns the controls that feed bytes and render settings into this canvas.
    BlockArray
        Rebuilds from the decoded object stored here.
    """

    def __init__(self, parent, object_set, graphic_set=1, palette_index=0):
        """Create the object preview canvas.

        The canvas creates the decoding factory and immediately materializes a
        minimal object so the surrounding viewer can show a valid preview
        before the user edits any bytes.
        That gives the whole object-viewer workflow a stable starting point:
        bytes can change, the object can be re-decoded, and both preview and
        block list can keep referring to one current object.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        graphic_set : int, optional
            Graphics set used to draw object previews.
        palette_index : int, optional
            Index of the palette.
        """
        super(ObjectDrawArea, self).__init__(parent)

        self.object_factory = LevelObjectFactory(object_set, graphic_set, palette_index, [], False, size_minimal=True)

        self.current_object: LevelObject = cast(
            LevelObject, self.object_factory.from_data(bytearray([0x0, 0x0, 0x0]), -1)
        )

        self.update_object()

        self.resize(QSize())

    def change_object_set(self, object_set: int):
        """Change the factory object set and refresh the preview.

        Parameters
        ----------
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        """
        self.object_factory.set_object_set(object_set)

        self.update_object()

    def change_graphic_set(self, graphic_set: int):
        """Change the factory graphics set and refresh the preview.

        Parameters
        ----------
        graphic_set : int
            Graphics set used to draw object previews.
        """
        self.object_factory.set_graphic_set(graphic_set)
        self.update_object()

    def resize(self, arg__1, arg__2=None) -> None:
        """Resize the preview canvas to the decoded object's footprint.

        The widget tracks the decoded object's rendered dimensions instead of a
        fixed viewport so large objects expand naturally and small ones do not
        waste space.
        This resize step is part of the decode-to-preview pipeline: new bytes
        create a new object, and the preview surface reshapes itself to that
        object's rendered footprint before the next paint pass. That means the
        method is not just a Qt compatibility hook; it is the layout boundary
        that keeps preview geometry synchronized with whatever object the
        factory most recently decoded.

        Parameters
        ----------
        arg__1 : QSize | int
            Positional argument accepted for compatibility with ``QWidget``.
        arg__2 : int | None, optional
            Optional height argument accepted for compatibility with
            ``QWidget``.
        """
        if isinstance(self.current_object, Jump):
            return

        self.setMinimumSize(
            QSize(
                self.current_object.rendered_width * Block.WIDTH,
                self.current_object.rendered_height * Block.HEIGHT,
            )
        )

    def update_object(self, object_data: bytearray | LevelObject | Jump | None = None):
        """Decode object data and refresh the rendered object.

        Parameters
        ----------
        object_data : bytearray | foundry.game.gfx.objects.in_level.level_object.LevelObject | Jump | None, optional
            Raw object bytes or object whose data should be decoded.
        """
        if object_data is None:
            object_data = self.current_object.data

        elif isinstance(object_data, (LevelObject, Jump)):
            object_data = object_data.data

        obj = self.object_factory.from_data(object_data, -1)

        if isinstance(obj, Jump):
            # fixme display actual graphic
            return

        self.current_object = obj

        self.resize(QSize())
        self.update()

    def paintEvent(self, event: QPaintEvent):
        """Render the decoded object preview at its in-level origin.

        The painter is translated by the rendered base offsets so the preview
        shows the same composed footprint the object would occupy in a level.
        This paint pass is the visual end of the object-viewer pipeline: raw
        bytes become a decoded ``LevelObject``, then this widget renders that
        object for side-by-side inspection with its bytes and blocks.

        Parameters
        ----------
        event : QPaintEvent
            Qt event delivered to the widget.
        """
        if not isinstance(self.current_object, LevelObject):
            return

        painter = QPainter(self)

        painter.translate(
            QPoint(
                -Block.WIDTH * self.current_object.rendered_base_x,
                -Block.HEIGHT * self.current_object.rendered_base_y,
            )
        )

        # !!! Can't animate here, because we'd have to redraw the object in sync with the level
        # Could be done but eh...
        draw_level_object(self.current_object, painter, Block.WIDTH, True, False)


class BlockArray(QWidget):
    """Display the block ids used by a generated level object.

    The row is rebuilt whenever the object changes so maintainers can inspect
    the decoded block sequence behind the rendered object. That makes the
    widget the inspection half of the object viewer: ``ObjectDrawArea`` shows
    the composed shape, while this class exposes the exact block sequence that
    came out of decoding and rendering. Keeping both views side by side makes
    it much easier to connect SMB3 object definitions, TSA/block data, and the
    final previewed geometry. This is especially useful when a preview "looks
    wrong": the block row reveals whether the issue comes from object decoding,
    block lookup, palette/graphics context, or only from how the composed
    object is drawn.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this object.
    level_object : foundry.game.gfx.objects.in_level.level_object.LevelObject
        Level object being displayed or modified.

    Attributes
    ----------
    level_object : foundry.game.gfx.objects.in_level.level_object.LevelObject
        Object whose decoded blocks are displayed.

    See Also
    --------
    ObjectDrawArea
        Produces the decoded ``LevelObject`` that this widget mirrors as a
        block sequence.
    BlockArea
        Per-block widget used to render each decoded block entry.

    Notes
    -----
    This widget deliberately rebuilds from the decoded object instead of
    caching independent block state. That keeps the block list trustworthy as
    a debugging aid when object bytes, graphics sets, or object sets change.
    """

    def __init__(self, parent, level_object: LevelObject):
        """Create a block row for an object.

        The widget starts by establishing a horizontal container with no extra
        margins, stores the decoded object currently being inspected, and then
        immediately rebuilds the row from that object's block sequence so the
        viewer opens with block inspection already synchronized to the preview.
        That keeps the block row as a direct mirror of the decoded object shown
        in ``ObjectDrawArea`` rather than a second source of truth. The
        constructor therefore finishes the decode-to-inspection pipeline by
        binding one decoded object instance to the widgets that expose its
        backing block sequence, and every later object change flows back
        through ``update_object`` to keep that mirror intact. In other words,
        the constructor establishes the persistent mirror between the decoded
        preview object and the row of block widgets rebuilt from it. The state
        created here is the state later consumed by ``update_object``: one
        decoded object instance, one layout that will be cleared and rebuilt
        from that object, and one widget tree that stays synchronized with each
        later decode pass. In lifecycle terms, this is the handoff where the
        object-decoding pipeline stops producing model data and the inspection
        pipeline starts owning that data as a row of widgets that later refresh
        cycles replace from the same decoded source.

        Parameters
        ----------
        parent : object
            Parent Qt widget that owns this object.
        level_object : foundry.game.gfx.objects.in_level.level_object.LevelObject
            Level object being displayed or modified.
        """
        super(BlockArray, self).__init__(parent)

        self.setLayout(QHBoxLayout())

        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.level_object = level_object

        self.update_object(level_object)

    def update_object(self, level_object: LevelObject):
        """Rebuild the row for a level object's block sequence.

        Parameters
        ----------
        level_object : foundry.game.gfx.objects.in_level.level_object.LevelObject
            Level object being displayed or modified.
        """
        self.level_object = level_object

        clear_layout(self.layout())

        for block_index in self.level_object.blocks:
            block = get_block(
                block_index,
                self.level_object.palette_group,
                self.level_object.graphics_set,
                self.level_object.tsa_data,
            )
            self.layout().addWidget(BlockArea(block))

        self.update()


class BlockArea(QWidget):
    """Paint one 16x16 block from an object preview.

    The tooltip exposes the source block id in hexadecimal so maintainers can
    connect the rendered preview back to TSA/block data. These widgets are
    created transiently whenever ``BlockArray`` rebuilds, so each block tile
    stays aligned with the latest decoded object rather than caching stale
    render state.

    Parameters
    ----------
    block : Block
        Block or block index being rendered or inspected.

    Attributes
    ----------
    block : Block
        Block rendered by this widget.

    See Also
    --------
    BlockArray
        Rebuilds these widgets from a decoded object's block sequence.
    """

    def __init__(self, block: Block):
        """Create a block preview widget.

        Parameters
        ----------
        block : Block
            Block or block index being rendered or inspected.
        """
        super(BlockArea, self).__init__()

        self.block = block

        self.setContentsMargins(0, 0, 0, 0)
        self.setToolTip(hex(self.block.index))

    def sizeHint(self):
        """Natural size for one SMB3 block-preview widget.

        ``BlockArray`` composes many of these widgets, so the hint keeps every
        block tile aligned to the native 16x16 SMB3 block size and therefore
        keeps the visual block row consistent with the decoded block sequence.
        The method is part of the same inspection flow as ``BlockArray``:
        decoded block ids become one widget per block, and each widget
        advertises the footprint needed to keep that row faithful to SMB3 block
        geometry during layout and repaint passes. That makes the hint part of
        the decode-to-layout path rather than a generic widget default, because
        Qt reads this value before paint to decide how much space each decoded
        block should occupy. In practice, this is the layout-side continuation
        of the decode flow: once ``BlockArray`` has turned block ids into
        widgets, ``sizeHint`` carries the decoded 16x16 geometry into row
        layout so the inspector preserves the source object's block structure
        instead of flattening it into generic control sizing.

        Returns
        -------
        QSize
            The recommended Qt size.
        """
        return QSize(Block.WIDTH, Block.HEIGHT)

    def paintEvent(self, event):
        """Draw the block at native size.

        Parameters
        ----------
        event : QPaintEvent
            Qt event delivered to the widget.
        """
        painter = QPainter(self)

        self.block.draw(painter, 0, 0, Block.WIDTH)
