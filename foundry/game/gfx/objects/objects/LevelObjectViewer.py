"""
A standalone object viewer for testing and modifying objects
"""

from typing import Optional
import sys
from PySide2.QtWidgets import (
    QApplication, QAction, QDialog, QFileDialog, QMainWindow, QMenu, QMessageBox, QPushButton, QScrollArea, QShortcut,
    QSizePolicy, QSplitter, QToolBar, QWhatsThis, QWidget
)
from PySide2.QtGui import QPaintEvent, QPainter

# change into the tmp directory pyinstaller uses for the data
from foundry.game.File import ROM
from foundry import (
    discord_link, feature_video_link, get_current_version_name, get_latest_version_name, github_link,
    icon, open_url, releases_link,
)
from PySide2.QtGui import Qt

from foundry.gui.SettingsDialog import show_settings, get_gui_style
from foundry.decorators.SaveSettings import handle_settings
from foundry.gui.QMenus.FileMenu import FileMenuLight, OpenRomMenuElement
from foundry.gui.QMenus.HelpMenu import HelpMenu
from foundry.game.gfx.objects.objects.LevelObjectBase import LevelObject
from foundry.decorators.Observer import Observed
from foundry.gui.QSpinner import Spinner
from foundry.gui.QSpinner.PositionSpinner import PositionSpinner
from foundry.gui.QSpinner.SizeSpinner import SizeSpinner
from foundry.gui.Custom.Palette import ColorPicker, PaletteEditor, PaletteSetEditor
from foundry.gui.QCheckBox.SpriteFlipCheckbox import SpriteFlipCheckbox
from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerPopup
from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET, DEFAULT_PALETTE
from foundry.game.gfx.PatternTableHandler import PatternTableHandler, PatternTable
from foundry.gui.Custom.Sprite import SpriteDisplayer
from foundry.gui.QComboBox import ComboBox, ComboBoxOption
from foundry.gui.QSpinner.RectSpinner import RectSpinner
from foundry.gui.QCheckBox import CheckBox
from foundry.gui.QSpinner.HexSpinner import HexSpinner
from foundry.gui.QWidget.Panel import Panel, ReversedPanel
from foundry.gui.QLineEdit import LineEdit
from foundry.gui.QToolbar import Toolbar
from foundry.game.gfx.objects.objects.LevelObjectDefinitionLoader import object_definitions
from foundry.game.gfx.Palette import load_palette
from foundry.game.Size import Size
from foundry.game.Position import Position


ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"


@handle_settings
def main(path_to_rom):
    """Handles the main window"""
    app = QApplication()
    if OpenRomMenuElement(None, False).action():
        MainWindow(path_to_rom)
    app.exec_()


