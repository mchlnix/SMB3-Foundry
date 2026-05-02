"""Render draggable object previews for the object toolbar.

This module owns the compact icon widget used by the object-toolbar surfaces
that let maintainers browse SMB3 level objects, inspect their decoded art, and
drag placements into a view. ``ObjectIcon`` keeps only the minimal object state
needed to rebuild an image, tooltip, and drag payload, so toolbar redraws stay
cheap while still carrying enough metadata for placement and recent-object
tracking.

See Also
--------
foundry.gui.widgets.object_toolbar.ObjectToolBox
    Hosts grids of ``ObjectIcon`` widgets for level objects and enemy items.
foundry.gui.widgets.object_toolbar.ObjectToolBar
    Coordinates the larger active-object preview and recent-object slots.
foundry.gui.visualization.MainView.object_to_mime_data
    Serializes the represented object into the MIME payload used for drag
    placement.
"""

from PySide6.QtCore import QSize, Qt, Signal, SignalInstance
from PySide6.QtGui import QDrag, QImage, QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QSizePolicy, QWidget

from foundry.game.gfx import object_to_image
from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.game.gfx.objects import get_minimal_icon_object
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.Palette import bg_color_for_palette_group
from foundry.gui.localization import tr_object_name
from foundry.gui.visualization.MainView import object_to_mime_data

objects_to_use_pngs_instead = {
    "'?' with flower": load_from_object_sprite_sheet(0, 4),
    "'?' with leaf": load_from_object_sprite_sheet(1, 4),
    "'?' with star": load_from_object_sprite_sheet(2, 4),
    "'?' with continuous star": load_from_object_sprite_sheet(3, 4),
    "brick with flower": load_from_object_sprite_sheet(6, 4),
    "brick with leaf": load_from_object_sprite_sheet(7, 4),
    "brick with star": load_from_object_sprite_sheet(8, 4),
    "brick with continuous star": load_from_object_sprite_sheet(9, 4),
    "brick with multi-coin": load_from_object_sprite_sheet(10, 4),
    "brick with 1-up": load_from_object_sprite_sheet(11, 4),
    "brick with vine": load_from_object_sprite_sheet(12, 4),
    "brick with p-switch": load_from_object_sprite_sheet(13, 4),
    "invisible coin": load_from_object_sprite_sheet(14, 4),
    "invisible 1-up": load_from_object_sprite_sheet(15, 4),
    "bricks with single coins": load_from_object_sprite_sheet(18, 4),
    "note block with flower": load_from_object_sprite_sheet(35, 5),
    "note block with leaf": load_from_object_sprite_sheet(36, 5),
    "note block with star": load_from_object_sprite_sheet(37, 5),
    "wooden block with flower": load_from_object_sprite_sheet(38, 5),
    "wooden block with leaf": load_from_object_sprite_sheet(39, 5),
    "wooden block with star": load_from_object_sprite_sheet(40, 5),
    "silver coins (appear when you hit a p-switch)": load_from_object_sprite_sheet(53, 5),
}


