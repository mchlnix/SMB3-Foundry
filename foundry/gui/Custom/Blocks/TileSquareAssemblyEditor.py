

import yaml
from yaml import CLoader as Loader
from typing import List
from PySide2.QtGui import Qt

from foundry import icon, data_dir

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.Action.Action import Action
from foundry.core.geometry.Size.Size import Size

from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET
from foundry.game.gfx.Palette import PaletteSet, Palette
from foundry.gui.QMenus.Menu.MenuFileLight import FileMenuLight
from foundry.gui.QMainWindow.ChildWindow import ChildWindow
from foundry.gui.QToolbar import Toolbar
from foundry.gui.Custom.Palette import PaletteSetEditor
from foundry.gui.Custom.Palette.Selector import PaletteSelector
from foundry.gui.QWidget.Panel import Panel
from foundry.gui.Custom.Block.BlockEditor import BlockEditor
from foundry.gui.QComboBox import ComboBox, ComboBoxOption
from foundry.gui.Custom.Block.Block import Block

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.gui.QCore.Tracker import AbstractActionObject

from .TileSquareAssemblyViewer import TileSquareAssemblyViewer

with open(data_dir.joinpath("tileset_info.yaml")) as f:
    tilesets = yaml.load(f, Loader=Loader)

tileset_offsets = [tileset["C000"] for tileset in tilesets.values()]
tileset_offsets[0] = 12  # correct incorrect world offset


