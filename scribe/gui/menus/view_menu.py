"""Build the Scribe world-view visibility and export menu.

This module owns :class:`ViewMenu`, the ``View`` menu used by Scribe's world
editor window. During window construction, the menu mirrors persisted
visibility settings into Qt actions so the first rendered world view matches
the previous editing session. Later triggers route overlay changes back into
the parent window's settings store and delegate follow-up work such as
animation timer refreshes and screenshot generation to
:class:`~foundry.gui.visualization.world.WorldView`. That puts this file on the
main window -> menu action -> settings update -> world redraw and export path.
In practice this module is the persistence boundary for world-view toggles:
menu actions convert user intent into saved settings values, and the renderer
re-reads those values on the next paint and on the next application session.

See Also
--------
foundry.gui.visualization.world.WorldView
    Renders the world map surface that these actions reveal, hide, or export.
scribe.gui.main_window
    Hosts the menu bar and owns the shared application settings object.
"""

from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QFileDialog, QMenu

from foundry import IMG_FILE_FILTER, icon
from foundry.game.File import ROM
from foundry.gui.visualization.world.WorldView import WorldView
from smb3parse.constants import AIRSHIP_TRAVEL_SET_COUNT


class ViewMenu(QMenu):
    """Expose persisted world-view toggles and screenshot export actions.

    The menu presents every world-overlay flag that Scribe stores in the
    parent window's settings object. Each action starts from the persisted
    value, then writes updated state back through :meth:`on_menu` so the next
    world view can restore the same overlay mix.

    Parameters
    ----------
    parent
        Qt owner that provides the shared ``settings`` object consumed by the
        menu actions.
    world_view : WorldView
        Render surface whose overlays, animation timer, and screenshot export
        pipeline are controlled by this menu.

    Attributes
    ----------
    world_view : WorldView
        Active world renderer updated when actions need redraw or export work.
    grid_action : QAction
        Toggle for the tile-grid overlay persisted at
        ``world_view/show_grid``.
    border_action : QAction
        Toggle for world-border guides persisted at
        ``world_view/show_border``.
    animation_action : QAction
        Toggle for animated overworld tiles persisted at
        ``world_view/animated_tiles``.
    level_pointer_action : QAction
        Toggle for level-pointer markers persisted at
        ``world_view/show_level_pointers``.
    level_preview_action : QAction
        Toggle for tooltip previews persisted at
        ``world_view/show_level_previews``.
    sprite_action : QAction
        Toggle for overworld sprite markers persisted at
        ``world_view/show_sprites``.
    starting_point_action : QAction
        Toggle for the player start marker persisted at
        ``world_view/show_start_position``.
    airship_travel_actions : list[QAction]
        Bitfield-backed actions that map each airship path overlay to one bit
        in the persisted ``world_view/show_airship_paths`` setting.
    lock_bridge_action : QAction
        Toggle for lock and bridge event markers persisted at
        ``world_view/show_locks``.
    show_all_action : QAction
        Command action that enables every overlay through the same trigger path
        used by manual toggles.
    screen_shot_action : QAction
        Command action that exports the rendered world view to an image file.
    """

    def __init__(self, parent, world_view: WorldView):
        """Create actions from persisted world-view settings.

        The constructor turns saved visibility flags into concrete Qt actions
        that the main window can show immediately. After setup, later triggers
        reuse those same action objects as the single source of truth for
        settings writes, redraw-affecting toggles, and screenshot export.

        Parameters
        ----------
        parent
            Qt owner whose ``settings`` object stores world-view visibility
            preferences between editing sessions.
        world_view : WorldView
            Active world renderer that reacts to visibility toggles and
            provides the screenshot image written by :meth:`_on_screenshot`.

        Notes
        -----
        Construction happens in three stages: connect the shared
        :attr:`QMenu.triggered` signal to :meth:`on_menu`, seed every
        checkable action from the persisted settings value it owns, then add
        command-style actions such as ``Show All`` and ``Save Screenshot`` that
        trigger broader workflow transitions instead of toggling one flag.
        That staging keeps the first paint, later user toggles, and screenshot
        export path all driven by the same menu-owned action state.
        """
        super(ViewMenu, self).__init__("&View", parent)

        self.triggered.connect(self.on_menu)

        self.world_view = world_view

        self.grid_action = self.addAction("&Grid")
        self.grid_action.setShortcut(Qt.Modifier.CTRL | Qt.Key_G)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(self.settings.value("world_view/show_grid"))

        self.border_action = self.addAction("Borders")
        self.border_action.setCheckable(True)
        self.border_action.setChecked(self.settings.value("world_view/show_border"))

        self.animation_action = self.addAction("Animated Tiles")
        self.animation_action.setCheckable(True)
        self.animation_action.setChecked(self.settings.value("world_view/animated_tiles"))

        self.addSeparator()

        self.level_pointer_action = self.addAction("&Level Pointers")
        self.level_pointer_action.setCheckable(True)
        self.level_pointer_action.setChecked(self.settings.value("world_view/show_level_pointers"))
        self.level_pointer_action.setShortcut(Qt.Modifier.CTRL | Qt.Key_L)

        self.level_preview_action = self.addAction("&Tooltip with Level Preview")
        self.level_preview_action.setCheckable(True)
        self.level_preview_action.setChecked(self.settings.value("world_view/show_level_previews"))
        self.level_preview_action.setShortcut(Qt.Modifier.CTRL | Qt.Key_T)

        self.sprite_action = self.addAction("Overworld &Sprites")
        self.sprite_action.setCheckable(True)
        self.sprite_action.setChecked(self.settings.value("world_view/show_sprites"))
        self.sprite_action.setShortcut(Qt.Modifier.CTRL | Qt.Key_O)

        self.starting_point_action = self.addAction("Starting &Point")
        self.starting_point_action.setCheckable(True)
        self.starting_point_action.setChecked(self.settings.value("world_view/show_start_position"))
        self.starting_point_action.setShortcut(Qt.Modifier.CTRL | Qt.Key_P)

        self.addSeparator()

        self.airship_travel_actions = []
        for i in range(AIRSHIP_TRAVEL_SET_COUNT):
            self.airship_travel_actions.append(self.addAction(f"&Airship Travel Path {i+1}"))
            self.airship_travel_actions[-1].setCheckable(True)
            self.airship_travel_actions[-1].setChecked(
                self.settings.value("world_view/show_airship_paths") & 2**i == 2**i
            )

        self.addSeparator()

        self.lock_bridge_action = self.addAction("Lock and &Bridge Events")
        self.lock_bridge_action.setCheckable(True)
        self.lock_bridge_action.setChecked(self.settings.value("world_view/show_locks"))
        self.lock_bridge_action.setShortcut(Qt.Modifier.CTRL | Qt.Key_B)

        self.addSeparator()

        self.show_all_action = self.addAction("Show All")
        self.show_all_action.setIcon(icon("eye.svg"))

        self.screen_shot_action = self.addAction("Save Screenshot")
        self.screen_shot_action.setIcon(icon("image.svg"))

    def on_menu(self, action: QAction):
        """Apply one triggered menu action to settings or export flow.

        Parameters
        ----------
        action : QAction
            Triggered menu action emitted through the menu's shared
            :attr:`QMenu.triggered` signal.

        Notes
        -----
        Most branches only synchronize one persisted visibility flag. A few
        actions perform wider workflow steps: animated tiles also refresh the
        world-view timer, airship path toggles rebuild a bitfield stored in
        settings, ``Show All`` reuses each action's existing trigger path to
        enable every overlay consistently, and ``Save Screenshot`` delegates to
        :meth:`_on_screenshot`.
        """
        if action is self.grid_action:
            self.settings.setValue("world_view/show_grid", action.isChecked())
        elif action is self.border_action:
            self.settings.setValue("world_view/show_border", action.isChecked())
        elif action is self.animation_action:
            self.settings.setValue("world_view/animated_tiles", action.isChecked())
            self.world_view.update_anim_timer()
        elif action is self.level_pointer_action:
            self.settings.setValue("world_view/show_level_pointers", action.isChecked())
        elif action is self.level_preview_action:
            self.settings.setValue("world_view/show_level_previews", action.isChecked())
        elif action is self.sprite_action:
            self.settings.setValue("world_view/show_sprites", action.isChecked())
        elif action is self.starting_point_action:
            self.settings.setValue("world_view/show_start_position", action.isChecked())
        elif action in self.airship_travel_actions:
            value = 0

            for index, action in enumerate(self.airship_travel_actions):
                if action.isChecked():
                    value += 2**index

            self.settings.setValue("world_view/show_airship_paths", value)
        elif action is self.lock_bridge_action:
            self.settings.setValue("world_view/show_locks", action.isChecked())

        elif action is self.show_all_action:
            for view_action in self.actions():
                if view_action.isCheckable() and not view_action.isChecked():
                    view_action.trigger()
        elif action is self.screen_shot_action:
            self._on_screenshot()

    @property
    def settings(self):
        """Expose the settings object that backs every menu action.

        The property marks the parent window's settings store as the one
        persistence boundary for menu construction, toggle handling, and
        screenshot-path suggestions.

        Returns
        -------
        QSettings
            Settings object used to seed action state during construction and
            persist updates from :meth:`on_menu`.
        """
        return self.parent().settings

    def _on_screenshot(self):
        """Export the rendered world-view image to a user-selected file.

        Notes
        -----
        The suggested pathname combines the editor's default directory, the
        active ROM name, and the selected level reference so exported images
        stay recognizable in the same workspace as the ROM. When the user
        accepts the dialog, the method asks :attr:`world_view` for the rendered
        screenshot image and writes it to disk unchanged.
        """
        recommended_file = (
            f"{self.settings.value('editor/default_dir_path')}/{ROM.name} - {self.world_view.level_ref.name}.png"
        )

        pathname, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save Screenshot",
            dir=recommended_file,
            filter=IMG_FILE_FILTER,
        )

        if not pathname:
            return

        self.world_view.make_screenshot().save(pathname)
