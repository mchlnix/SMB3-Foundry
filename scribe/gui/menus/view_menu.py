from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QFileDialog, QMenu

from foundry import IMG_FILE_FILTER, icon
from foundry.game.File import ROM
from foundry.gui.visualization.world.WorldView import WorldView
from smb3parse.constants import AIRSHIP_TRAVEL_SET_COUNT


class ViewMenu(QMenu):
    def __init__(self, parent, world_view: WorldView):
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
        return self.parent().settings

    def _on_screenshot(self):
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
