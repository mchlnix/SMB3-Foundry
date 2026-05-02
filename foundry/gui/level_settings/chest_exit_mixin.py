"""Edit treasure-chest exit metadata and reward objects for a level.

This module owns the level-settings controls for SMB3 treasure chest behavior.
Its workflow is: snapshot the chest metadata records when the dialog opens,
stage user choices through the checkbox and reward combobox while the dialog
is open, then convert the net difference back into undo commands when the
dialog closes. That lets the level-settings dialog present special enemy/item
records as ordinary controls without losing the editor's usual undo
boundaries.

See Also
--------
foundry.gui.level_settings.level_settings_dialog
    Hosts this mixin with the rest of the per-level settings editors.
foundry.gui.commands.AddEnemyAt
    Used when staged chest metadata needs a new enemy/item record.
foundry.gui.commands.MoveObject
    Used when an existing chest reward setter changes its encoded item byte.
foundry.gui.commands.RemoveObject
    Used when closing removes a staged chest record.
"""

from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QCheckBox, QComboBox, QGroupBox, QVBoxLayout

from foundry import make_macro
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.world_map.sprite import MAP_ITEM_SPRITES
from foundry.game.level.Level import Level
from foundry.gui import label_and_widget
from foundry.gui.commands import AddEnemyAt, MoveObject, RemoveObject
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.localization import tr, tr_data_name
from smb3parse.constants import (
    MAPITEM_MUSHROOM,
    MAPITEM_MUSICBOX,
    MAPITEM_NAMES,
    OBJ_CHEST_EXIT,
    OBJ_CHEST_ITEM_SETTER,
)


class _ChestState:
    """Capture treasure-chest enemy items before editing.

    Treasure chest behavior is encoded through special enemy/item records: one
    marks that collecting the chest exits the level, and another selects the
    overworld reward item. The state object lets close handling compare the
    initial records with the final widget choices.

    Parameters
    ----------
    level : foundry.game.level.Level.Level
        Level being inspected for chest metadata objects.

    Attributes
    ----------
    chest_exit : EnemyItem | None
        Existing chest-exit marker object.
    chest_item : EnemyItem | None
        Existing chest reward setter object.
    level : foundry.game.level.Level.Level
        Level being inspected for chest metadata objects.
    """

    def __init__(self, level: Level):
        """Read current treasure-chest metadata from a level.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level being inspected for chest metadata objects.
        """
        self.level = level

        self.chest_exit = self._get_chest_exit()
        self.chest_item = self._get_chest_item()

    @property
    def item_index(self):
        """Expose the encoded chest-reward selector byte.

        The reward setter stores the selected overworld item in its
        ``y_position`` field, so the property translates that record into the
        combobox index used by the settings dialog.

        Returns
        -------
        int
            Reward item index, or ``-2`` when no reward setter object exists.
        """
        if self.chest_item:
            return self.chest_item.y_position
        else:
            return -2

    def _get_chest_exit(self) -> EnemyItem | None:
        """Locate the enemy record that makes the chest end the level.

        ``_ChestState`` uses this scan while it snapshots the opening level so
        close handling can later tell whether the user added, removed, or left
        the exit marker unchanged.

        Returns
        -------
        EnemyItem | None
            Chest-exit object, or ``None`` when collecting the chest does not end the level.
        """
        for item in self.level.enemies:
            if item.obj_index == OBJ_CHEST_EXIT:
                return item
        else:
            return None

    def _get_chest_item(self) -> EnemyItem | None:
        """Locate the enemy record that encodes the chest reward item.

        The returned object seeds the reward dropdown and the before/after
        comparison that determines whether close handling needs a move, add, or
        remove command. ``_ChestState`` runs this lookup during its opening
        snapshot, so the method is part of the dialog's larger open-state ->
        staged-widget-state -> close-time-command pipeline rather than a
        stand-alone search helper.

        Returns
        -------
        EnemyItem | None
            Reward setter object, or ``None`` when no overworld item is configured.
        """
        for item in self.level.enemies:
            if item.obj_index == OBJ_CHEST_ITEM_SETTER:
                return item
        else:
            return None


