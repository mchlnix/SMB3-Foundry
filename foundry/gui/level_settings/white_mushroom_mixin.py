from warnings import warn

from PySide6.QtWidgets import QCheckBox, QGroupBox, QVBoxLayout

from foundry import make_macro
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.gui import label_and_widget
from foundry.gui.commands import AddObject, MoveObject, RemoveObject
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJ_WHITE_MUSHROOM_HOUSE


class WhiteMushroomHouseMixin(SettingsMixin):
    def __init__(self, parent):
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
        return self.level_ref.level

    def _get_mushroom_item(self) -> EnemyItem | None:
        for enemy_item in self.level.enemies:
            if enemy_item.type == OBJ_WHITE_MUSHROOM_HOUSE:
                return enemy_item
        else:
            return None

    def closeEvent(self, event):
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

            make_macro(self.undo_stack, "Disable White Mushroom House", RemoveObject(self.level, old_mushroom_item))

        # mushroom house added
        elif not self._had_mushroom_item and now_has_mushroom_item:
            new_mushroom_item = self.level.enemy_item_factory.from_properties(
                OBJ_WHITE_MUSHROOM_HOUSE, 1, new_coins_required
            )

            make_macro(self.undo_stack, "Enable White Mushroom House", AddObject(self.level, new_mushroom_item))

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
                MoveObject(self.level, old_mushroom_item, new_mushroom_item),
            )

        else:
            warn("White Mushroom House Change was not covered")

        super().closeEvent(event)
