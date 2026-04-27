"""Persist level-view overlay toggles and screenshot actions.

This module owns the View menu for Foundry's active level canvas. The main
window exposes these actions from the menu bar, the menu seeds each checkable
action from the level-view settings store, and later trigger events write the
updated values back into that same store. `MainView` then consumes the
persisted state during redraw, timer updates, and screenshot export, so this
file sits directly on the editor workflow that turns menu input into visible
level-view changes.

See Also
--------
foundry.gui.visualization.MainView
    Consumes the persisted settings toggled by this menu during redraw.
foundry.gui.FoundryMainWindow
    Hosts the menu bar that exposes these visualization controls.
"""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMenu

from foundry import IMG_FILE_FILTER, icon
from foundry.game.File import ROM


class ViewMenu(QMenu):
    """Persist and expose level-view visualization toggles.

    The view menu controls overlays and rendering options for the active level
    canvas. Each checkable action mirrors a value in the view settings store so
    the editor can preserve grid, animation, helper-overlay, and screenshot
    behavior across sessions.

    Parameters
    ----------
    level_view : MainView
        Level-view widget whose settings and rendering behavior are managed by
        this menu.
    title : str, optional
        Menu title shown in the main window.

    Attributes
    ----------
    _level_view : MainView
        Level-view widget updated by this menu.
    _grid_action : QAction
        Toggle for grid lines.
    _coord_action : QAction
        Toggle for grid-coordinate labels.
    _mario_action : QAction
        Toggle for the Mario start marker.
    _jumps_action : QAction
        Toggle for jump markers drawn on objects.
    _items_action : QAction
        Toggle for item previews inside blocks.
    _invis_action : QAction
        Toggle for invisible-item markers.
    _auto_scroll_action : QAction
        Toggle for the autoscroll path overlay.
    _jump_zones_action : QAction
        Toggle for jump-zone overlays.
    _resize_action : QAction
        Toggle for resize and expansion markers.
    _anim_action : QAction
        Toggle for block-animation playback.
    _trans_action : QAction
        Toggle for block transparency rendering.
    _special_bg_action : QAction
        Toggle for the default-background override.
    _screen_shot_action : QAction
        Action that exports the visible level view as an image.
    """

    def __init__(self, level_view, title="&View"):
        """Create the view menu for a level-view widget.

        Construction runs in four stages. It first stores the managed level
        view and connects the menu's central trigger dispatcher. It then builds
        the grid and object-overlay toggles from persisted settings. Next it
        adds the motion-overlay and render toggles that feed the same settings
        store. Finally it adds the screenshot action. Once those stages are in
        place, later triggers follow one consistent workflow: a menu action
        changes a persisted view setting, ``_on_trigger`` writes that setting
        back through the shared store, and the level view redraws against the
        updated state.

        Parameters
        ----------
        level_view
            Level-view widget whose settings and rendering behavior are managed
            by this menu.
        title : str, optional
            Menu title shown in the main window.
        """
        super(ViewMenu, self).__init__(title)

        self.triggered.connect(self._on_trigger)

        self._level_view = level_view

        self._grid_action = self._make_action("&Grid lines", "level_view/draw_grid")
        self._coord_action = self._make_action("&Coordinates", "level_view/draw_grid_coordinates")

        self.addSeparator()

        self._mario_action = self._make_action("&Mario", "level_view/draw_mario")
        self._jumps_action = self._make_action("&Jumps on objects", "level_view/draw_jump_on_objects")
        self._items_action = self._make_action("&Items in blocks", "level_view/draw_items_in_blocks")
        self._invis_action = self._make_action("I&nvisible items", "level_view/draw_invisible_items")

        self.addSeparator()

        self._auto_scroll_action = self._make_action("&Autoscroll Path", "level_view/draw_autoscroll")
        self._jump_zones_action = self._make_action("Jump &Zones", "level_view/draw_jumps")
        self._resize_action = self._make_action("&Resize Type", "level_view/draw_expansion")

        self.addSeparator()

        self._anim_action = self._make_action("Show Block Animation", "level_view/block_animation")
        self._trans_action = self._make_action("&Block Transparency", "level_view/block_transparency")
        self._special_bg_action = self._make_action("Default Background Tiles", "level_view/special_background")

        self.addSeparator()

        self._screen_shot_action = self.addAction("Save &Screenshot of Level")
        self._screen_shot_action.setIcon(icon("image.svg"))

    def _make_action(self, title: str, setting_string: str):
        """Create a checkable action backed by a stored view setting.

        The action is initialized from the view's settings store so the menu
        opens in the same state the renderer is already using.

        Parameters
        ----------
        title : str
            Text shown in the menu.
        setting_string : str
            Settings key mirrored by the check state.

        Returns
        -------
        QAction
            Newly created action with its checked state initialized from the
            current settings store.
        """
        checkable_action = self.addAction(title)
        checkable_action.setCheckable(True)
        checkable_action.setChecked(self.settings.value(setting_string))

        return checkable_action

    @property
    def settings(self):
        """Expose the settings store that drives the managed level view.

        Menu actions persist into the same settings object that ``MainView``
        reads during paint and timer setup, which keeps the menu and renderer in
        sync across sessions. Reading this property is part of the menu's data
        flow: action creation seeds check states from it, action triggers write
        updated values back into it, and the level view redraws against that
        same shared store after the toggle changes.

        Returns
        -------
        Settings
            Settings store queried and updated by the menu actions.
        """
        return self._level_view.settings

    def _on_trigger(self, action: QAction):
        """Persist a visualization toggle and refresh the level view.

        Parameters
        ----------
        action : QAction
            Triggered action from this menu.
        """
        checked = action.isChecked()

        if action is self._grid_action:
            self.settings.setValue("level_view/draw_grid", checked)
        elif action is self._coord_action:
            self.settings.setValue("level_view/draw_grid_coordinates", checked)
        elif action is self._anim_action:
            self.settings.setValue("level_view/block_animation", checked)
            self._level_view.update_anim_timer()
        elif action is self._trans_action:
            self.settings.setValue("level_view/block_transparency", checked)
        elif action is self._jump_zones_action:
            self.settings.setValue("level_view/draw_jumps", checked)
        elif action is self._mario_action:
            self.settings.setValue("level_view/draw_mario", checked)
        elif action is self._resize_action:
            self.settings.setValue("level_view/draw_expansion", checked)
        elif action is self._jumps_action:
            self.settings.setValue("level_view/draw_jump_on_objects", checked)
        elif action is self._items_action:
            self.settings.setValue("level_view/draw_items_in_blocks", checked)
        elif action is self._invis_action:
            self.settings.setValue("level_view/draw_invisible_items", checked)
        elif action is self._auto_scroll_action:
            self.settings.setValue("level_view/draw_autoscroll", checked)
        elif action is self._special_bg_action:
            self.settings.setValue("level_view/special_background", checked)
        elif action is self._screen_shot_action:
            self._on_screenshot()
            return

        self._level_view.update()

        self.exec_()

    def _on_screenshot(self):
        """Export the rendered level view to an image file.

        The default filename uses the loaded ROM and level name so repeated
        captures land near other editor exports without retyping a path.
        """
        recommended_file = (
            f"{self.settings.value('editor/default_dir_path')}/{ROM.name} - {self._level_view.level_ref.name}.png"
        )

        pathname, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save Screenshot",
            dir=recommended_file,
            filter=IMG_FILE_FILTER,
        )

        if not pathname:
            return

        self._level_view.make_screenshot().save(pathname)
