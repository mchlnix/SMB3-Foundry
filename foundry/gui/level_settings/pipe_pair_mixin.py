"""Edit world-map pipe-pair exits from the level-settings dialog.

This module owns the controls for SMB3 pipe exits that jump from a level back
to two configurable world-map destinations. It coordinates the temporary pipe
enemy record that lives inside the level with the ROM-backed ``PipeData``
table entries that store the actual world-map destinations.

See Also
--------
foundry.gui.level_settings.level_settings_dialog
    Hosts this mixin alongside the other level-settings editors.
foundry.gui.commands.UpdatePipeData
    Undo command used when staged pipe-table edits are committed.
foundry.gui.dialogs.level_selector.LevelSelector
    Supplies the world-map selector widget reused for choosing destinations.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
)

from foundry import icon, make_macro
from foundry.game.File import ROM
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.gui import label_and_widget
from foundry.gui.commands import AddEnemyAt, RemoveObject, UpdatePipeData
from foundry.gui.dialogs.level_selector.LevelSelector import WorldMapLevelSelect
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJ_PIPE_EXITS, PIPE_PAIR_COUNT
from smb3parse.data_points import Position
from smb3parse.data_points.pipe_data import PipeData
from smb3parse.levels import WORLD_COUNT


class PipePairMixin(SettingsMixin):
    """Edit the world-map destinations used by pipe-pair exits.

    SMB3 represents world-map pipe exits as a special enemy/item object in the
    level plus a ROM pipe-data table entry. The controls here stage both pieces:
    the enemy item's y-position selects the pipe-pair index and orientation,
    while ``PipeData`` stores the two world-map destinations.

    Parameters
    ----------
    parent : object
        Parent window that owns the level view and undo stack.

    Attributes
    ----------
    left_pos_label : QLabel
        Label displaying the first pipe destination.
    original_pipe_item : EnemyItem | None
        Pipe-exit object present when the dialog opened.
    original_pipe_y_value : int
        Original encoded pipe index and orientation byte.
    pipe_data_changed : bool
        Whether pipe table data was edited and needs an undo command.
    pipe_datas : list[PipeData]
        ROM pipe-pair table entries available to this dialog.
    pipe_pair_check_box : QCheckBox
        Toggle for adding or removing the special pipe-exit object.
    pipe_pair_spinner : Spinner
        Selector for the pipe-pair table index.
    right_pos_label : QLabel
        Label displaying the second pipe destination.
    set_new_button : QPushButton
        Button that opens world-map destination pickers.
    sky_tower_check_box : QCheckBox
        Toggle for the high-bit orientation used by Sky Tower-style exits.

    Notes
    -----
    The dialog edits pipe-pair state in two layers while it is open: a
    temporary in-level pipe-exit object keeps the UI interactive, and close-time
    handling folds the net result into the appropriate undo commands and pipe
    table updates.

    See Also
    --------
    PipeExitSetScreen
        World-map picker used for selecting pipe destinations.
    UpdatePipeData
        Undo command used when pipe table data is committed.
    """

    def __init__(self, parent):
        """Create pipe-pair controls from the loaded level state.

        Construction runs in five stages. It first loads the ROM pipe table and
        snapshots the original in-level pipe object plus its encoded y byte.
        It then builds the enable/orientation/index controls that stage edits
        on that temporary pipe object, creates the destination labels and
        picker button that operate on the active ``PipeData`` slot, refreshes
        those labels from the staged state, and finally attaches the whole
        group to the shared level-settings layout. That order matters because
        destination picking, label refreshes, and close-time undo generation
        all depend on the constructor having already established both layers of
        state: the temporary in-level object and the ROM-backed pipe table
        entry it selects. After construction, every user action follows the
        same staged route: the checkbox adds or removes the temporary pipe
        object, the spinner rewrites that object's encoded y byte, destination
        picking rewrites the selected ``PipeData`` entry, label refreshes mirror
        both layers back into the UI, and ``closeEvent`` later turns the net
        result into undo commands. The constructor is what wires those phases
        together, so later handlers can assume the temporary object, pipe-data
        table, labels, and buttons are already synchronized around one active
        pipe-pair slot.

        Parameters
        ----------
        parent : object
            Parent window that owns the level view and undo stack.
        """
        super(PipePairMixin, self).__init__(parent)

        pipe_pair_group = QGroupBox("Pipe Pair Exits")
        QVBoxLayout(pipe_pair_group)

        self.pipe_datas = [PipeData(ROM(), index) for index in range(PIPE_PAIR_COUNT)]
        self.pipe_data_changed = False

        self.original_pipe_item = _get_pipe_item(self.level_ref.enemies)
        if self.original_pipe_item is None:
            self.original_pipe_y_value = -1
        else:
            self.original_pipe_y_value = self.original_pipe_item.y_position

        self.pipe_pair_check_box = QCheckBox("Enable exiting somewhere else on WorldMap")
        self.pipe_pair_check_box.setChecked(self.original_pipe_item is not None)
        self.pipe_pair_check_box.clicked.connect(self._on_pipe_check_box)
        pipe_pair_group.layout().addWidget(self.pipe_pair_check_box)

        self.sky_tower_check_box = QCheckBox("Like Sky Tower (Top and Bottom, instead of Left and Right)")
        self.sky_tower_check_box.clicked.connect(self._on_update_y_position)
        pipe_pair_group.layout().addWidget(self.sky_tower_check_box)

        self.pipe_pair_spinner = Spinner(self, maximum=PIPE_PAIR_COUNT - 1)
        self.pipe_pair_spinner.valueChanged.connect(self._on_update_y_position)
        pipe_pair_group.layout().addLayout(label_and_widget("Pipe Pair Index", self.pipe_pair_spinner))

        self.left_pos_label = QLabel("-")
        pipe_pair_group.layout().addLayout(label_and_widget("Left Exit", self.left_pos_label))

        self.right_pos_label = QLabel("-")
        pipe_pair_group.layout().addLayout(label_and_widget("Right Exit", self.right_pos_label))

        self.set_new_button = QPushButton("Change Exit Locations")
        self.set_new_button.clicked.connect(self._on_set_pipe_exits)
        pipe_pair_group.layout().addWidget(self.set_new_button)

        self._update_position_labels()

        self.layout().addWidget(pipe_pair_group)

    def _on_pipe_check_box(self, checked):
        """Add or remove the temporary pipe-exit object.

        The undo command is not pushed immediately. The dialog keeps the model
        interactive while open and commits the net change in ``closeEvent``.

        Parameters
        ----------
        checked : bool
            Whether pipe-pair exits should be enabled.
        """
        if checked:
            self.level_ref.level.add_enemy(OBJ_PIPE_EXITS, Position.from_xy(0, 0))
        else:
            self.level_ref.level.remove_object(_get_pipe_item(self.level_ref.enemies))

        self._update_position_labels()

    def _on_set_pipe_exits(self):
        """Prompt for both world-map pipe destinations.

        The selected positions update the selected ``PipeData`` entry
        and mark the pipe table dirty for close-time undo handling. The dialog
        gathers the first exit, seeds the second picker with the chosen world,
        and keeps the temporary pipe object as the source of the active pipe
        table index.
        """
        QMessageBox.information(
            self,
            "Select Pipe Pair Exit",
            "On the next screen, choose where the Left/Top Exit should lead to.",
        )
        left_pair_screen = PipeExitSetScreen(self)
        left_pair_screen.current_world = self.level_ref.level.world
        left_pair_screen.exec()

        QMessageBox.information(
            self,
            "Select Pipe Pair Exit",
            "On the next screen, choose where the Right/Bottom Exit should lead to.",
        )
        right_pair_screen = PipeExitSetScreen(self)
        right_pair_screen.current_world = left_pair_screen.current_world
        right_pair_screen.exec()

        pipe_item = _get_pipe_item(self.level_ref.enemies)
        assert pipe_item is not None

        pipe_data = self.pipe_datas[pipe_item.y_position % 0x80]

        pipe_data.left_pos = left_pair_screen.selected_position
        pipe_data.right_pos = right_pair_screen.selected_position
        self.pipe_data_changed = True

        self._update_position_labels()

    def _on_update_y_position(self):
        """Update the pipe-exit object's encoded y-position byte.

        The low seven bits select the pipe-pair index. The high bit switches
        between left/right and top/bottom orientation.
        """
        pipe_item = _get_pipe_item(self.level_ref.enemies)

        if pipe_item is not None:
            new_value = self.pipe_pair_spinner.value()

            if self.sky_tower_check_box.isChecked():
                new_value += 0x80

            pipe_item.y_position = new_value

        self._update_position_labels()

    def _update_position_labels(self):
        """Synchronize pipe controls and destination labels from the model.

        Disabled controls show a neutral ``-`` state when no pipe-exit object is
        present. Enabled controls display the selected ROM pipe-data entry.
        """
        pipe_item = _get_pipe_item(self.level_ref.enemies)

        self.sky_tower_check_box.setEnabled(pipe_item is not None)
        self.sky_tower_check_box.setChecked(pipe_item is not None and pipe_item.y_position & 0x80 == 0x80)
        self.pipe_pair_spinner.setEnabled(pipe_item is not None)
        self.set_new_button.setEnabled(pipe_item is not None)

        if pipe_item is None:
            self.left_pos_label.setText("-")
            self.right_pos_label.setText("-")

            self.pipe_pair_spinner.setValue(0)
        else:
            self.pipe_pair_spinner.setValue(pipe_item.y_position % 0x80)

            pipe_data = self.pipe_datas[pipe_item.y_position % 0x80]

            self.left_pos_label.setText(
                f"Screen: {pipe_data.screen_left}, x: {pipe_data.x_left}, y: {pipe_data.y_left}"
            )
            self.right_pos_label.setText(
                f"Screen: {pipe_data.screen_right}, x: {pipe_data.x_right}, y: {pipe_data.y_right}"
            )

        self.level_ref.data_changed.emit()

    def closeEvent(self, event):
        """Commit staged pipe-pair changes as undoable commands.

        During editing, the level may contain temporary pipe objects. Closing
        restores the original model state and pushes commands that reproduce the
        user's final choice through the normal undo stack.

        Parameters
        ----------
        event : object
            Qt event delivered to the widget.
        """
        super(PipePairMixin, self).closeEvent(event)

        current_pipe_item = _get_pipe_item(self.level_ref.enemies)

        pipe_kept_disabled = self.original_pipe_item is current_pipe_item is None
        pipe_was_disabled = self.original_pipe_item is not None and current_pipe_item is None
        pipe_was_enabled = self.original_pipe_item is None and current_pipe_item is not None

        if pipe_kept_disabled:
            pass
        elif pipe_was_disabled:
            assert self.original_pipe_item

            self.level_ref.level.enemies.insert(0, self.original_pipe_item)

            make_macro(
                self.undo_stack, "Disable Pipe Pair Exits", RemoveObject(self.level_ref, self.original_pipe_item)
            )

        elif pipe_was_enabled:
            assert current_pipe_item is not None

            self.level_ref.level.remove_object(current_pipe_item)

            level_view = self._parent.level_view

            command = AddEnemyAt(
                level_view, level_view.from_level_point(0, current_pipe_item.y_position), OBJ_PIPE_EXITS
            )
            command.setText("Enable Pipe Pair Exits")

            self.undo_stack.push(command)

        else:
            assert self.original_pipe_item is not None

            if current_pipe_item is self.original_pipe_item:
                current_pipe_item = self.original_pipe_item.copy()
            else:
                self.level_ref.level.remove_object(current_pipe_item)
                self.level_ref.level.enemies.append(self.original_pipe_item)

            assert current_pipe_item is not None

            if self.original_pipe_y_value != current_pipe_item.y_position:
                assert self.original_pipe_item is not current_pipe_item

                self.original_pipe_item.y_position = self.original_pipe_y_value

                level_view = self._parent.level_view
                make_macro(
                    self.undo_stack,
                    f"Pipe Pair Exits Index to {current_pipe_item.y_position:#x}",
                    RemoveObject(self.level_ref, self.original_pipe_item),
                    AddEnemyAt(
                        level_view, level_view.from_level_point(0, current_pipe_item.y_position), OBJ_PIPE_EXITS
                    ),
                )

        if self.pipe_data_changed:
            self.undo_stack.push(UpdatePipeData(self.pipe_datas))


class PipeExitSetScreen(QDialog):
    """Let the user choose a world-map tile for a pipe destination.

    Each tab embeds a world-map selector. Clicking a map tile records the
    selected position and accepts the dialog.

    Parameters
    ----------
    parent : object
        Parent settings dialog.

    Attributes
    ----------
    selected_position : Position
        World-map position chosen by the user.
    world_tabs : QTabWidget
        Tabs containing per-world map selectors.
    """

    def __init__(self, parent):
        """Build the per-world destination picker tabs.


        Parameters
        ----------
        parent : object
            Parent settings dialog.
        """
        super(PipeExitSetScreen, self).__init__(parent)

        self.selected_position = Position.from_xy(0, 0)

        self.world_tabs = QTabWidget()

        for world_number in range(WORLD_COUNT - 1):
            world_number += 1

            world_map_select = WorldMapLevelSelect(world_number)
            world_map_select.ignore_levels = True
            world_map_select.map_position_clicked.connect(self._set_position)
            world_map_select.map_position_clicked.connect(self.accept)

            self.world_tabs.addTab(world_map_select, f"World {world_number}")
            self.world_tabs.setTabIcon(world_number, icon("globe.svg"))

        self.setLayout(QVBoxLayout())

        self.layout().addWidget(self.world_tabs)

    @property
    def current_world(self):
        """Expose the one-based world number for the active destination tab.

        The pipe-exit picker uses this property to keep the second destination
        dialog on the same world that was chosen for the first destination, so
        callers can carry staged selection context forward between the two map
        picks. It is therefore part of the picker-to-picker workflow for
        building one coherent pipe pair, not just a convenience wrapper around
        the tab index. Reading it affects the next picker dialog because that
        returned world number is fed directly into the second chooser's tab
        selection before the user picks the matching destination.

        Returns
        -------
        int
            One-based world number for the active tab.
        """
        return self.world_tabs.currentIndex() + 1

    @current_world.setter
    def current_world(self, value):
        """Select a world tab by one-based world number.

        Parameters
        ----------
        value : int
            One-based world number to display.
        """
        if value not in range(1, WORLD_COUNT + 1):
            return

        self.world_tabs.setCurrentIndex(value - 1)

    def _set_position(self, pos: Position):
        """Store the clicked world-map position.

        Parameters
        ----------
        pos : Position
            World-map tile position selected by the user.
        """
        self.selected_position = pos.copy()


def _get_pipe_item(enemy_items: list[EnemyItem]) -> EnemyItem | None:
    """Return the level's pipe-pair enemy item.

    Parameters
    ----------
    enemy_items : list[EnemyItem]
        Enemy and item objects in the level.

    Returns
    -------
    EnemyItem | None
        Pipe-pair object, or ``None`` when the level has no pipe-pair exits.
    """
    for item in enemy_items:
        if item.obj_index == OBJ_PIPE_EXITS:
            return item
    else:
        return None
