"""Level-editor context menus and their shared clipboard state.

This module groups the reusable context-menu state that multiple level-editing
surfaces depend on. The base menu preserves clipboard contents, paste anchors,
and popup positions across invocations, while the concrete level menu turns
that state into actions for placement, selection, draw-order changes, and the
grab-object workflow.

See Also
--------
foundry.gui.ObjectList
    Shares selection-oriented edit workflows with the level context menu.
foundry.gui.visualization.level.LevelView
    Opens these menus from canvas interactions and translates actions back into
    editor commands.
"""

from enum import Enum
from typing import Self, Sequence

from PySide6.QtCore import QPoint, SignalInstance
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from foundry import icon
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.level.LevelRef import LevelRef
from smb3parse.data_points import Position


class CMMode(Enum):
    """Name the editor surface that opened the shared level context menu.

    ``LevelContextMenu`` is reused across several entry points instead of
    building separate menus for the canvas, object list, and background. This
    enum is the small routing token that tells that shared command surface
    which actions should be visible or enabled for a given selection
    situation. In practice it is the state-machine input for one menu that
    serves multiple editing workflows.

    Attributes
    ----------
    BG : CMMode
        Menu opened on empty level background, where placement and paste are
        the primary actions.
    LIST : CMMode
        Menu opened from the object list, where selection is driven
        by the list rather than the canvas hit target.
    OBJ : CMMode
        Menu opened over an object in the level view, where draw-order, copy,
        cut, and grab-object actions are relevant.

    See Also
    --------
    LevelContextMenu
        Applies these modes when enabling and disabling edit actions.
    """

    BG = 1
    OBJ = 2
    LIST = 3


MAX_ORIGIN = 0xFF, 0xFF


class ContextMenu(QMenu):
    """Base context menu state shared by level editing menus.

    The menu stores the non-visual state that must survive between invocations:
    where the popup was opened, which objects are staged for copy/paste, and
    the minimum copied origin used to preserve relative offsets when a pasted
    group is placed elsewhere. That clipboard-like state is shared by the level
    canvas, object list, and any context-specific menu configuration layered on
    top of this base class.

    Parameters
    ----------
    level_ref : LevelRef
        Reference to the edited level.

    Attributes
    ----------
    copied_objects : list[ObjectLike]
        Copies of objects staged for the next paste operation.
    copied_objects_origin : Position
        Minimum copied position used as the paste anchor for relative offsets.
    last_opened_at : QPoint
        Global position where the menu was last opened.
    level_ref : LevelRef
        Reference that owns the edited level and selection.
    """

    def __init__(self, level_ref: LevelRef):
        """Create shared context-menu state.

        Parameters
        ----------
        level_ref : LevelRef
            Reference to the edited level.
        """
        super(ContextMenu, self).__init__()

        self.level_ref = level_ref

        self.copied_objects: list[ObjectLike] = []
        self.copied_objects_origin = Position.from_xy(0, 0)

        self.last_opened_at = QPoint(0, 0)

    def get_position(self) -> QPoint:
        """Popup origin recorded for the last context-menu invocation.

        Paste and add-object workflows reuse this anchor when translating menu
        actions back into editor coordinates.

        Returns
        -------
        QPoint
            Last popup position.
        """
        return self.last_opened_at

    def set_copied_objects(self, objects: Sequence[ObjectLike]):
        """Copy objects and compute their paste anchor.

        The stored origin is the minimum copied position, which lets paste keep
        relative offsets between a copied group of heterogeneous objects across
        later paste operations instead of flattening them to one anchor point.
        In practice this is the clipboard-staging step for every cut, copy, and
        duplicate workflow: it snapshots the selected objects, normalizes the
        group's anchor, and leaves later paste actions enough state to rebuild
        the selection at a new menu position.

        Parameters
        ----------
        objects : Sequence[ObjectLike]
            Objects to copy.
        """
        if not objects:
            return

        self.copied_objects = [obj.copy() for obj in objects]

        min_x, min_y = MAX_ORIGIN

        for obj in objects:
            obj_x, obj_y = obj.get_position()

            min_x = min(min_x, obj_x)
            min_y = min(min_y, obj_y)

        min_x = max(min_x, 0)
        min_y = max(min_y, 0)

        self.copied_objects_origin = Position.from_xy(min_x, min_y)

    def get_copied_objects(self) -> tuple[list[ObjectLike], Position]:
        """Copied objects and their paste anchor.

        Callers use the returned origin to translate the copied group to a new
        insertion point without flattening each object's relative offset during
        paste or duplicate workflows.

        Returns
        -------
        tuple[list[ObjectLike], Position]
            Copied objects and minimum copied position.
        """
        return self.copied_objects, self.copied_objects_origin

    def popup(self, pos: QPoint, at: QAction = None):
        """Store the popup position before showing the Qt menu.

        Recording the global popup point lets later actions interpret "paste"
        or "place object" relative to the menu invocation site after Qt has
        already handed control back to the caller and the cursor location may
        no longer be available. That recorded point becomes the bridge from a
        transient right-click event into follow-up edit commands that need a
        stable placement anchor after the menu interaction completes, because
        this method updates ``last_opened_at`` before delegating to Qt and that
        stored state is what later add or paste handlers convert back into
        level coordinates.

        Parameters
        ----------
        pos : QPoint
            Global popup position.
        at : QAction, optional
            Optional action to place under the popup.

        Returns
        -------
        object
            Context menu popup result, if provided by Qt.
        """
        self.last_opened_at = pos

        return super(ContextMenu, self).popup(pos, at)


