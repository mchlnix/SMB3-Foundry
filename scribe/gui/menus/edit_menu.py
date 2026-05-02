"""Expose Scribe overworld edit actions through the Edit menu.

This module defines :class:`EditMenu`, the ``QMenu`` used by Scribe's
overworld editor to surface undo and redo commands, bulk-clearing operations,
and the modal world-info editor. The menu itself does not mutate world data
directly beyond launching dialogs. Instead it delegates destructive map edits
to the owning world view and reuses the parent's shared undo stack so menu
actions join the same history as direct canvas edits.

The edit workflow splits into two paths. Undo and redo actions are created by
the parent editor's ``QUndoStack`` and stay synchronized with that shared
history automatically. The remaining menu actions route through
``scribe.gui.visualization.world.WorldView`` helpers or open
:class:`scribe.gui.edit_world_info.EditWorldInfo`, which may update per-world
metadata and cross-world ordering state before the menu emits a refresh signal
for downstream world-list consumers.

See Also
--------
scribe.gui.edit_world_info.EditWorldInfo
    Dialog launched from this menu to edit world metadata and staged
    reorganization changes.
foundry.gui.visualization.world.WorldView
    Owns the bulk-clearing operations delegated by this menu.
"""

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QMenu

from foundry import icon
from foundry.gui.localization import tr
from scribe.gui.edit_world_info import EditWorldInfo

TR_CONTEXT = "ScribeEditMenu"


