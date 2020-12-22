

from typing import Optional

from PySide2.QtWidgets import QBoxLayout
from PySide2.QtGui import Qt

from foundry import icon

from foundry.core.geometry.Size.Size import Size

from foundry.gui.QMenus.Menu.MenuFileLight import FileMenuLight
from foundry.gui.QMainWindow.ChildWindow import ChildWindow
from foundry.gui.QToolbar import Toolbar
from foundry.gui.Custom.Palette import PaletteSetEditor
from foundry.gui.Custom.Palette.Selector import PaletteSelector
from foundry.gui.QSpinner.HexSpinner import HexSpinner
from foundry.gui.QWidget.Panel import Panel
from foundry.gui.Custom.Block.BlockEditor import BlockEditor
from foundry.gui.Custom.Block.BlockWidget import BlockWidget
from foundry.gui.Custom.Block.Block import Block

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import load_palette

from .TileSquareAssemblyViewer import TileSquareAssemblyViewer


class DialogTileSquareAssemblyEditor(ChildWindow):
    """The viewer of the TSA editor"""

    def __init__(self, parent):
        super(DialogTileSquareAssemblyEditor, self).__init__(parent, title="Tile Square Assembly Editor")
        self.setWindowIcon(icon("tanooki.ico"))

        # Add a default file menu
        self.file_menu = FileMenuLight(self)
        self.menuBar().addMenu(self.file_menu)

        self.tileset_toolbar = Toolbar.default_toolbox(
            self, "tileset_toolbar", Panel(self, "Tileset", HexSpinner(self, 0, 0xFF)), Qt.RightToolBarArea
        )

        self.tsa_offset = Toolbar.default_toolbox(
            self, "offset", Panel(self, "Offset", HexSpinner(self, 0, 0xFF)), Qt.RightToolBarArea
        )

        palette_selector = Panel(self, "Palette", PaletteSelector(self, 0))
        self.palette_selector_toolbar = Toolbar.default_toolbox(
            self, "palette_selector_toolbar", palette_selector, Qt.RightToolBarArea
        )

        self.color_picker_toolbox = Toolbar.default_toolbox(
            self, "color_picker_toolbar", PaletteSetEditor(self), Qt.RightToolBarArea
        )

        ptn_tbl = PatternTableHandler.from_tileset(1)
        palette = load_palette(1, 0)
        tsa_offset = 15

        self.block_editor_toolbox = Toolbar.default_toolbox(
            self, "block_editor_toolbar", BlockEditor(
                self, BlockWidget(
                    self, "Block", Block.from_tsa(
                        Size(3, 3), 0, ptn_tbl, palette, tsa_offset
                    )
                )
            ), Qt.RightToolBarArea
        )

        self.tsa_viewer = TileSquareAssemblyViewer(self, ptn_tbl, palette, tsa_offset)
        self.setCentralWidget(self.tsa_viewer)

        self.showMaximized()


