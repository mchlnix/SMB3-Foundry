import os
from logging import error
from typing import Tuple
from warnings import warn

from PySide2.QtGui import QIcon, Qt, QCloseEvent, QWheelEvent, QKeySequence
from PySide2.QtWidgets import (
    QMenu,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QDialog,
    QAction,
    QScrollArea,
    QToolBar,
    QSplitter,
    QSizePolicy,
    QShortcut,
)

from foundry.game.File import ROM
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.AboutWindow import AboutDialog
from foundry.gui.BlockViewer import BlockViewer
from foundry.gui.ContextMenu import (
    ContextMenu,
    ID_CTX_REMOVE,
    ID_CTX_ADD_OBJECT,
    ID_CTX_ADD_ENEMY,
    ID_CTX_COPY,
    ID_CTX_PASTE,
    ID_CTX_CUT,
)
from foundry.gui.HeaderEditor import HeaderEditor
from foundry.gui.JumpEditor import JumpEditor
from foundry.gui.JumpList import JumpList
from foundry.gui.LevelSelector import LevelSelector
from foundry.gui.LevelView import LevelView
from foundry.gui.ObjectDropdown import ObjectDropdown
from foundry.gui.ObjectList import ObjectList
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.ObjectViewer import ObjectViewer
from foundry.gui.SpinnerPanel import SpinnerPanel

ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"
M3L_FILE_FILTER = "M3L files (*.m3l);;All files (*)"
IMG_FILE_FILTER = "Screenshots (*.png);;All files (*)"

# file menu

ID_OPEN_ROM = 101
ID_OPEN_M3L = 102
ID_SAVE_ROM = 103
ID_SAVE_M3L = 104
ID_SAVE_LEVEL_TO = 105
ID_SAVE_ROM_AS = 106
ID_APPLY_IPS_PATCH = 107
ID_ROM_PRESET = 108
ID_EXIT = 109

# edit menu

ID_EDIT_LEVEL = 201
ID_EDIT_OBJ_DEFS = 202
ID_EDIT_PALETTE = 203
ID_EDIT_GRAPHICS = 204
ID_EDIT_MISC = 205
ID_FREE_FORM_MODE = 206
ID_LIMIT_SIZE = 207

# level menu

ID_GOTO_NEXT_AREA = 301
ID_SELECT_LEVEL = 302
ID_RELOAD_LEVEL = 303
ID_EDIT_HEADER = 304
ID_EDIT_POINTERS = 305

# object menu

ID_VIEW_BLOCKS = 401
ID_CLONE_OBJECT_ENEMY = 402
ID_ADD_3_BYTE_OBJECT = 403
ID_ADD_4_BYTE_OBJECT = 404
ID_ADD_ENEMY = 405
ID_DELETE_OBJECT_ENEMY = 406
ID_DELETE_ALL = 407
ID_VIEW_OBJECTS = 408

# view menu

ID_GRID_LINES = 501
ID_BACKGROUND_FLOOR = 502
ID_TOOLBAR = 503
ID_ZOOM = 504
ID_USE_ROM_GRAPHICS = 505
ID_PALETTE = 506
ID_MORE = 507
ID_TRANSPARENCY = 508
ID_JUMPS = 509
ID_SCREEN_SHOT = 510

# help menu

ID_ENEMY_COMPATIBILITY = 601
ID_TROUBLESHOOTING = 602
ID_PROGRAM_WEBSITE = 603
ID_MAKE_A_DONATION = 604
ID_ABOUT = 605

CHECKABLE_MENU_ITEMS = [ID_TRANSPARENCY, ID_GRID_LINES, ID_JUMPS]

# mouse modes

MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE = 2


def undoable(func):
    def wrapped(self, *args):
        func(self, *args)
        self.level_ref.save_level_state()

    return wrapped