class MainWindow(QMainWindow):
    """The main window for the program"""
    def __init__(self, path_to_rom=""):
        super(MainWindow, self).__init__()
        self.setWindowIcon(icon("tanooki.ico"))
        self.setStyleSheet(get_gui_style())


        self.file_menu = FileMenuLight(self)
        self.menuBar().addMenu(self.file_menu)

        self.menuBar().addMenu(HelpMenu(self))

        # Set the main widget
        self.object_view = ObjectViewer(self, LevelObject(object_definitions[0], load_palette(1, 0)))
        self.scroll_panel = QScrollArea()
        self.scroll_panel.setWidgetResizable(True)
        self.scroll_panel.setWidget(self.object_view)
        self.setCentralWidget(self.scroll_panel)

        name_text = Panel(self, "Name", LineEdit(self, "test"))
        self.name_toolbar = Toolbar.default_toolbox(self, "name_toolbar", name_text, Qt.RightToolBarArea)

        page_spinner = Panel(self, "Page", HexSpinner(self, 0, 0xFF))
        self.page_toolbar = Toolbar.default_toolbox(self, "page_toolbar", page_spinner, Qt.RightToolBarArea)

        graphic_spinner = Panel(self, "Sprite", HexSpinner(self, 0, 0xFF))
        self.graphic_toolbar = Toolbar.default_toolbox(self, "graphic_spinner", graphic_spinner, Qt.RightToolBarArea)

        horizontal_mirror_checkbox = Panel(self, "Horizontal Mirror", CheckBox(self, ""))
        self.horizontal_mirror_toolbar = Toolbar.default_toolbox(
            self, "horizontal_mirror_toolbar", horizontal_mirror_checkbox, Qt.RightToolBarArea
        )

        vertical_mirror_checkbox = ReversedPanel(self, "Vertical Mirror", CheckBox(self, ""))
        self.vertical_mirror_toolbar = Toolbar.default_toolbox(
            self, "vertical_mirror_toolbar", vertical_mirror_checkbox, Qt.RightToolBarArea
        )

        mirror_checkbox = Panel(self, "Mirroring", SpriteFlipCheckbox(self, True))
        self.mirroing_toolbar = Toolbar.default_toolbox(
            self, "mirring_toolbar", mirror_checkbox, Qt.RightToolBarArea
        )

        self.hitbox_toolbar = Toolbar.default_toolbox(
            self, "hitbox_toolbar", RectSpinner(self, "Hitbox"), Qt.RightToolBarArea
        )

        self.bounding_box_toolbox = Toolbar.default_toolbox(
            self, "bounding_box_toolbar", RectSpinner(self, "Bounding Box"), Qt.RightToolBarArea
        )

        self.color_picker_toolbox = Toolbar.default_toolbox(
            self, "color_picker_toolbar", PaletteSetEditor(self), Qt.RightToolBarArea
        )

        c1 = ComboBoxOption("test", lambda *_: print("test goes test"))
        c2 = ComboBoxOption("test 2", lambda *_: print("computer go brrr"))
        dropdown = ComboBox(self, [c1, c2])
        self.drop_down_toolbox = Toolbar.default_toolbox(
            self, "drop_down_toobox", Panel(self, "Test", dropdown), Qt.RightToolBarArea
        )

        print(object_definitions[0].animations, object_definitions[0].hitbox)
        sprite_viewer = SpriteDisplayer(
            self,
            object_definitions[0].hitbox,
            DEFAULT_PALETTE_SET,
            PatternTableHandler(PatternTable(0, 0, 0, 0, 0, 0))
        )
        self.sprite_viewer_toolbox = Toolbar.default_toolbox(
            self, "sprite_viewer_toolbox", Panel(self, "Viewer", sprite_viewer), Qt.RightToolBarArea
        )

        self.showMaximized()


class ObjectViewer(QWidget):
    def __init__(self, parent: QWidget, object: Optional[LevelObject] = None):
        super(ObjectViewer, self).__init__(parent)
        self.level_object = object

        self.update = Observed(self.update)
        self.update.attach_observer(lambda *_: self.resize_by_size_hint)

        self.level_object.action_page.attach_observer(self.update)
        self.level_object.action_palette.attach_observer(self.update)
        self.level_object.action_graphic.attach_observer(self.update)
        self.level_object.action_horizontal_mirror.attach_observer(self.update)
        self.level_object.action_vertical_mirror.attach_observer(self.update)
        self.level_object.action_hitbox.attach_observer(self.update)

        self._zoom = 16


        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

    def resize_by_size_hint(self, *_) -> None:
        """Resizes by the size hint"""
        self.resize(self.sizeHint())

    def update(self):
        """Updates observers to do whatever they need"""

    @property
    def zoom(self):
        """Determines the size of each pixel"""
        return self._zoom

    @zoom.setter
    def zoom(self, zoom: int) -> None:
        if not (0 <= zoom <= 64):
            return

        self._zoom = zoom

        self.update()

    def zoom_out(self):
        """Zooms out by a single unit"""
        self.set_zoom(self.zoom - 1)

    def zoom_in(self):
        """Zooms in by a single unit"""
        self.set_zoom(self.zoom + 1)

    def paintEvent(self, event: QPaintEvent, force=False):
        painter = QPainter(self)
        self.level_object.draw(painter, Position(10, 10), Size(5, 5))
        painter.save()


class LevelObjectDrawer():
    pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = ""

    main(path)
