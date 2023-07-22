from PySide6.QtWidgets import QComboBox, QGroupBox, QVBoxLayout

from foundry.game.gfx.objects import EnemyItem
from foundry.gui import label_and_widget
from foundry.gui.commands import ChangeLockIndex
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJ_BOOMBOOM, OBJ_FLYING_BOOMBOOM


class BoomBoomMixin(SettingsMixin):
    def __init__(self, parent):
        super(BoomBoomMixin, self).__init__(parent)

        boom_boom_group = QGroupBox("Boom Boom Lock Destruction Index")
        QVBoxLayout(boom_boom_group)

        boom_booms = _get_boom_booms(self.level_ref.enemies)
        self.original_lock_indexes = [boom_boom.lock_index for boom_boom in boom_booms]

        self.boom_boom_dropdown = QComboBox()
        self.boom_boom_dropdown.addItems(
            [f"{boom_boom.name} at {boom_boom.get_position()}" for boom_boom in boom_booms]
        )
        self.boom_boom_dropdown.currentIndexChanged.connect(self._on_boom_boom_dropdown)

        self.boom_boom_index_spinner = Spinner(self, maximum=3)
        self.boom_boom_index_spinner.setEnabled(bool(boom_booms))
        self.boom_boom_index_spinner.valueChanged.connect(self._on_boom_boom_spinner)

        if boom_booms:
            self._on_boom_boom_dropdown(0)

        boom_boom_group.layout().addWidget(self.boom_boom_dropdown)
        boom_boom_group.layout().addLayout(label_and_widget("Lock index", self.boom_boom_index_spinner))

        self.layout().addWidget(boom_boom_group)

    def _on_boom_boom_dropdown(self, new_index: int):
        boom_boom = _get_boom_booms(self.level_ref.enemies)[new_index]

        self.boom_boom_index_spinner.setValue(boom_boom.lock_index)

    def _on_boom_boom_spinner(self, new_value):
        boom_boom = _get_boom_booms(self.level_ref.enemies)[self.boom_boom_dropdown.currentIndex()]

        boom_boom.lock_index = new_value

    def closeEvent(self, event):
        super(BoomBoomMixin, self).closeEvent(event)

        boom_booms = _get_boom_booms(self.level_ref.enemies)

        for old_index, boom_boom in zip(self.original_lock_indexes, boom_booms):
            boom_boom.lock_index, new_index = old_index, boom_boom.lock_index

            if boom_boom.lock_index != new_index:
                self.undo_stack.push(ChangeLockIndex(boom_boom, new_index))


def _get_boom_booms(enemy_items: list[EnemyItem]) -> list[EnemyItem]:
    boom_booms = [item for item in enemy_items if item.obj_index in [OBJ_BOOMBOOM, OBJ_FLYING_BOOMBOOM]]

    return boom_booms
