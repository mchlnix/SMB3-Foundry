"""Configure the white mushroom house reward marker for a level.

This mixin translates SMB3's encoded white mushroom house marker into dialog
controls that level editors can reason about directly. It reads the reward
marker from the enemy list, exposes the enable state and coin threshold as Qt
controls, and turns the final dialog diff into undoable add, remove, or move
commands when the settings window closes.

See Also
--------
foundry.gui.level_settings.settings_mixin.SettingsMixin
    Base dialog mixin that supplies shared level and undo-stack access.
foundry.gui.commands
    Undoable commands used to add, remove, or retarget the marker object.
foundry.game.gfx.objects.in_level.enemy_item.EnemyItem
    Enemy-item model that stores the reward marker and encoded threshold.
"""

from warnings import warn

from PySide6.QtWidgets import QCheckBox, QGroupBox, QVBoxLayout

from foundry import make_macro
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.gui import label_and_widget
from foundry.gui.commands import AddEnemyAt, MoveObject, RemoveObject
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJ_WHITE_MUSHROOM_HOUSE


class WhiteMushroomHouseMixin(SettingsMixin):
    """Edit the white mushroom house spawn condition.

    SMB3 encodes the white mushroom house reward as a special enemy/item object
    whose y-position stores the coin threshold. The mixin presents that as a
    checkbox plus numeric threshold and commits the net change on close.

    Parameters
    ----------
    parent : object
        Parent window that owns the level view and undo stack.

    Attributes
    ----------
    _coins_required_spinner : Spinner
        Spinner for the coin threshold byte.
    _had_mushroom_item : bool
        Whether the level had a mushroom-house object when the dialog opened.
    _mushroom_checkbox : QCheckBox
        Toggle for enabling the white mushroom house reward.
    _old_coins_required : int
        Coin threshold captured when the dialog opened.
    """

    def __init__(self, parent):
        """Build the reward controls from the level's opening marker state.

        The dialog snapshots whether a white mushroom house marker already
        exists and, when present, captures its encoded coin threshold from the
        marker's ``y_position``. That opening state drives the checkbox,
        spinner enablement, and later close-event comparison that decides
        whether the editor must add, remove, or move the marker through the
        undo stack.

        Parameters
        ----------
        parent : object
            Parent window that owns the level view and undo stack.
        """
        super().__init__(parent)

        self._had_mushroom_item = False
        self._old_coins_required = -1

        if (mushroom_item := self._get_mushroom_item()) is not None:
            self._had_mushroom_item = True
            self._old_coins_required = mushroom_item.y_position

        mushroom_group = QGroupBox("White Mushroom House", self)
        QVBoxLayout(mushroom_group)

        self._mushroom_checkbox = QCheckBox("Spawn White Mushroom House on Overworld", self)
        self._mushroom_checkbox.setChecked(self._had_mushroom_item)

        self._coins_required_spinner = Spinner(maximum=2**8 - 1, base=10)
        self._coins_required_spinner.setEnabled(self._had_mushroom_item)

        self._mushroom_checkbox.toggled.connect(self._coins_required_spinner.setEnabled)

        if self._coins_required_spinner.isEnabled():
            self._coins_required_spinner.setValue(self._old_coins_required)

        mushroom_group.layout().addWidget(self._mushroom_checkbox)
        mushroom_group.layout().addLayout(label_and_widget("Coins required to spawn:", self._coins_required_spinner))

        self.layout().addWidget(mushroom_group)

    @property
    def level(self):
        """Expose the level model that backs the settings widgets.

        The mixin resolves the active level through ``level_ref`` so helper
        methods can inspect and mutate the same model that undo commands and
        the parent settings dialog already coordinate.

        Returns
        -------
        Level
            Current level model from ``level_ref``.
        """
        return self.level_ref.level

    def _get_mushroom_item(self) -> EnemyItem | None:
        """Locate the encoded reward marker inside the level enemy list.

        SMB3 stores the white mushroom house configuration as a special
        enemy-item entry. This helper feeds both setup and commit paths: the
        constructor uses it to seed the checkbox and spinner from the opening
        level state, and ``closeEvent`` uses the same lookup to resolve the
        marker instance that undo commands will remove or retarget.

        Returns
        -------
        EnemyItem | None
            Marker object, or ``None`` when no white mushroom house is configured.
        """
        for enemy_item in self.level.enemies:
            if enemy_item.type == OBJ_WHITE_MUSHROOM_HOUSE:
                return enemy_item
        else:
            return None

    def closeEvent(self, event):
        """Commit white mushroom house edits on close.

        The close handler compares the checkbox and threshold against the
        opening state and pushes add, remove, or move commands as needed.

        Parameters
        ----------
        event : object
            Qt event delivered to the widget.
        """
        new_coins_required = self._coins_required_spinner.value()

        now_has_mushroom_item = self._mushroom_checkbox.isChecked()

        if not now_has_mushroom_item:
            new_coins_required = -1

        # nothing changed
        if self._had_mushroom_item == now_has_mushroom_item and self._old_coins_required == new_coins_required:
            pass

        # mushroom house removed
        elif self._had_mushroom_item and not now_has_mushroom_item:
            old_mushroom_item = self._get_mushroom_item()
            assert old_mushroom_item is not None

            make_macro(self.undo_stack, "Disable White Mushroom House", RemoveObject(self.level_ref, old_mushroom_item))

        # mushroom house added
        elif not self._had_mushroom_item and now_has_mushroom_item:
            level_view = self._parent.level_view

            make_macro(
                self.undo_stack,
                "Enable White Mushroom House",
                # x must be uneven
                AddEnemyAt(level_view, level_view.from_level_point(1, y=new_coins_required), OBJ_WHITE_MUSHROOM_HOUSE),
            )

        # coins requirement has changed
        elif self._old_coins_required != new_coins_required:
            old_mushroom_item = self._get_mushroom_item()
            assert old_mushroom_item is not None

            # keep copy of old state for undo command
            old_mushroom_item, new_mushroom_item = old_mushroom_item.copy(), old_mushroom_item
            new_mushroom_item.y_position = new_coins_required

            assert old_mushroom_item is not None

            make_macro(
                self.undo_stack,
                f"Set White Mushroom House Coin Limit to {new_coins_required}",
                MoveObject(self.level_ref, old_mushroom_item, new_mushroom_item),
            )

        else:
            warn("White Mushroom House Change was not covered")

        super().closeEvent(event)
