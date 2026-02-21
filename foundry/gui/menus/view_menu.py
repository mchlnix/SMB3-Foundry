from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMenu

from foundry import IMG_FILE_FILTER, icon
from foundry.game.File import ROM


class ViewMenu(QMenu):
    # TRANSLATORS: Ampersand designates keyboard shortcut key
    def __init__(self, level_view, title=_("&View")):
        super(ViewMenu, self).__init__(title)

        self.triggered.connect(self._on_trigger)

        self._level_view = level_view

        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._grid_action = self._make_action(_("&Grid lines"), "level view/draw_grid")
        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._coord_action = self._make_action(
            _("&Coordinates"), "level view/draw_grid_coordinates"
        )

        self.addSeparator()

        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._mario_action = self._make_action(_("&Mario"), "level view/draw_mario")
        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._jumps_action = self._make_action(
            _("&Jumps on objects"), "level view/draw_jump_on_objects"
        )
        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._items_action = self._make_action(
            _("&Items in blocks"), "level view/draw_items_in_blocks"
        )
        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._invis_action = self._make_action(
            _("I&nvisible items"), "level view/draw_invisible_items"
        )

        self.addSeparator()

        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._auto_scroll_action = self._make_action(
            _("&Autoscroll Path"), "level view/draw_autoscroll"
        )
        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._jump_zones_action = self._make_action(
            _("Jump &Zones"), "level view/draw_jumps"
        )
        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._resize_action = self._make_action(
            _("&Resize Type"), "level view/draw_expansion"
        )

        self.addSeparator()

        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._anim_action = self._make_action(
            _("Show Block Animation"), "level view/block_animation"
        )
        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._trans_action = self._make_action(
            _("&Block Transparency"), "level view/block_transparency"
        )
        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._special_bg_action = self._make_action(
            _("Default Background Tiles"), "level view/special_background"
        )

        self.addSeparator()

        # TRANSLATORS: Ampersand designates keyboard shortcut key
        self._screen_shot_action = self.addAction(_("Save &Screenshot of Level"))
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
        recommended_file = f"{self.settings.value('editor/default dir path')}/{ROM.name} - {self._level_view.level_ref.name}.png"

        pathname, __ = QFileDialog.getSaveFileName(
            self,
            caption=_("Save Screenshot"),
            dir=recommended_file,
            filter=IMG_FILE_FILTER,
        )

        if not pathname:
            return

        self._level_view.make_screenshot().save(pathname)
