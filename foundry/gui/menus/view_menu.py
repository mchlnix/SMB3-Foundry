import os

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMenu

from foundry import IMG_FILE_FILTER
from foundry.game.File import ROM
from foundry.gui.settings import SETTINGS, save_settings


class ViewMenu(QMenu):
    def __init__(self, level_view, title="&View"):
        super(ViewMenu, self).__init__(title)

        self.triggered.connect(self._on_trigger)

        self._level_view = level_view

        self._mario_action = self.addAction("&Mario")
        self._mario_action.setCheckable(True)
        self._mario_action.setChecked(SETTINGS["draw_mario"])

        self._jumps_action = self.addAction("&Jumps on objects")
        self._jumps_action.setCheckable(True)
        self._jumps_action.setChecked(SETTINGS["draw_jump_on_objects"])

        self._items_action = self.addAction("&Items in blocks")
        self._items_action.setCheckable(True)
        self._items_action.setChecked(SETTINGS["draw_items_in_blocks"])

        self._invis_action = self.addAction("I&nvisible items")
        self._invis_action.setCheckable(True)
        self._invis_action.setChecked(SETTINGS["draw_invisible_items"])

        self._auto_scroll_action = self.addAction("&Autoscroll Path")
        self._auto_scroll_action.setCheckable(True)
        self._auto_scroll_action.setChecked(SETTINGS["draw_autoscroll"])

        self.addSeparator()

        self._jump_zones_action = self.addAction("Jump &Zones")
        self._jump_zones_action.setCheckable(True)
        self._jump_zones_action.setChecked(SETTINGS["draw_jumps"])

        self._grid_action = self.addAction("&Grid lines")
        self._grid_action.setCheckable(True)
        self._grid_action.setChecked(SETTINGS["draw_grid"])

        self._resize_action = self.addAction("&Resize Type")
        self._resize_action.setCheckable(True)
        self._resize_action.setChecked(SETTINGS["draw_expansion"])

        self.addSeparator()

        self._trans_action = self.addAction("&Block Transparency")
        self._trans_action.setCheckable(True)
        self._trans_action.setChecked(SETTINGS["block_transparency"])

        self.addSeparator()
        self._screen_shot_action = self.addAction("Save &Screenshot of Level")

    def _on_trigger(self, action: QAction):
        checked = action.isChecked()

        if action is self._grid_action:
            self._level_view.draw_grid = checked
        elif action is self._trans_action:
            self._level_view.transparency = checked
        elif action is self._jump_zones_action:
            self._level_view.draw_jumps = checked
        elif action is self._mario_action:
            self._level_view.draw_mario = checked
        elif action is self._resize_action:
            self._level_view.draw_expansions = checked
        elif action is self._jumps_action:
            self._level_view.draw_jumps_on_objects = checked
        elif action is self._items_action:
            self._level_view.draw_items_in_blocks = checked
        elif action is self._invis_action:
            self._level_view.draw_invisible_items = checked
        elif action is self._auto_scroll_action:
            self._level_view.draw_autoscroll = checked
        elif action is self._screen_shot_action:
            self._on_screenshot()
            return

        SETTINGS["draw_mario"] = self._level_view.draw_mario
        SETTINGS["draw_jumps"] = self._level_view.draw_jumps
        SETTINGS["draw_grid"] = self._level_view.draw_grid
        SETTINGS["draw_expansion"] = self._level_view.draw_expansions
        SETTINGS["draw_jump_on_objects"] = self._level_view.draw_jumps_on_objects
        SETTINGS["draw_items_in_blocks"] = self._level_view.draw_items_in_blocks
        SETTINGS["draw_invisible_items"] = self._level_view.draw_invisible_items
        SETTINGS["draw_autoscroll"] = self._level_view.draw_autoscroll
        SETTINGS["block_transparency"] = self._level_view.transparency

        save_settings()

        self._level_view.update()

        self.exec_()

    def _on_screenshot(self):
        recommended_file = f"{os.path.expanduser('~')}/{ROM.name} - {self._level_view.level_ref.name}.png"

        pathname, _ = QFileDialog.getSaveFileName(
            self, caption="Save Screenshot", dir=recommended_file, filter=IMG_FILE_FILTER
        )

        if not pathname:
            return

        self._level_view.make_screenshot().save(pathname)
