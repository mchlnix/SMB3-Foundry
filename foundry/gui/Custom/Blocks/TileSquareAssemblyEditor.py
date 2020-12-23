


from PySide2.QtGui import Qt

from foundry import icon

from foundry.core.geometry.Size.Size import Size

from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET
from foundry.game.gfx.Palette import PaletteSet, Palette
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

        self.tileset_spinner = HexSpinner(self, maximum=0xFF)
        self.tileset_spinner.setValue(15)
        self.tileset_toolbar = Toolbar.default_toolbox(
            self, "tileset_toolbar", Panel(self, "Tileset", self.tileset_spinner), Qt.RightToolBarArea
        )

        self.tsa_offset = Toolbar.default_toolbox(
            self, "offset", Panel(self, "Offset", HexSpinner(self, 0, 0xFF)), Qt.RightToolBarArea
        )

        self._palette_set = DEFAULT_PALETTE_SET
        self._palette_index = 0
        self.color_picker = PaletteSetEditor(self, self.palette_set)
        self.palette_selector = PaletteSelector(self, self.palette_index, self.palette_set)
        self.palette_selector_toolbar = Toolbar.default_toolbox(
            self, "palette_selector_toolbar", Panel(self, "Palette", self.palette_selector), Qt.RightToolBarArea
        )

        self.color_picker_toolbox = Toolbar.default_toolbox(
            self, "color_picker_toolbar", self.color_picker, Qt.RightToolBarArea
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

        self.tsa_viewer = TileSquareAssemblyViewer.from_tsa(self, ptn_tbl, palette, tsa_offset)
        self.setCentralWidget(self.tsa_viewer)

        self.color_picker.palette_set_changed_action.observer.attach_observer(lambda p: setattr(self, "palette_set", p))
        self.palette_selector.palette_changed_action.observer.attach_observer(
            lambda p: setattr(self, "palette", p)
        )

        self.tileset_spinner.value_changed_action.observer.attach_observer(
            lambda offset: setattr(self.tsa_viewer, "tsa_data", self.tsa_viewer.tsa_data_from_tsa_offset(offset))
        )

        self.showMaximized()

    def _push_palette_set(self) -> None:
        """Pushes the palette set to the gui"""
        self.color_picker._palette_set = self.palette_set  # Note: Push directly to avoid recursion issues
        self.color_picker._push_palette_set()
        self.palette_selector._palette_set = self.palette_set
        self.palette_selector._update_palette()
        self.tsa_viewer.palette_set = self.palette_set

    @property
    def palette_set(self) -> PaletteSet:
        """The palette set used by the editor"""
        return self._palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self._palette_set = palette_set
        self._push_palette_set()

    @property
    def palette(self) -> Palette:
        """The palette used by the editor"""
        return self.palette_set[self.palette_index]

    @palette.setter
    def palette(self, palette: Palette) -> None:
        self._palette_set[self.palette_index] = palette
        self._push_palette_set()

    @property
    def palette_index(self) -> int:
        """The index of the currently active palette"""
        return self._palette_index

    @palette_index.setter
    def palette_index(self, index: int) -> None:
        if index != self.palette_index:
            self.palette_index = index
            self.palette_selector.index = self.palette_index