class EditMenu(QMenu):
    """Provide edit actions for Scribe's overworld editor.

    The menu is a thin controller over the parent editor's world-editing
    collaborators. It binds Qt actions to the shared undo history, forwards
    bulk-clearing requests to the active world view, and launches the world
    metadata dialog when the user needs to adjust information that affects more
    than the visible map tiles alone.

    Parameters
    ----------
    parent : QWidget
        Owning editor widget whose interface is expected to expose
        ``undo_stack`` and ``world_view`` attributes used by the menu actions.

    Attributes
    ----------
    world_order_maybe_changed : SignalInstance
        Emitted after the world-info dialog closes so other widgets can refresh
        any cached world-order presentation.
    undo_action : QAction
        Action bound to the parent editor's shared undo stack.
    redo_action : QAction
        Action bound to the parent editor's shared redo stack.
    clear_tiles_action : QAction
        Clears all map tiles through :meth:`world_view.clear_tiles`.
    clear_level_pointers_action : QAction
        Clears every level pointer through
        :meth:`world_view.clear_level_pointers`.
    clear_sprites_action : QAction
        Clears all overworld sprites through :meth:`world_view.clear_sprites`.
    edit_world_info : QAction
        Opens :class:`scribe.gui.edit_world_info.EditWorldInfo` for the active
        world.

    Notes
    -----
    The menu assumes its parent provides the editor-specific collaborators it
    needs. That coupling is intentional here: ``EditMenu`` stays lightweight by
    adapting existing editor services instead of owning duplicate state.
    """

    world_order_maybe_changed: SignalInstance = Signal()

    def __init__(self, parent):
        """Create the edit menu and bind its actions to the active editor.

        The constructor stages the menu around the editor services that already
        own overworld state. It first connects one Qt dispatcher so every menu
        item can funnel through :meth:`on_menu` and preserve a single trigger
        routing path. It then asks the parent's shared ``QUndoStack`` to build
        the undo and redo actions, which keeps labels, enabled state, and
        command replay synchronized with edits that originate outside the menu.
        The remaining actions are lightweight entry points: bulk-clear items
        forward directly into :attr:`world_view`, while the world-info item
        opens a modal dialog for metadata that can change both the active world
        and higher-level world ordering state.

        Parameters
        ----------
        parent : QWidget
            Owning editor widget whose ``undo_stack`` supplies the undo and
            redo actions, whose ``world_view`` handles bulk-edit commands, and
            whose ``level_ref`` provides the world model consumed by the
            world-info dialog.
        """
        super(EditMenu, self).__init__(tr(TR_CONTEXT, "edit", "&Edit"), parent)

        self.triggered.connect(self.on_menu)

        self.undo_action = self.undo_stack.createUndoAction(self)
        self.undo_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_Z)
        self.undo_action.setIcon(icon("rotate-ccw.svg"))

        self.redo_action = self.undo_stack.createRedoAction(self)
        self.redo_action.setShortcut(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Z)
        self.redo_action.setIcon(icon("rotate-cw.svg"))

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)

        self.addSeparator()

        self.clear_tiles_action = self.addAction(tr(TR_CONTEXT, "clear_tiles", "Clear &Tiles"))
        self.clear_tiles_action.setIcon(icon("loader.svg"))
        self.clear_level_pointers_action = self.addAction(
            tr(TR_CONTEXT, "clear_all_level_pointers", "Clear All &Level Pointers")
        )
        self.clear_level_pointers_action.setIcon(icon("loader.svg"))
        self.clear_sprites_action = self.addAction(tr(TR_CONTEXT, "clear_all_sprites", "Clear All &Sprites"))
        self.clear_sprites_action.setIcon(icon("loader.svg"))

        self.addSeparator()

        self.edit_world_info = self.addAction(tr(TR_CONTEXT, "edit_world_info", "Edit World Info"))
        self.edit_world_info.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_E)
        self.edit_world_info.setIcon(icon("tool.svg"))

    def retranslate_ui(self) -> None:
        """Refresh edit-menu labels after a language change.

        The menu updates only visible action text and the menu title. QAction
        identity, shortcuts, undo-stack bindings, and world-view callbacks stay
        intact so a live language change cannot disturb edit history, selected
        world state, or undo ownership.
        """
        self.setTitle(tr(TR_CONTEXT, "edit", "&Edit"))
        self.clear_tiles_action.setText(tr(TR_CONTEXT, "clear_tiles", "Clear &Tiles"))
        self.clear_level_pointers_action.setText(
            tr(TR_CONTEXT, "clear_all_level_pointers", "Clear All &Level Pointers")
        )
        self.clear_sprites_action.setText(tr(TR_CONTEXT, "clear_all_sprites", "Clear All &Sprites"))
        self.edit_world_info.setText(tr(TR_CONTEXT, "edit_world_info", "Edit World Info"))

    def on_menu(self, action: QAction):
        """Dispatch a triggered menu action to the appropriate editor helper.

        Qt delivers every triggered action through one slot, so this dispatcher
        maps each menu item back to the editor service that owns the underlying
        behavior. The method does not build undo commands itself; it forwards
        the request to collaborators that already know how to mutate the world
        model and record the change in the shared editing history.

        Parameters
        ----------
        action : QAction
            Action emitted by Qt when the user activates an item in this menu.

        Notes
        -----
        Bulk-clear actions delegate to :attr:`world_view`, which records the
        resulting changes on the shared undo stack. The world-info action runs
        a modal dialog for the active world's level reference and then emits
        :attr:`world_order_maybe_changed` because that dialog can reorder or
        relabel worlds in ways that external menus and selectors need to
        refresh.
        """
        if action is self.clear_tiles_action:
            self.world_view.clear_tiles()
        elif action is self.clear_sprites_action:
            self.world_view.clear_sprites()
        elif action is self.clear_level_pointers_action:
            self.world_view.clear_level_pointers()
        elif action is self.edit_world_info:
            EditWorldInfo(self.parent(), self.world_view.level_ref.level).exec()

            self.world_order_maybe_changed.emit()

    @property
    def undo_stack(self):
        """Expose the parent editor's shared undo history object.

        ``EditMenu`` never owns an independent command timeline. Resolving the
        parent's stack on demand keeps this menu attached to the same replay
        boundary used by tile placement, pointer edits, and other editor
        gestures. The actions created in :meth:`__init__` and the bulk-edit
        helpers triggered later through :meth:`on_menu` therefore all converge
        on one command history instead of drifting onto menu-local state.

        Returns
        -------
        QUndoStack
            Undo stack retrieved from the parent editor.
        """
        return self.parent().undo_stack

    @property
    def world_view(self):
        """Expose the active world view used for bulk map-edit actions.

        The menu forwards destructive overworld operations to the editor's
        existing world view at call time instead of caching a separate
        reference. That keeps menu actions aligned with whichever level
        reference, selection state, and undo-aware helpers the editor is
        currently presenting.

        Returns
        -------
        WorldView
            Parent editor's active overworld view.
        """
        return self.parent().world_view
