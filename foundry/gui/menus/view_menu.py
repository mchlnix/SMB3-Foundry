from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMenu

from foundry import IMG_FILE_FILTER, icon
from foundry.game.File import ROM


class ViewMenu(QMenu):
    def __init__(self, level_view, title="&View"):
        super(ViewMenu, self).__init__(title)

        self.triggered.connect(self._on_trigger)

        self._level_view = level_view

        self._grid_action = self._make_action("&Grid lines", "level view/draw_grid")
        self._coord_action = self._make_action("&Coordinates", "level view/draw_grid_coordinates")

        self.addSeparator()

        self._mario_action = self._make_action("&Mario", "level view/draw_mario")
        self._jumps_action = self._make_action("&Jumps on objects", "level view/draw_jump_on_objects")
        self._items_action = self._make_action("&Items in blocks", "level view/draw_items_in_blocks")
        self._invis_action = self._make_action("I&nvisible items", "level view/draw_invisible_items")

        self.addSeparator()

        self._auto_scroll_action = self._make_action("&Autoscroll Path", "level view/draw_autoscroll")
        self._jump_zones_action = self._make_action("Jump &Zones", "level view/draw_jumps")
        self._resize_action = self._make_action("&Resize Type", "level view/draw_expansion")

        self.addSeparator()

        self._anim_action = self._make_action("Show Block Animation", "level view/block_animation")
        self._trans_action = self._make_action("&Block Transparency", "level view/block_transparency")
        self._special_bg_action = self._make_action("Default Background Tiles", "level view/special_background")

        self.addSeparator()

        self._screen_shot_action = self.addAction("Save &Screenshot of Level")
        self._screen_shot_action.setIcon(icon("image.svg"))

    def _make_action(self, title: str, setting_string: str):
        checkable_action = self.addAction(title)
        checkable_action.setCheckable(True)
        checkable_action.setChecked(self.settings.value(setting_string))

        return checkable_action

    @property
    def settings(self):
        return self._level_view.settings

    def _on_trigger(self, action: QAction):
        checked = action.isChecked()

        if action is self._grid_action:
            self.settings.setValue("level view/draw_grid", checked)
        elif action is self._coord_action:
            self.settings.setValue("level view/draw_grid_coordinates", checked)
        elif action is self._anim_action:
            self.settings.setValue("level view/block_animation", checked)
            self._level_view.update_anim_timer()
        elif action is self._trans_action:
            self.settings.setValue("level view/block_transparency", checked)
        elif action is self._jump_zones_action:
            self.settings.setValue("level view/draw_jumps", checked)
        elif action is self._mario_action:
            self.settings.setValue("level view/draw_mario", checked)
        elif action is self._resize_action:
            self.settings.setValue("level view/draw_expansion", checked)
        elif action is self._jumps_action:
            self.settings.setValue("level view/draw_jump_on_objects", checked)
        elif action is self._items_action:
            self.settings.setValue("level view/draw_items_in_blocks", checked)
        elif action is self._invis_action:
            self.settings.setValue("level view/draw_invisible_items", checked)
        elif action is self._auto_scroll_action:
            self.settings.setValue("level view/draw_autoscroll", checked)
        elif action is self._special_bg_action:
            self.settings.setValue("level view/special_background", checked)
        elif action is self._screen_shot_action:
            self._on_screenshot()
            return

        self._level_view.update()

        self.exec_()

    def _on_screenshot(self):
        recommended_file = (
            f"{self.settings.value('editor/default dir path')}/{ROM.name} - {self._level_view.level_ref.name}.png"
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