class ObjectIcon(QWidget):
    """Display and drag a minimized level object or enemy.

    Icons render a compact preview using the object's palette group and provide
    MIME data for drag-and-drop placement. Some SMB3 power-up container objects
    use hand-picked sprite-sheet images so the toolbar shows their contents
    instead of only the generic block art. The icon stores a minimal object
    representation so palette previews stay cheap to redraw while still carrying
    enough metadata for drag-and-drop and tooltip inspection.

    Parameters
    ----------
    level_object : InLevelObject | None, optional
        Level object being displayed or modified.

    Attributes
    ----------
    MAX_SIZE : QSize
        Larger icon size used by the active-object preview.
    MIN_SIZE : QSize
        Standard toolbar icon size.
    clicked : SignalInstance
        Signal emitted after click or accepted drag. Consumers read
        :attr:`object` for the stable placement payload rather than tooltip
        text.
    draw_background_color : bool
        Whether the icon paints the object palette background.
    image : QImage
        Cached image rendered for the represented object.
    max_size : QSize
        Maximum size used by ``sizeHint``.
    object : InLevelObject | None
        Minimal object represented by this icon and serialized into drag MIME
        data. Localized tooltip text is display-only and is rebuilt by
        :meth:`retranslate_ui`.
    zoom : int
        Stored zoom factor applied by the icon when rendering its preview.
    """

    MIN_SIZE = QSize(32, 32)
    MAX_SIZE = MIN_SIZE * 2

    clicked: SignalInstance = Signal()

    def __init__(self, level_object: InLevelObject | None = None):
        """Create an icon for an optional object.

        Construction sets up the fixed-size Qt widget, initializes an empty
        preview cache, and then routes the optional object through
        :meth:`set_object` so tooltip text, decoded art, and drag metadata are
        populated through the same path later used by the toolbar and active
        preview. The widget starts with drag tracking disabled until the left
        button is held, which keeps ordinary hover movement from triggering the
        placement workflow.

        Parameters
        ----------
        level_object : InLevelObject | None, optional
            Level object being displayed or modified.
        """
        super(ObjectIcon, self).__init__()

        size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # set to False so move event is only fired, when they are clicked and dragged
        self.setMouseTracking(False)

        self.setSizePolicy(size_policy)

        self.zoom = 1

        self.object: InLevelObject | None = None
        self.image = QImage()

        self.set_object(level_object)

        self.draw_background_color = True

        self.max_size = self.MIN_SIZE

    def mouseMoveEvent(self, event):
        """Start a drag operation while the left button is held.

        Successful drops count as an object pick, so the icon emits ``clicked``
        after the drag finishes and was accepted by a view.
        This keeps recent-object tracking and selection state aligned with drag
        placement as well as plain clicks.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the base Qt handler when no drag starts, if any.
        """
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return super(ObjectIcon, self).mouseMoveEvent(event)

        assert self.object is not None

        drag = QDrag(self)

        mime_data = object_to_mime_data(self.object)

        drag.setMimeData(mime_data)

        if drag.exec() != Qt.DropAction.IgnoreAction:
            self.clicked.emit()

        return None

    def set_object(self, level_object: InLevelObject | None):
        """Replace the represented object and rebuild the preview image.

        Jump objects are ignored because they are edited through separate UI and
        are not placeable from the object toolbar.

        Parameters
        ----------
        level_object : InLevelObject | None
            Level object being displayed or modified.
        """
        if isinstance(level_object, Jump):
            return

        elif level_object is not None and (obj := get_minimal_icon_object(level_object)):
            self.object = obj

            if obj.name.lower() in objects_to_use_pngs_instead:
                self.image = objects_to_use_pngs_instead[obj.name.lower()]
            else:
                self.image = object_to_image(obj)

            if isinstance(obj, LevelObject):
                additional_data = f"{obj.domain:#x} {obj.obj_index:#x}"
            else:
                additional_data = f"{obj.obj_index:#x}"

            self._set_tooltip(additional_data)

        else:
            self.image = QImage()

        self.update_image()
        self.update()

    def retranslate_ui(self) -> None:
        """Refresh the represented object's tooltip text in place.

        The tooltip is rebuilt from the active catalog and stable object data.
        The icon image, stored ``LevelObject`` or jump payload, and grid widget
        identity remain unchanged so the toolbar still places the same object.
        """
        if isinstance(self.object, Jump) or self.object is None:
            return

        if isinstance(self.object, LevelObject):
            additional_data = f"{self.object.domain:#x} {self.object.obj_index:#x}"
        else:
            additional_data = f"{self.object.obj_index:#x}"

        self._set_tooltip(additional_data)

    def _set_tooltip(self, additional_data: str) -> None:
        """Refresh the translated object tooltip while preserving raw ids.

        The tooltip combines localized display text with raw SMB3 domain and
        object identifiers. Those hex values are stable placement metadata for
        maintainers inspecting toolbar entries; only the object name is
        localized, and neither part is used as the drag payload identity.

        Parameters
        ----------
        additional_data : str
            Hex domain/object id suffix shown beside the translated object
            name.
        """
        if self.object is not None:
            self.setToolTip(f"{tr_object_name(self.object)}, {additional_data}")

    def update_image(self):
        """Refresh the cached image for the represented object."""
        if isinstance(self.object, Jump):
            return

        elif self.object is None:
            self.image = QImage()

        elif self.object.name.lower() in objects_to_use_pngs_instead:
            self.image = objects_to_use_pngs_instead[self.object.name.lower()]

        else:
            self.image = object_to_image(self.object)

    def heightForWidth(self, width: int) -> int:
        """Calculate the proportional icon height for a requested width.

        The icon preserves the decoded preview aspect ratio instead of forcing
        every object into a square thumbnail.

        Parameters
        ----------
        width : int
            Width in pixels.

        Returns
        -------
        int
            Height required to preserve the widget aspect ratio.
        """
        current_width, current_height = self.image.size().toTuple()

        height = current_height / current_width * width

        return height

    def sizeHint(self):
        """Return the QSize Qt should reserve for this icon surface.

        Qt queries this hint after :meth:`set_object` and
        :meth:`update_image` have already rebuilt ``image`` from the minimal
        object payload. The object toolbox, recent-object strip, and active
        preview use this hint while they choose row geometry before any paint
        or drag gesture begins. ``ObjectIcon`` first checks whether doubling
        the decoded preview would still fit inside the slot envelope stored in
        ``max_size``. Small SMB3 objects therefore get a larger readable slot
        when space allows, while oversized previews stay clamped to the parent
        surface's configured bounds. That single decision keeps Qt layout
        negotiation, the scaled image produced later by :meth:`paintEvent`,
        and the widget geometry used as the drag source aligned around the same
        preview-size policy.

        Returns
        -------
        QSize
            Either the doubled decoded preview size or the configured
            ``max_size`` envelope, depending on which layout policy applies.
        """
        if self.object is not None and self.fits_inside(self.image.size() * 2, self.max_size):
            return self.image.size() * 2
        else:
            return self.max_size

    def paintEvent(self, event: QPaintEvent):
        """Paint the palette background and scaled object image.

        The widget uses the object's palette group when requested so preview
        icons read more like the level canvas and block viewer. Each paint pass
        turns the cached minimal-object image into the final toolbar surface by
        filling the palette background, scaling the preview to the slot Qt
        assigned, and centering it so drag sources and recent-object previews
        stay visually consistent.

        Parameters
        ----------
        event : QPaintEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the base Qt paint handler, if any.
        """
        if self.object is not None:
            painter = QPainter(self)

            if self.draw_background_color:
                painter.fillRect(event.rect(), bg_color_for_palette_group(self.object.palette_group))

            scaled_image = self.image.scaled(self.size(), aspectMode=Qt.AspectRatioMode.KeepAspectRatio)

            x = (self.width() - scaled_image.width()) // 2
            y = (self.height() - scaled_image.height()) // 2

            painter.drawImage(x, y, scaled_image)

        return super(ObjectIcon, self).paintEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Emit ``clicked`` when the mouse is released.

        Plain clicks use the same signal path as accepted drags so toolbar
        selection and recent-object tracking do not diverge. That keeps the
        object-browser workflow on a single signal whether the user is just
        selecting an object in the toolbox or finishing a drag-and-drop
        placement gesture.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the base Qt handler, if any.
        """
        self.clicked.emit()

        return super(ObjectIcon, self).mouseReleaseEvent(event)

    @staticmethod
    def fits_inside(size1: QSize, size2: QSize):
        """Check whether one preview size fits inside another.

        ``ObjectIcon`` uses this to decide when a decoded image can be shown at
        double size without overflowing the toolbar or active-preview slot.
        ``sizeHint`` relies on this boundary check to choose between a more
        readable enlarged SMB3 preview and the fixed Qt layout envelope that
        keeps icon rows aligned.

        Parameters
        ----------
        size1 : QSize
            Candidate size.
        size2 : QSize
            Maximum allowed size.

        Returns
        -------
        bool
            ``True`` when ``size1`` fits inside ``size2``.
        """
        return size1.width() <= size2.width() and size1.height() <= size2.height()
