


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

        self.tsa_viewer = None
        self.tileset = 1
        self.tileset_spinner = HexSpinner(self, maximum=0xFF)
        self.tileset_spinner.setValue(self.tileset)
        self.tileset_toolbar = Toolbar.default_toolbox(
            self, "tileset_toolbar", Panel(self, "Tileset", self.tileset_spinner), Qt.RightToolBarArea
        )

        self._offset = 15
        self.offset_spinner = HexSpinner(self, maximum=0xFF)
        self.offset_spinner.setValue(self.offset)
        self.tsa_offset = Toolbar.default_toolbox(
            self, "offset", Panel(self, "Offset", self.offset_spinner), Qt.RightToolBarArea
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

        self.block_editor = BlockEditor(self, BlockWidget(
                self, "Block", Block.from_tsa(Size(3, 3), 0, self.pattern_table, self.palette_set, self.offset)
        ))
        self.block_editor_toolbox = Toolbar.default_toolbox(
            self, "block_editor_toolbar", self.block_editor, Qt.RightToolBarArea
        )

        self.tsa_viewer = TileSquareAssemblyViewer.from_tsa(self, self.pattern_table, self.palette_set, self.offset)
        self.setCentralWidget(self.tsa_viewer)

        self.block_editor.block_changed_action.observer.attach_observer(
            lambda tsa_data: setattr(self.tsa_viewer, "tsa_data", tsa_data)
        )

        self.color_picker.palette_set_changed_action.observer.attach_observer(lambda p: setattr(self, "palette_set", p))
        self.palette_selector.palette_changed_action.observer.attach_observer(
            lambda p: setattr(self, "palette", p)
        )

        self.tileset_spinner.value_changed_action.observer.attach_observer(
            lambda tileset: setattr(self, "tileset", tileset)
        )

        self.offset_spinner.value_changed_action.observer.attach_observer(
            lambda offset: setattr(self.tsa_viewer, "tsa_data", self.tsa_viewer.tsa_data_from_tsa_offset(offset))
        )

        self.tsa_viewer.single_clicked_action.observer.attach_observer(lambda i: setattr(self.block_editor, "index", i))

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

    @property
    def tileset(self) -> int:
        """The tileset of the current tsa"""
        return self._tileset

    @tileset.setter
    def tileset(self, tileset: int) -> None:
        self._tileset = tileset
        self._pattern_table = PatternTableHandler.from_tileset(tileset)
        if self.tsa_viewer is not None:
            self.tsa_viewer.pattern_table = self.pattern_table

    @property
    def offset(self) -> int:
        """The offset to the bank for the tsa"""
        return self._offset

    @offset.setter
    def offset(self, offset: int) -> None:
        self._offset = offset

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table of the tsa"""
        return self._pattern_table