class LevelContextMenu(ContextMenu):
    """Context menu for level object editing actions.

    The same menu instance is reconfigured for background, object, and list
    invocations so action enabled states reflect the edited selection,
    clipboard state, and object under the cursor. That lets Foundry keep one
    authoritative command surface for placement, clipboard actions, draw-order
    changes, deletion, and the pipette-style "grab object" workflow.

    Parameters
    ----------
    level_ref : LevelRef
        Reference to the edited level.

    Attributes
    ----------
    add_object_action : QAction
        Action that places the toolbar object currently selected for painting.
    copy_action : QAction
        Action that copies selected level objects.
    cut_action : QAction
        Action that copies and removes selected level objects.
    grab_selected_object_action : QAction
        Action that updates the toolbar selection from the object under the cursor.
    into_background_action : QAction
        Action that moves selected objects earlier in draw order.
    into_foreground_action : QAction
        Action that moves selected objects later in draw order.
    object_to_grab : LevelObject | EnemyItem | None
        Object under the cursor for the grab action.
    paste_action : QAction
        Action that pastes copied objects.
    remove_action : QAction
        Action that removes selected objects.
    triggered : SignalInstance
        Qt signal emitted when an action is triggered.
    """

    triggered: SignalInstance

    def __init__(self, level_ref: LevelRef):
        """Create the level-editing context menu actions.

        One menu instance is reused across level-view, background, and
        object-list entry points, so construction wires every action up front
        and leaves later calls to adjust enabled state only. The workflow is
        split into three phases: build the complete action surface once, retain
        object-independent clipboard state in the base class, and let
        ``as_object_menu()``, ``as_background_menu()``, or ``as_list_menu()``
        re-stage the same actions for a specific invocation context without
        rebuilding the menu.

        Parameters
        ----------
        level_ref : LevelRef
            Reference to the edited level.
        """
        super(LevelContextMenu, self).__init__(level_ref)

        self.add_object_action = self.addAction("Place Object")
        self.add_object_action.setIcon(icon("plus.svg"))
        self.grab_selected_object_action = self.addAction("Grab Object")
        self.grab_selected_object_action.setIcon(icon("crosshair.svg"))

        self.addSeparator()

        self.cut_action = self.addAction("Cut")
        self.cut_action.setIcon(icon("scissors.svg"))
        self.copy_action = self.addAction("Copy")
        self.copy_action.setIcon(icon("copy.svg"))
        self.paste_action = self.addAction("Paste")
        self.paste_action.setIcon(icon("clipboard.svg"))

        self.addSeparator()

        self.into_foreground_action = self.addAction("To Foreground")
        self.into_foreground_action.setIcon(icon("upload.svg"))
        self.into_background_action = self.addAction("To Background")
        self.into_background_action.setIcon(icon("download.svg"))

        self.addSeparator()

        self.remove_action = self.addAction("Remove")
        self.remove_action.setIcon(icon("minus.svg"))

        self.object_to_grab: LevelObject | EnemyItem | None = None

    def as_object_menu(self, level_object: LevelObject | EnemyItem | None) -> Self:
        """Configure the menu for an object-view click.

        This mode exposes object-centric actions such as cut, copy, draw-order
        changes, and grab-object, then routes the request through the shared
        action-state setup.

        Parameters
        ----------
        level_object : LevelObject | EnemyItem | None
            Level object being displayed or modified.

        Returns
        -------
        Self
            Context menu configured for object actions.
        """
        return self._setup_items(CMMode.OBJ, level_object)

    def as_background_menu(self, level_object: LevelObject | EnemyItem | None) -> Self:
        """Configure the menu for a background click.

        Background invocations emphasize placement and paste actions while
        suppressing commands that require an existing selection, then route the
        state through the same shared action setup.

        Parameters
        ----------
        level_object : LevelObject | EnemyItem | None
            Level object being displayed or modified.

        Returns
        -------
        Self
            Context menu configured for background actions.
        """
        return self._setup_items(CMMode.BG, level_object)

    def as_list_menu(self, level_object: LevelObject | EnemyItem | None) -> Self:
        """Configure the menu for an object-list click.

        List invocations keep selection-driven edit actions while disabling
        placement that only makes sense from a canvas position, then route the
        result through the shared action-state setup.

        Parameters
        ----------
        level_object : LevelObject | EnemyItem | None
            Level object being displayed or modified.

        Returns
        -------
        Self
            Context menu configured for list actions.
        """
        return self._setup_items(CMMode.LIST, level_object)

    def _setup_items(self, mode: CMMode | None, object_under_cursor: LevelObject | EnemyItem | None) -> Self:
        """Enable actions for a menu invocation context.

        The method is the routing point that turns clipboard state, current
        selection, and invocation surface into one coherent menu state.

        Parameters
        ----------
        mode : CMMode | None
            Invocation context.
        object_under_cursor : LevelObject | EnemyItem | None
            Object under the cursor, if any.

        Returns
        -------
        Self
            Context menu with its actions initialized.
        """
        self.object_to_grab = object_under_cursor

        objects_selected = bool(self.level_ref.selected_objects)
        objects_copied = bool(self.copied_objects)

        self.grab_selected_object_action.setEnabled(object_under_cursor is not None)
        self.grab_selected_object_action.setText(
            f"Grab '{object_under_cursor.name}'" if object_under_cursor else "Nothing to grab"
        )

        self.cut_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.copy_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.paste_action.setEnabled(not mode == CMMode.LIST and objects_copied)

        self.into_background_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.into_foreground_action.setEnabled(not mode == CMMode.BG and objects_selected)

        self.remove_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.add_object_action.setEnabled(not mode == CMMode.LIST)

        return self