class DialogTileSquareAssemblyEditor(ChildWindow, AbstractActionObject):
    """The viewer of the TSA editor"""

    tsa_data_update_action: Action  # Updates when the tsa offset updates
    palette_set_update_action: Action  # Updates when the palette set updates
    tileset_update_action: Action  # Update when the tileset updates

    def __init__(self, parent):
        ChildWindow.__init__(self, parent, title="Tile Square Assembly Editor")
        AbstractActionObject.__init__(self)

        self.tsa_viewer = None
        self._tileset = 0
        self._pattern_table = PatternTableHandler.from_tileset(self.tileset)
        self._palette_set = DEFAULT_PALETTE_SET
        self._palette_index = 0

        self._set_up_layout()
        self._initialize_internal_observers()

        self.showMaximized()

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__

        self.tileset_update_action.observer.attach_observer(
            lambda *_: setattr(self.tsa_viewer, "pattern_table", self.pattern_table),
            name=f"{name} Update Tileset"
        )
        self.tileset_update_action.observer.attach_observer(
            lambda *_: setattr(self.block_editor, "pattern_table", self.pattern_table),
            name=f"{name} Update Tileset"
        )

        self.tileset_combo_box.index_changed_action.observer.attach_observer(
            lambda tileset: setattr(self, "tileset", tileset),
            name=f"{name} Update Tileset"
        )
        self.tileset_combo_box.index_changed_action.observer.attach_observer(
            lambda offset: setattr(self.tsa_viewer, "tsa_data", self.tsa_viewer.tsa_data_from_tsa_offset(self.offset)),
            name=f"{name} Update TSA Data"
        )
        self.block_editor.block_changed_action.observer.attach_observer(
            lambda tsa_data: setattr(self.tsa_viewer, "tsa_data", tsa_data),
            name=f"{name} Update TSA"
        )
        self.tsa_viewer.single_clicked_action.observer.attach_observer(
            lambda i: setattr(self.block_editor, "index", i),
            name=f"{name} Update Index"
        )

        self.palette_set_update_action.observer.attach_observer(
            lambda palette_set: setattr(self.tsa_viewer, "palette_set", palette_set),
            name=f"{name} Update Palette Set"
        )
        self.palette_set_update_action.observer.attach_observer(
            lambda palette_set: setattr(self.palette_selector, "palette_set", palette_set),
            name=f"{name} Update Palette Set"
        )
        self.palette_set_update_action.observer.attach_observer(
            lambda palette_set: setattr(self.color_picker, "palette_set", palette_set),
            name=f"{name} Update Palette Set"
        )

        self.color_picker.palette_set_changed_action.observer.attach_observer(
            lambda p: setattr(self, "palette_set", p),
            name=f"{name} Update Palette Set"
        )
        self.palette_selector.palette_changed_action.observer.attach_observer(
            lambda p: setattr(self, "palette", p),
            name=f"{name} Update Palette"
        )

    def _set_up_layout(self) -> None:
        self.setWindowIcon(icon("tanooki.ico"))

        # Add a default file menu
        self.file_menu = FileMenuLight(self)
        self.menuBar().addMenu(self.file_menu)

        def push_tileset_closure(index: int):
            """Closure for pushing the tileset"""
            def push_tileset(*_):
                """Pushes the tileset"""
                return index
            return push_tileset

        tileset_options: List[ComboBoxOption] = []
        self.combo_box_actions = []
        for idx, tileset in enumerate(tilesets.values()):
            tileset_option = ObservableDecorator(
                push_tileset_closure(idx), name=f"{self.__class__.__name__} Push Tileset {idx}"
            )
            tileset_options.append(ComboBoxOption(tileset["name"], Action("name", tileset_option)))
            self.combo_box_actions.append(tileset_option)

        self.tileset_combo_box = ComboBox(self, tileset_options)
        self.tileset_toolbar = Toolbar.default_toolbox(
            self, "tileset_toolbar", Panel(self, "Tileset", self.tileset_combo_box), Qt.RightToolBarArea
        )

        self.palette_selector = PaletteSelector(self, self.palette_index, self.palette_set)
        self.palette_selector_toolbar = Toolbar.default_toolbox(
            self, "palette_selector_toolbar", Panel(self, "Palette", self.palette_selector), Qt.RightToolBarArea
        )

        self.color_picker = PaletteSetEditor(self, self.palette_set)
        self.color_picker_toolbox = Toolbar.default_toolbox(
            self, "color_picker_toolbar", self.color_picker, Qt.RightToolBarArea
        )

        self.block_editor = BlockEditor(
            self, Block.from_tsa(Size(3, 3), 0, self.pattern_table, self.palette_set, self.offset)
        )
        self.block_editor_toolbox = Toolbar.default_toolbox(
            self, "block_editor_toolbar", self.block_editor, Qt.RightToolBarArea
        )

        self.tsa_viewer = TileSquareAssemblyViewer.from_tsa(self, self.pattern_table, self.palette_set, self.offset)
        self.setCentralWidget(self.tsa_viewer)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        name = self.__class__.__name__
        return [
            Action("tsa_data_update", ObservableDecorator(
                lambda tsa_offset: tsa_offset, f"{name} TSA Updated"
            )),
            Action("palette_set_update", ObservableDecorator(
                lambda palette_set: palette_set, f"{name} Palette Set Updated"
            )),
            Action("tileset_update", ObservableDecorator(
                lambda pattern_table: pattern_table, f"{name} Tileset Updated"
            )),
        ]

    @property
    def palette_set(self) -> PaletteSet:
        """The palette set used by the editor"""
        return self._palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        if self.palette_set != palette_set:
            self._palette_set = palette_set
            self.palette_set_update_action(palette_set)

    @property
    def palette(self) -> Palette:
        """The palette used by the editor"""
        return self.palette_set[self.palette_index]

    @palette.setter
    def palette(self, palette: Palette) -> None:
        if self.palette_set[self.palette_index] != palette:
            self._palette_set[self.palette_index] = palette
            self.palette_set_update_action(self.palette_set)

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
        if self.tileset != tileset:
            self._tileset = tileset
            self._pattern_table = PatternTableHandler.from_tileset(tileset)
            self.tileset_update_action((self.tileset, self.offset, self.pattern_table))

    @property
    def offset(self) -> int:
        """The offset to the bank for the tsa"""
        return tileset_offsets[self.tileset]

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table of the tsa"""
        return self._pattern_table