class SMB3Foundry(QMainWindow):
    def __init__(self):
        super(SMB3Foundry, self).__init__()

        self.setWindowIcon(QIcon("data/foundry.ico"))

        file_menu = QMenu("File")

        open_rom_action = file_menu.addAction("&Open ROM")
        open_rom_action.triggered.connect(self.on_open_rom)
        open_m3l_action = file_menu.addAction("&Open M3L")
        open_m3l_action.triggered.connect(self.on_open_m3l)

        file_menu.addSeparator()

        save_rom_action = file_menu.addAction("&Save ROM")
        save_rom_action.triggered.connect(self.on_save_rom)
        save_rom_as_action = file_menu.addAction("&Save ROM as ...")
        save_rom_as_action.triggered.connect(self.on_save_rom_as)
        """
        file_menu.AppendSeparator()
        """
        self.save_m3l_action = file_menu.addAction("&Save M3L")
        self.save_m3l_action.triggered.connect(self.on_save_m3l)
        """
        file_menu.Append(ID_SAVE_LEVEL_TO, "&Save Level to", "")
        file_menu.AppendSeparator()
        file_menu.Append(ID_APPLY_IPS_PATCH, "&Apply IPS Patch", "")
        file_menu.AppendSeparator()
        file_menu.Append(ID_ROM_PRESET, "&ROM Preset", "")
        """
        file_menu.addSeparator()
        exit_action = file_menu.addAction("&Exit")
        exit_action.triggered.connect(lambda _: self.close())

        self.menuBar().addMenu(file_menu)

        """
        edit_menu = wx.Menu()

        edit_menu.Append(ID_EDIT_LEVEL, "&Edit Level", "")
        edit_menu.Append(ID_EDIT_OBJ_DEFS, "&Edit Object Definitions", "")
        edit_menu.Append(ID_EDIT_PALETTE, "&Edit Palette", "")
        edit_menu.Append(ID_EDIT_GRAPHICS, "&Edit Graphics", "")
        edit_menu.Append(ID_EDIT_MISC, "&Edit Miscellaneous", "")
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_FREE_FORM_MODE, "&Free form Mode", "")
        edit_menu.Append(ID_LIMIT_SIZE, "&Limit Size", "")
        """

        level_menu = QMenu("Level")

        select_level_action = level_menu.addAction("&Select Level")
        select_level_action.triggered.connect(self.open_level_selector)

        """
        level_menu.Append(ID_GOTO_NEXT_AREA, "&Go to next Area", "")
        level_menu.AppendSeparator()
        """
        level_menu.addAction("&Reload Level")
        level_menu.addSeparator()
        self.edit_header_action = level_menu.addAction("&Edit Header")
        self.edit_header_action.triggered.connect(self.on_header_editor)
        """
        level_menu.Append(ID_EDIT_POINTERS, "&Edit Pointers", "")
        """

        self.menuBar().addMenu(level_menu)

        object_menu = QMenu("Objects")

        view_blocks_action = object_menu.addAction("&View Blocks")
        view_blocks_action.triggered.connect(self.on_block_viewer)
        view_objects_action = object_menu.addAction("&View Objects")
        view_objects_action.triggered.connect(self.on_object_viewer)
        """
        object_menu.AppendSeparator()
        object_menu.Append(ID_CLONE_OBJECT_ENEMY, "&Clone Object/Enemy", "")
        object_menu.AppendSeparator()
        object_menu.Append(ID_ADD_3_BYTE_OBJECT, "&Add 3 Byte Object", "")
        object_menu.Append(ID_ADD_4_BYTE_OBJECT, "&Add 4 Byte Object", "")
        object_menu.Append(ID_ADD_ENEMY, "&Add Enemy", "")
        object_menu.AppendSeparator()
        object_menu.Append(ID_DELETE_OBJECT_ENEMY, "&Delete Object/Enemy", "")
        object_menu.Append(ID_DELETE_ALL, "&Delete All", "")
        """

        self.menuBar().addMenu(object_menu)

        view_menu = QMenu("View")
        view_menu.triggered.connect(self.on_menu)

        self._show_jump_action = view_menu.addAction("Jumps")
        self._show_jump_action.setProperty("ID", ID_JUMPS)
        self._show_jump_action.setCheckable(True)

        self._show_grid_action = view_menu.addAction("&Grid lines")
        self._show_grid_action.setProperty("ID", ID_GRID_LINES)
        self._show_grid_action.setCheckable(True)

        self._show_transparent_blocks_action = view_menu.addAction("&Block Transparency")
        self._show_transparent_blocks_action.setProperty("ID", ID_TRANSPARENCY)
        self._show_transparent_blocks_action.setCheckable(True)
        self._show_transparent_blocks_action.setChecked(True)

        view_menu.addSeparator()
        view_menu.addAction("&Save Screenshot of Level").triggered.connect(self.on_screenshot)
        """
        view_menu.Append(ID_BACKGROUND_FLOOR, "&Background & Floor", "")
        view_menu.Append(ID_TOOLBAR, "&Toolbar", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_ZOOM, "&Zoom", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_USE_ROM_GRAPHICS, "&Use ROM Graphics", "")
        view_menu.Append(ID_PALETTE, "&Palette", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_MORE, "&More", "")
        """

        self.menuBar().addMenu(view_menu)

        help_menu = QMenu("Help")
        """
        help_menu.Append(ID_ENEMY_COMPATIBILITY, "&Enemy Compatibility", "")
        help_menu.Append(ID_TROUBLESHOOTING, "&Troubleshooting", "")
        help_menu.AppendSeparator()
        help_menu.Append(ID_PROGRAM_WEBSITE, "&Program Website", "")
        help_menu.Append(ID_MAKE_A_DONATION, "&Make a Donation", "")
        help_menu.AppendSeparator()
        """
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.on_about)

        self.menuBar().addMenu(help_menu)

        self.level_selector = LevelSelector(parent=self)

        self.block_viewer = None
        self.object_viewer = None

        self.context_menu = ContextMenu()
        self.context_menu.triggered.connect(self.on_menu)

        self.scroll_panel = QScrollArea()

        self.level_ref = LevelRef()

        self.level_view = LevelView(self, self.level_ref, self.context_menu)
        self.scroll_panel.setWidget(self.level_view)

        self.setCentralWidget(self.scroll_panel)

        self.spinner_panel = SpinnerPanel(self, self.level_ref)
        self.spinner_panel.zoom_in_triggered.connect(self.level_view.zoom_in)
        self.spinner_panel.zoom_out_triggered.connect(self.level_view.zoom_out)
        self.spinner_panel.object_change.connect(self.on_spin)

        self.object_list = ObjectList(self, self.level_ref, self.context_menu)

        self.object_dropdown = ObjectDropdown(self)

        self.jump_list = JumpList(self, self.level_ref)
        self.jump_list.add_jump.connect(self.on_jump_added)
        self.jump_list.edit_jump.connect(self.on_jump_edit)
        self.jump_list.remove_jump.connect(self.on_jump_removed)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)

        splitter.addWidget(self.object_list)
        splitter.setStretchFactor(0, 1)
        splitter.addWidget(self.jump_list)

        splitter.setChildrenCollapsible(False)

        toolbar = QToolBar(self)
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        toolbar.setOrientation(Qt.Vertical)
        toolbar.setFloatable(False)

        toolbar.addWidget(self.spinner_panel)
        toolbar.addWidget(self.object_dropdown)
        toolbar.addWidget(splitter)

        toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea)

        self.addToolBar(Qt.RightToolBarArea, toolbar)

        self.status_bar = ObjectStatusBar(self, self.level_ref)
        self.setStatusBar(self.status_bar)

        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self, self.remove_selected_objects)

        self.cut_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_X), self, self._cut_objects)
        self.copy_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self, self._copy_objects)
        self.paste_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self, self._paste_objects)

        if not self.on_open_rom():
            self.deleteLater()

        self.showMaximized()

    def on_screenshot(self, _) -> bool:
        if self.level_view is None:
            return False

        recommended_file = f"{os.path.expanduser('~')}/{ROM.name} - {self.level_view.level_ref.name}.png"

        pathname, _ = QFileDialog.getSaveFileName(
            self, caption="Save Screenshot", dir=recommended_file, filter=IMG_FILE_FILTER
        )

        # Proceed loading the file chosen by the user
        self.level_view.make_screenshot().save(pathname)

        return True

    def update_title(self):
        if self.level_view.level_ref is not None and ROM is not None:
            title = f"{self.level_view.level_ref.name} - {ROM.name}"
        else:
            title = "SMB3Foundry"

        self.setWindowTitle(title)

    def on_open_rom(self) -> bool:
        if not self.safe_to_change():
            return False

        # otherwise ask the user what new file to open
        pathname, _ = QFileDialog.getOpenFileName(self, caption="Open ROM", filter=ROM_FILE_FILTER)

        if not pathname:
            return False

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(pathname)

            return self.open_level_selector(None)

        except IOError:
            warn(f"Cannot open file '{pathname}'.")
            return False

    def on_open_m3l(self, _) -> bool:
        if not self.safe_to_change():
            return False

        # otherwise ask the user what new file to open
        pathname, _ = QFileDialog.getOpenFileName(self, caption="Open M3L file", filter=M3L_FILE_FILTER)

        if not pathname:
            return False

        # Proceed loading the file chosen by the user
        try:
            with open(pathname, "rb") as m3l_file:

                self.level_view.from_m3l(bytearray(m3l_file.read()))
        except IOError:
            warn(f"Cannot open file '{pathname}'.")

            return False

        self.level_view.level_ref.name = os.path.basename(pathname)

        self.set_up_gui_for_level()

        return True

    def safe_to_change(self) -> bool:
        if not self.level_ref:
            return True

        if self.level_ref.changed:
            answer = QMessageBox.question(
                self,
                "Please confirm",
                "Current content has not been saved! Proceed?",
                QMessageBox.No | QMessageBox.Yes,
                QMessageBox.No,
            )

            return answer == QMessageBox.Yes
        else:
            return True

    def on_save_rom(self, _):
        self.save_rom(False)

    def on_save_rom_as(self, _):
        self.save_rom(True)

    def save_rom(self, is_save_as):

        safe_to_save, reason, additional_info = self.level_view.level_safe_to_save()

        if not safe_to_save:
            answer = QMessageBox.warning(
                self,
                reason,
                f"{additional_info}\n\nDo you want to proceed?",
                QMessageBox.No | QMessageBox.Yes,
                QMessageBox.No,
            )

            if answer == QMessageBox.No:
                return

        if not self.level_view.level_ref.attached_to_rom:
            QMessageBox.information(
                self,
                "Importing M3L into ROM",
                "Please select the positions in the ROM you want the level objects and enemies/items to be stored.",
                QMessageBox.Ok,
            )

            answer = self.level_selector.exec_()

            if answer == QMessageBox.OK:
                self.level_view.level_ref.attach_to_rom(
                    self.level_selector.object_data_offset, self.level_selector.enemy_data_offset
                )

                if is_save_as:
                    # if we save to another rom, don't consider the level
                    # attached (to the current rom)
                    self.level_view.level_ref.attached_to_rom = False
            else:
                return

        if is_save_as:
            pathname, _ = QFileDialog.getSaveFileName(self, caption="Save ROM as", filter=ROM_FILE_FILTER)
            if pathname is None:
                return  # the user changed their mind
        else:
            pathname = ROM.path

        try:
            level = self.level_view.level_ref

            for offset, data in level.to_bytes():
                ROM().bulk_write(data, offset)

            ROM().save_to_file(pathname)

            self.update_title()

            self.level_view.level_ref.changed = False
        except IOError:
            warn("Cannot save current data in file '%s'." % pathname)

    def on_save_m3l(self, _):
        suggested_file = self.level_view.level_ref.name

        if not suggested_file.endswith(".m3l"):
            suggested_file += ".m3l"

        pathname, _ = QFileDialog.getSaveFileName(self, caption="Save M3L as", filter=M3L_FILE_FILTER)

        if not pathname:
            return

        try:
            level = self.level_view.level_ref

            with open(pathname, "wb") as m3l_file:
                m3l_file.write(level.to_m3l())
        except IOError:
            error(f"Cannot save current data in file '{pathname}'.")

    def on_menu(self, action: QAction):
        item_id = action.property("ID")

        if item_id in CHECKABLE_MENU_ITEMS:
            self.on_menu_item_checked(action)

        elif item_id in self.context_menu.get_all_menu_item_ids():
            x, y = self.context_menu.get_position()

            if item_id == ID_CTX_REMOVE:
                self.remove_selected_objects()
            elif item_id == ID_CTX_ADD_OBJECT:
                selected_object = self.object_dropdown.currentIndex()

                if selected_object == -1:
                    self.create_object_at(x, y)
                else:
                    self.place_object_from_dropdown((x, y))
            elif item_id == ID_CTX_ADD_ENEMY:
                self.create_enemy_at(x, y)
            elif item_id == ID_CTX_CUT:
                self._cut_objects()
            elif item_id == ID_CTX_COPY:
                self._copy_objects()
            elif item_id == ID_CTX_PASTE:
                self._paste_objects(x, y)

            self.object_list.update()

        elif item_id == ID_RELOAD_LEVEL:
            self.reload_level()

        self.level_view.update()

    def reload_level(self):
        if not self.safe_to_change():
            return

        world = self.level_view.level_ref.world
        level = self.level_view.level_ref.level
        object_data = self.level_view.level_ref.object_offset
        enemy_data = self.level_view.level_ref.enemy_offset
        object_set = self.level_view.level_ref.object_set

        self.update_level(world, level, object_data, enemy_data, object_set)

    @undoable
    def create_object_at(self, x, y):
        self.level_view.create_object_at(x, y)

    @undoable
    def create_enemy_at(self, x, y):
        self.level_view.create_enemy_at(x, y)

    def _cut_objects(self):
        self._copy_objects()
        self.remove_selected_objects()

    def _copy_objects(self):
        selected_objects = self.level_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

    @undoable
    def _paste_objects(self, x=None, y=None):
        self.level_view.paste_objects_at(self.context_menu.get_copied_objects(), x, y)

        self.object_list.update()

    @undoable
    def remove_selected_objects(self):
        self.level_view.remove_selected_objects()
        self.level_view.update()
        self.object_list.update()
        self.spinner_panel.disable_all()

    def on_menu_item_checked(self, action: QAction):
        item_id = action.property("ID")

        checked = action.isChecked()

        if item_id == ID_GRID_LINES:
            self.level_view.grid_lines = checked
        elif item_id == ID_TRANSPARENCY:
            self.level_view.transparency = checked
        elif item_id == ID_JUMPS:
            self.level_view.jumps = checked

    @undoable
    def on_spin(self, _):
        selected_objects = self.level_ref.selected_objects

        assert len(selected_objects) == 1, print(selected_objects)

        selected_object = selected_objects[0]

        obj_type = self.spinner_panel.get_type()

        if isinstance(selected_object, LevelObject):
            domain = self.spinner_panel.get_domain()

            if selected_object.is_4byte:
                length = self.spinner_panel.get_length()
            else:
                length = None

            self.level_view.replace_object(selected_object, domain, obj_type, length)
        else:
            self.level_view.replace_enemy(selected_object, obj_type)

        self.level_ref.data_changed.emit()

    def fill_object_list(self):
        self.object_list.Clear()

        self.object_list.SetItems(self.level_view.get_object_names())

    def open_level_selector(self, _):
        if not self.safe_to_change():
            return

        level_was_selected = self.level_selector.exec_() == QDialog.Accepted

        if level_was_selected:
            self.update_level(
                self.level_selector.selected_world,
                self.level_selector.selected_level,
                self.level_selector.object_data_offset,
                self.level_selector.enemy_data_offset,
                self.level_selector.object_set,
            )

        return level_was_selected

    def on_block_viewer(self, _):
        if self.block_viewer is None:
            self.block_viewer = BlockViewer(parent=self)

        self.block_viewer.show()

    def on_object_viewer(self, _):
        if self.object_viewer is None:
            self.object_viewer = ObjectViewer(parent=self)

        self.object_viewer.show()

    def on_header_editor(self, _):
        HeaderEditor(self, self.level_ref).exec_()

    def update_level(self, world: int, level: int, object_data_offset: int, enemy_data_offset: int, object_set: int):
        try:
            self.level_ref.load_level(world, level, object_data_offset, enemy_data_offset, object_set)
        except IndexError:
            QMessageBox.critical(self, "Please confirm", "Failed loading level. The level offsets don't match.")

            return

        self.set_up_gui_for_level()

    def set_up_gui_for_level(self):
        self.object_list.update()
        self.update_title()
        self.jump_list.update()

        is_a_world_map = self.level_view.level_ref.world == 0

        self.save_m3l_action.setEnabled(not is_a_world_map)
        self.edit_header_action.setEnabled(not is_a_world_map)

        if is_a_world_map:
            self.object_dropdown.Clear()
            self.object_dropdown.setEnabled(False)

            self.jump_list.setEnabled(False)
            self.jump_list.Clear()
        else:
            self.object_dropdown.setEnabled(True)
            self.object_dropdown.set_object_factory(self.level_view.level_ref.object_factory)

            self.jump_list.setEnabled(True)

        self.level_view.update()

    def on_jump_edit(self):
        index = self.jump_list.currentIndex().row()

        jump_editor = JumpEditor(self, self.level_view.level_ref.jumps[index], index)

        jump_editor.jump_updated.connect(self.on_jump_edited)

        jump_editor.exec_()

    @undoable
    def on_jump_added(self):
        self.level_view.add_jump()

    @undoable
    def on_jump_removed(self):
        self.level_view.remove_jump(self.jump_list.currentIndex())

    @undoable
    def on_jump_edited(self, jump):
        index = self.jump_list.currentIndex().row()

        assert index >= 0

        if isinstance(self.level_view.level_ref, Level):
            self.level_view.level_ref.jumps[index] = jump
            self.jump_list.item(index).setText(str(jump))

    def on_jump_list_change(self, event):
        self.jump_list.set_jumps(event)

    def on_middle_click(self, event):
        pos = event.pos().toTuple()

        self.place_object_from_dropdown(pos)

    @undoable
    def place_object_from_dropdown(self, pos: Tuple[int, int]) -> None:
        domain, object_index = self.object_dropdown.currentData(Qt.UserRole)

        self.level_view.create_object_at(*pos, domain, object_index)

        self.object_list.update()

    def wheelEvent(self, event: QWheelEvent):
        x, y = event.pos().toTuple()

        obj_under_cursor = self.level_view.object_at(x, y)

        if obj_under_cursor is None:
            return
        else:
            if isinstance(self.level_view.level_ref, WorldMap):
                return

            # scrolling through the level could unintentionally change objects, if the cursor would wander onto them.
            # this is annoying (to me) so only change already selected objects
            if obj_under_cursor not in self.level_view.selected_objects:
                return

            self.change_object_on_mouse_wheel(event)

    @undoable
    def change_object_on_mouse_wheel(self, event: QWheelEvent):
        x, y = event.pos().toTuple()

        obj_under_cursor = self.level_view.object_at(x, y)

        if event.angleDelta() > 0:
            obj_under_cursor.increment_type()
        else:
            obj_under_cursor.decrement_type()

        obj_under_cursor.selected = True

    def on_about(self, _):
        about = AboutDialog(self)

        about.show()

    def closeEvent(self, event: QCloseEvent):
        if not self.safe_to_change():
            event.ignore()

            return

        super(SMB3Foundry, self).closeEvent(event)