class ChestExitMixin(SettingsMixin):
    """Edit treasure-chest level-ending and reward behavior.

    SMB3 chest behavior is represented by special enemy/item entries rather
    than header bits. The mixin presents those entries as ordinary controls and
    emits undo commands that add, remove, or move the corresponding records.

    Parameters
    ----------
    parent : object
        Parent window that owns the level view and undo stack.

    Attributes
    ----------
    before : _ChestState
        Snapshot of chest metadata when the dialog opened.
    chest_end_checkbox : QCheckBox
        Toggle for adding or removing the chest-exit marker.
    chest_item_dropdown : QComboBox
        Dropdown selecting the overworld reward item.
    """

    def __init__(self, parent):
        """Create treasure-chest controls from the loaded level state.

        The mixin snapshots the existing chest metadata first so close handling
        can express the user's checkbox and reward changes as targeted undo
        commands instead of raw in-place edits.

        Parameters
        ----------
        parent : object
            Parent window that owns the level view and undo stack.
        """
        super(ChestExitMixin, self).__init__(parent)

        self.before = _ChestState(self.level_ref.level)

        chest_group = QGroupBox(tr("ChestExitMixin", "treasure_chest", "Treasure Chest"), self)
        QVBoxLayout(chest_group)

        self.chest_end_checkbox = QCheckBox(
            tr("ChestExitMixin", "getting_chest_ends_level", "Getting Chest ends Level"), self
        )
        self.chest_end_checkbox.setChecked(self.before.chest_exit is not None)

        self.chest_item_dropdown = QComboBox()
        self.chest_item_dropdown.addItem(
            tr("ChestExitMixin", "no_item_hammer_bros_levels", "No Item (Hammer Bros Levels)")
        )

        for item_id in range(MAPITEM_MUSHROOM, MAPITEM_MUSICBOX + 1):
            self.chest_item_dropdown.addItem(
                QPixmap(MAP_ITEM_SPRITES[item_id]),
                tr_data_name("MapItem", MAPITEM_NAMES[item_id]),
            )

        if self.before.chest_item is not None:
            self.chest_item_dropdown.setCurrentIndex(self.before.item_index)
        else:
            self.chest_item_dropdown.setCurrentIndex(0)

        chest_group.layout().addWidget(self.chest_end_checkbox)
        chest_group.layout().addLayout(
            label_and_widget(tr("ChestExitMixin", "item_in_chest", "Item in Chest: "), self.chest_item_dropdown)
        )

        self.layout().addWidget(chest_group)

    @property
    def level(self):
        """Expose the loaded level model used by chest-setting commands.

        The property keeps the mixin code readable while still routing every
        mutation through ``level_ref``, which is the shared editor coordination
        object for selection, updates, and undo workflows.

        Returns
        -------
        Level
            Current level model from ``level_ref``.
        """
        return self.level_ref.level

    def closeEvent(self, event: QMouseEvent):
        """Commit treasure-chest setting changes on close.

        The checkbox and dropdown are compared against the opening snapshot and
        converted into undoable commands.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        self._update_chest_exit_item()
        self._update_chest_reward_item()

        self.level.data_changed.emit()

        super(ChestExitMixin, self).closeEvent(event)

    def _update_chest_reward_item(self):
        """Push undo commands for the selected chest reward item.

        Changing the dropdown either removes the reward setter, moves its
        y-position to the new item index, or adds a new setter object.
        """
        item_index = self.chest_item_dropdown.currentIndex()
        chest_item_name = tr_data_name("MapItem", MAPITEM_NAMES[item_index])

        # not item set
        if item_index == 0:
            if self.before.chest_item is not None:
                self.undo_stack.push(RemoveObject(self.level_ref, self.before.chest_item))

        # item was changed/set
        elif self.before.item_index != item_index:
            self.undo_stack.beginMacro(
                tr("ChestExitMixin", "set_chest_item_to_item_name", "Set Chest Item to '{item_name}'").format(
                    item_name=chest_item_name
                )
            )

            if self.before.chest_item is not None:
                before_move = self.before.chest_item.copy()
                self.before.chest_item.y_position = item_index

                self.undo_stack.push(MoveObject(self.level_ref, before_move, self.before.chest_item))

            else:
                self.undo_stack.push(
                    AddEnemyAt(
                        self._parent.level_view,
                        self._parent.level_view.from_level_point(0, y=item_index),
                        OBJ_CHEST_ITEM_SETTER,
                    )
                )

            self.undo_stack.endMacro()

    def _update_chest_exit_item(self):
        """Push undo commands for the chest-exit marker.

        A checked box adds the special chest-exit object; an unchecked box
        removes the one that existed when the dialog opened.
        """
        if self.chest_end_checkbox.isChecked() and self.before.chest_exit is None:
            # when putting it at x=0, it doesn't work for some reason
            make_macro(
                self.undo_stack,
                tr("ChestExitMixin", "enable_chest_exit", "Enable Chest Exit"),
                AddEnemyAt(
                    self._parent.level_view,
                    self._parent.level_view.from_level_point(1, 0),
                    OBJ_CHEST_EXIT,
                ),
            )

        # was disabled
        elif self.before.chest_exit is not None and not self.chest_end_checkbox.isChecked():
            assert self.before.chest_exit is not None

            make_macro(
                self.undo_stack,
                tr("ChestExitMixin", "disable_chest_exit", "Disable Chest Exit"),
                RemoveObject(self.level_ref, self.before.chest_exit),
            )
