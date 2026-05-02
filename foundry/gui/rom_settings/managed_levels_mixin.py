"""ROM-settings mixins for managed-level compaction controls.

This module hosts the mixin that exposes Foundry's managed-level-position
workflow inside the ROM settings dialog. It is the UI bridge between
``LevelOrganizer`` and the ROM-scoped controls that let users inspect and
trigger level compaction.

See Also
--------
foundry.game.additional_data.LevelOrganizer
    Performs the ROM rewrite and metadata update work described by this mixin.
foundry.gui.rom_settings.rom_settings_dialog
    Hosts the mixin inside the ROM-scoped settings dialog.
"""

from collections import defaultdict

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout

from foundry.game.additional_data import LevelOrganizer
from foundry.game.File import ROM
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.dialogs.LevelParseProgressDialog import LevelParseProgressDialog
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.localization import tr_data_name, tr
from foundry.gui.widgets.HorizontalLine import HorizontalLine
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJECT_SET_NAMES, Constants
from smb3parse.util.rom import PRG_BANK_SIZE

TR_KEY_CONTEXT = "foundry.managed_levels"


class ManagedLevelsMixin(SettingsMixin):
    """Add managed-level-position controls to the ROM settings dialog.

    This mixin exposes Foundry's automatic level-management feature: it lets
    users enable managed level positions, inspect the per-bank level ranges
    that will be compacted, and trigger a rearrangement pass that rewrites ROM
    addresses through ``LevelOrganizer``.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this object.

    Attributes
    ----------
    enabled_checkbox : QCheckBox
        Toggle controlling whether automatic level management is enabled.
    level_info_box : QGroupBox
        Container showing the per-bank level data ranges.
    level_info_box_initialized : bool
        Whether the range UI has already been built.
    level_ref : LevelRef
        Reference to the loaded level.
    needs_gui_update : SignalInstance
        Signal emitted when the surrounding dialog or main window should refresh.

    Notes
    -----
    The mixin is the UI counterpart to ``LevelOrganizer``. It lets the ROM
    settings surface present managed-level compaction as a reversible editor
    workflow instead of a hidden ROM rewrite step. The data flow is checkbox
    and spinner state -> ``AdditionalData`` and ``LevelOrganizer`` updates ->
    ROM rewrite -> GUI refresh.
    """

    needs_gui_update: SignalInstance
    level_ref: LevelRef

    def __init__(self, parent):
        """Build the managed-level controls inside the ROM settings dialog.

        Construction wires the enable toggle, creates the per-bank summary box,
        and immediately derives the initial managed-level state from ROM data.

        Parameters
        ----------
        parent : QWidget
            Parent Qt widget that owns this object.
        """
        super().__init__(parent)

        managed_level_positions_box = QGroupBox(tr(TR_KEY_CONTEXT, "group.title"))
        QVBoxLayout(managed_level_positions_box)

        self.enabled_checkbox = QCheckBox(tr(TR_KEY_CONTEXT, "checkbox.enable"))
        self.enabled_checkbox.setChecked(bool(ROM.additional_data.managed_level_positions))

        self.enabled_checkbox.toggled.connect(self.update_level_info)

        managed_level_positions_box.layout().addWidget(self.enabled_checkbox)

        self.layout().addWidget(managed_level_positions_box)

        self.level_info_box = QGroupBox(tr(TR_KEY_CONTEXT, "group.level_range"))
        QVBoxLayout(self.level_info_box)
        self.layout().addWidget(self.level_info_box)

        self.level_info_box.hide()
        self.level_info_box_initialized = False

        self.update_level_info()

    def update_level_info(self):
        """Refresh or build the managed-level bank summary UI.

        This method is the main bridge between the checkbox state, parsed level
        discovery, and the bank ranges shown to the user.
        """
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
        prg_banks_by_object_set = ROM().read(Constants.OFFSET_BY_OBJECT_SET_A000, 16)

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
                        tr(TR_KEY_CONTEXT, "bank.title").format(
                            prg_index=prg_index,
                            object_sets=", ".join(
                                tr_data_name("ObjectSet", OBJECT_SET_NAMES[index]) for index in object_set_indexes
                            ),
                        )
                    )
                )

                level_start_spinner = Spinner(None, maximum=prg_end - 1)
                level_start_spinner.setMinimum(prg_start)
                level_start_spinner.setValue(level_start)

                level_start_layout = QHBoxLayout()
                level_start_layout.addWidget(QLabel(tr(TR_KEY_CONTEXT, "level_range.label")))
                level_start_layout.addWidget(level_start_spinner)
                level_start_layout.addWidget(QLabel(tr(TR_KEY_CONTEXT, "level_range.end").format(prg_end=prg_end - 1)))

                self.level_info_box.layout().addLayout(level_start_layout)
                self.level_info_box.layout().addWidget(HorizontalLine())

            self.level_info_box_initialized = True
            self.on_rearrange()

        self.needs_gui_update.emit()

    @property
    def level(self) -> Level | None:
        """Loaded level currently coordinated by the dialog.

        Rearrangement needs access to the active level so it can update any
        open level addresses after ROM compaction.

        Returns
        -------
        Level | None
            Active level from ``level_ref``, or ``None``.
        """
        if self.level_ref is not None:
            return self.level_ref.level
        else:
            return None

    def on_rearrange(self):
        """Repack managed levels in ROM and refresh the open level state."""
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
        """Discard cached found levels when management is disabled on close.

        Parameters
        ----------
        event : QCloseEvent
            Qt event delivered to the widget.
        """
        super().closeEvent(event)

        if not self.enabled_checkbox.isChecked():
            ROM.additional_data.found_levels.clear()
