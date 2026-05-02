"""Specialize clipboard popup actions for Scribe's world-map view.

This module narrows :class:`foundry.gui.ContextMenu.ContextMenu` to the
world-map editing path in Scribe. The shared base class already stores copied
objects, popup anchors, and cursor placement state; ``WorldContextMenu`` adds
only the tile-oriented cut, copy, and paste actions that
``scribe.gui.main_window.ScribeMainWindow`` wires into undoable world-map
commands.

At popup time the menu reads tile selection from
``foundry.gui.visualization.world.WorldView`` through :class:`LevelRef`,
enables only the clipboard actions that match that snapshot, and then hands the
triggered action back to the main window. That keeps clipboard enablement,
popup anchoring, and command dispatch on one stable world-view -> menu ->
main-window path.

See Also
--------
foundry.gui.ContextMenu.ContextMenu
    Provides the shared clipboard and popup-position state reused here.
scribe.gui.main_window.ScribeMainWindow
    Connects these actions to the world-map editing commands.
"""

from PySide6.QtCore import QPoint
from PySide6.QtGui import QAction, Qt

from foundry import icon
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.ContextMenu import ContextMenu
from foundry.gui.localization import tr

TR_CONTEXT = "ScribeWorldContextMenu"


class WorldContextMenu(ContextMenu):
    """Context menu for editing selected tiles in the world view.

    The menu is the world-map counterpart to Foundry's shared level-editing
    context-menu state. It exposes only the clipboard actions Scribe supports
    on the world canvas and updates their enabled state from the active
    selection and staged clipboard contents each time the menu is opened.

    Parameters
    ----------
    level_ref : LevelRef
        Reference whose ``level`` is the active :class:`WorldMap` instance.

    Attributes
    ----------
    copy_action : QAction
        Action that copies the active tile selection into the shared
        clipboard state.
    cut_action : QAction
        Action that copies and then removes the active tile selection.
    level_ref : LevelRef
        Reference that supplies the active world map and selection.
    paste_action : QAction
        Action that pastes the staged clipboard contents at the popup anchor.

    Notes
    -----
    The class owns enablement policy, not edit execution. Each popup pass reads
    tile selection and staged clipboard state, enables only the actions that
    make sense for that snapshot, and then relies on the main window's command
    handlers to perform the actual undoable world-map edits.
    """

    def __init__(self, level_ref: LevelRef):
        """Create the world-view clipboard actions.

        Construction is intentionally small because clipboard storage and popup
        anchoring already live in :class:`foundry.gui.ContextMenu.ContextMenu`.
        This initializer only installs the tile-editing actions that the
        Scribe main window later connects to copy, cut, and paste handlers,
        while the inherited clipboard fields remain the shared state those
        handlers populate and consume across popup invocations.

        Parameters
        ----------
        level_ref : LevelRef
            Reference whose active level is edited by the world view.
        """
        super(WorldContextMenu, self).__init__(level_ref)

        self.level_ref = level_ref

        self.cut_action = self.addAction(tr(TR_CONTEXT, "cut_tiles", "Cut Tiles"))
        self.cut_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_X)
        self.cut_action.setIcon(icon("scissors.svg"))

        self.copy_action = self.addAction(tr(TR_CONTEXT, "copy_tiles", "Copy Tiles"))
        self.copy_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_C)
        self.copy_action.setIcon(icon("copy.svg"))

        self.paste_action = self.addAction(tr(TR_CONTEXT, "paste_tiles", "Paste Tiles"))
        self.paste_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_V)
        self.paste_action.setIcon(icon("clipboard.svg"))

    def retranslate_ui(self) -> None:
        """Refresh world context-menu labels without changing commands.

        The cut, copy, and paste action text is rebuilt from the active catalog.
        Existing ``QAction`` objects, shortcuts, icons, and connected tile
        command handlers stay in place so translated labels never become command
        identity.
        """
        self.cut_action.setText(tr(TR_CONTEXT, "cut_tiles", "Cut Tiles"))
        self.copy_action.setText(tr(TR_CONTEXT, "copy_tiles", "Copy Tiles"))
        self.paste_action.setText(tr(TR_CONTEXT, "paste_tiles", "Paste Tiles"))

    @property
    def world(self) -> WorldMap:
        """Active world map displayed by the owning Scribe window.

        The property narrows ``level_ref.level`` to the world-map type this
        menu expects so popup-time enablement checks can read selection state
        without repeating that cast at each call site.

        Returns
        -------
        foundry.game.level.WorldMap.WorldMap
            World map whose tile selection controls action enabled state.
        """
        return self.level_ref.level

    def popup(self, pos: QPoint, at: QAction = None):
        """Refresh enabled state before opening the Qt popup menu.

        Cut and copy are available only when the world view has
        selected tiles. Paste is available only when the shared clipboard from
        :class:`foundry.gui.ContextMenu.ContextMenu` already holds copied
        objects. After those checks, this method delegates to the base class so
        it can remember the popup position for later paste placement.

        Parameters
        ----------
        pos : QPoint
            Global popup position supplied by the world view.
        at : QAction, optional
            Optional action to place under the popup.

        Returns
        -------
        object
            Result returned by Qt's popup handling, if any.
        """
        self.copy_action.setEnabled(bool(self.world.get_selected_tiles()))
        self.cut_action.setEnabled(bool(self.world.get_selected_tiles()))

        self.paste_action.setEnabled(bool(self.copied_objects))

        return super(WorldContextMenu, self).popup(pos, at)
