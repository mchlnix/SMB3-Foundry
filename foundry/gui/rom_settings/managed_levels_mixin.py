from collections import defaultdict

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout

from foundry.game.additional_data import LevelOrganizer
from foundry.game.File import ROM
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.dialogs.LevelParseProgressDialog import LevelParseProgressDialog
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.widgets.HorizontalLine import HorizontalLine
from foundry.gui.widgets.Spinner import Spinner
from smb3parse import PAGE_A000_ByTileset
from smb3parse.objects.object_set import OBJECT_SET_NAMES
from smb3parse.util.rom import PRG_BANK_SIZE


class ManagedLevelsMixin(SettingsMixin):
    needs_gui_update: SignalInstance
    level_ref: LevelRef

    def __init__(self, parent):
        super().__init__(parent)

        boom_boom_group = QGroupBox("Managed Level Positions")
        QVBoxLayout(boom_boom_group)

        self.enabled_checkbox = QCheckBox("Enable Managed Level Positions")
        self.enabled_checkbox.setChecked(bool(ROM.additional_data.managed_level_positions))

        self.enabled_checkbox.toggled.connect(self.update_level_info)

        boom_boom_group.layout().addWidget(self.enabled_checkbox)

        self.layout().addWidget(boom_boom_group)

        self.level_info_box = QGroupBox("Level Range in Rom Banks")
        QVBoxLayout(self.level_info_box)
        self.layout().addWidget(self.level_info_box)

        self.level_info_box.hide()
        self.level_info_box_initialized = False

        self.update_level_info()

    def update_level_info(self):
        was_enabled = ROM.additional_data.managed_level_positions

        ROM.additional_data.managed_level_positions = self.enabled_checkbox.isChecked()

        self.level_info_box.setEnabled(self.enabled_checkbox.isChecked())
        if not self.enabled_checkbox.isChecked():
            self.needs_gui_update.emit()
            return
        else:
            self.level_info_box.show()

        if self.level_info_box_initialized:
            self.needs_gui_update.emit()
            return

        if was_enabled:
            levels_per_object_set: dict[int, set[int]] = defaultdict(set)

            for found_level in ROM.additional_data.found_levels:  # noqa
                levels_per_object_set[found_level.object_set_number].add(found_level.level_offset)

        else:
            pd = LevelParseProgressDialog()

            if pd.wasCanceled():
                self.enabled_checkbox.setChecked(False)
                return

            levels_per_object_set = pd.levels_per_object_set

            ROM.additional_data.found_levels = [
                pd.levels_by_address[key] for key in sorted(pd.levels_by_address.keys())
            ]

        # get prg numbers for object sets and sort them
        prg_banks_by_object_set = ROM().read(PAGE_A000_ByTileset, 16)

        object_set_by_prg_banks = defaultdict(list)

        for object_set_index, prg_index in enumerate(prg_banks_by_object_set):
            object_set_by_prg_banks[prg_index].append(object_set_index)

        if not self.level_info_box_initialized:
            for prg_index, object_set_indexes in sorted(object_set_by_prg_banks.items()):
                prg_start = prg_index * PRG_BANK_SIZE
                if any(not levels_per_object_set[object_set] for object_set in object_set_indexes):
                    level_start = prg_start
                else:
                    level_start = min(list(levels_per_object_set[object_set])[0] for object_set in object_set_indexes)

                prg_end = (prg_index + 1) * PRG_BANK_SIZE

                self.level_info_box.layout().addWidget(
                    QLabel(
                        f"PRG Bank #{prg_index}, {', '.join([OBJECT_SET_NAMES[index] for index in object_set_indexes])}"
                    )
                )

                level_start_spinner = Spinner(None, maximum=prg_end - 1)
                level_start_spinner.setMinimum(prg_start)
                level_start_spinner.setValue(level_start)

                level_start_layout = QHBoxLayout()
                level_start_layout.addWidget(QLabel("Level data range:"))
                level_start_layout.addWidget(level_start_spinner)
                level_start_layout.addWidget(QLabel(f" to 0x{prg_end - 1:x}"))

                self.level_info_box.layout().addLayout(level_start_layout)
                self.level_info_box.layout().addWidget(HorizontalLine())

            self.level_info_box_initialized = True
            self.on_rearrange()

        self.needs_gui_update.emit()

    @property
    def level(self) -> Level | None:
        if self.level_ref is not None:
            return self.level_ref.level
        else:
            return None

    def on_rearrange(self):
        lo = LevelOrganizer(ROM(), ROM().additional_data.found_levels)
        lo.rearrange_levels()
        lo.rearrange_enemies()

        ROM.save_to_file(ROM.path)

        if self.level and self.level.attached_to_rom:
            new_level_address = lo.old_level_address_to_new[self.level.header_offset]
            new_enemy_address = lo.old_enemy_address_to_new[self.level.enemy_offset]

            new_jump_level_address = lo.old_level_address_to_new[self.level.header.jump_level_address]
            new_jump_enemy_address = lo.old_enemy_address_to_new[self.level.header.jump_enemy_address]

            print(f"Level      {self.level.layout_address:x} -> {new_level_address:x}")
            print(f"Enemy      {self.level.enemy_offset:x} -> {new_enemy_address:x}")

            self.level.set_addresses(new_level_address, new_enemy_address)

            print(f"Jump Level {self.level.header.jump_level_address:x} -> {new_jump_level_address:x}")
            print(f"Jump Enemy {self.level.header.jump_enemy_address:x} -> {new_jump_enemy_address:x}")

            self.level.next_area_objects = new_jump_level_address
            self.level.next_area_enemies = new_jump_enemy_address

        self.needs_gui_update.emit()

    def closeEvent(self, event):
        super().closeEvent(event)

        if not self.enabled_checkbox.isChecked():
            ROM.additional_data.found_levels.clear()
