"""Edit per-boss overworld lock indexes in the level-settings dialog.

This module owns the level-settings controls for Boom Boom and flying Boom
Boom enemy records that remove an overworld lock when the boss is defeated.
It bridges the in-level enemy records shown by the active ``LevelRef`` to the
close-time undo commands that persist lock-index changes back into the editor.

See Also
--------
foundry.gui.level_settings.level_settings_dialog
    Hosts this mixin alongside the other specialized level-settings editors.
foundry.gui.commands.ChangeLockIndex
    Undo command used when a staged lock-index change is committed.
foundry.game.gfx.objects.in_level.enemy_item
    Defines the enemy records whose lock-index bytes are edited here.
"""

from PySide6.QtWidgets import QComboBox, QGroupBox, QVBoxLayout

from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.gui import label_and_widget
from foundry.gui.commands import ChangeLockIndex
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.localization import tr, tr_object_name
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJ_BOOMBOOM, OBJ_FLYING_BOOMBOOM


class BoomBoomMixin(SettingsMixin):
    """Edit Boom Boom lock-destruction indexes.

    Boom Boom and flying Boom Boom enemy items can encode which overworld lock
    should be removed after the boss is defeated. The mixin exposes each boss in
    the level and stages lock-index edits until the dialog closes.

    Parameters
    ----------
    parent : object
        Parent window that owns the undo stack.

    Attributes
    ----------
    boom_boom_dropdown : QComboBox
        Dropdown listing Boom Boom instances found in the level.
    boom_boom_index_spinner : Spinner
        Spinner editing the selected boss lock index.
    original_lock_indexes : list[int]
        Lock indexes captured when the dialog opened.
    """

    def __init__(self, parent):
        """Create Boom Boom lock-index controls.

        Construction gathers the Boom Boom enemy records from the active level,
        snapshots their original lock indexes for later undo reconstruction,
        creates one dropdown row that selects which boss is being edited, and
        then binds a spinner that stages the selected boss record in place.
        The dialog therefore stays interactive while it is open, but
        ``closeEvent`` remains the commit boundary that turns the net
        difference from ``original_lock_indexes`` into undo commands.

        Parameters
        ----------
        parent : object
            Parent window that owns the undo stack.
        """
        super(BoomBoomMixin, self).__init__(parent)

        boom_boom_group = QGroupBox(
            tr("BoomBoomMixin", "boom_boom_lock_destruction_index", "Boom Boom Lock Destruction Index")
        )
        QVBoxLayout(boom_boom_group)

        boom_booms = _get_boom_booms(self.level_ref.enemies)
        self.original_lock_indexes = [boom_boom.lock_index for boom_boom in boom_booms]

        self.boom_boom_dropdown = QComboBox()
        self.boom_boom_dropdown.addItems(
            [
                tr("BoomBoomMixin", "object_name_at_position", "{object_name} at {position}").format(
                    object_name=tr_object_name(boom_boom),
                    position=boom_boom.get_position(),
                )
                for boom_boom in boom_booms
            ]
        )
        self.boom_boom_dropdown.currentIndexChanged.connect(self._on_boom_boom_dropdown)

        self.boom_boom_index_spinner = Spinner(self, maximum=3)
        self.boom_boom_index_spinner.setEnabled(bool(boom_booms))
        self.boom_boom_index_spinner.valueChanged.connect(self._on_boom_boom_spinner)

        if boom_booms:
            self._on_boom_boom_dropdown(0)

        boom_boom_group.layout().addWidget(self.boom_boom_dropdown)
        boom_boom_group.layout().addLayout(
            label_and_widget(tr("BoomBoomMixin", "lock_index", "Lock index"), self.boom_boom_index_spinner)
        )

        self.layout().addWidget(boom_boom_group)

    def _on_boom_boom_dropdown(self, new_index: int):
        """Load the selected Boom Boom's lock index into the spinner.

        Parameters
        ----------
        new_index : int
            Index of the selected boss in the dropdown.
        """
        boom_boom = _get_boom_booms(self.level_ref.enemies)[new_index]

        self.boom_boom_index_spinner.setValue(boom_boom.lock_index)

    def _on_boom_boom_spinner(self, new_value):
        """Stage a lock-index change on the selected Boom Boom.

        The enemy item is updated immediately for preview consistency; close
        handling turns the net difference into a command.

        Parameters
        ----------
        new_value : int
            Replacement setting value.
        """
        boom_boom = _get_boom_booms(self.level_ref.enemies)[self.boom_boom_dropdown.currentIndex()]

        boom_boom.lock_index = new_value

    def closeEvent(self, event):
        """Commit Boom Boom lock-index changes as undoable commands.

        Each boss is restored to its original lock index before the command is
        pushed, matching the undo stack's expected before/after model.

        Parameters
        ----------
        event : object
            Qt event delivered to the widget.
        """
        super(BoomBoomMixin, self).closeEvent(event)

        boom_booms = _get_boom_booms(self.level_ref.enemies)

        for old_index, boom_boom in zip(self.original_lock_indexes, boom_booms):
            boom_boom.lock_index, new_index = old_index, boom_boom.lock_index

            if boom_boom.lock_index != new_index:
                self.undo_stack.push(
                    ChangeLockIndex(
                        self.level_ref,
                        self.level_ref.enemies.index(boom_boom),
                        new_index,
                    )
                )


def _get_boom_booms(enemy_items: list[EnemyItem]) -> list[EnemyItem]:
    """Collect lock-index-capable Boom Boom enemy items in level order.

    The dropdown and close-time comparison both rely on this stable ordering:
    the opening snapshot stores lock indexes by position in the returned list,
    and close handling zips the current list with that snapshot to build undo
    commands for changed bosses.

    Parameters
    ----------
    enemy_items : list[EnemyItem]
        Enemy and item objects in the level.

    Returns
    -------
    list[EnemyItem]
        Boss objects that can control overworld lock destruction.
    """
    boom_booms = [item for item in enemy_items if item.obj_index in [OBJ_BOOMBOOM, OBJ_FLYING_BOOMBOOM]]

    return boom_booms
