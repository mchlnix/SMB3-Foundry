from PySide6.QtWidgets import QMessageBox


class AutoSaveDialog(QMessageBox):
    def __init__(self):
        super(AutoSaveDialog, self).__init__()

        self.setWindowTitle(_("Rom was recovered"))
        self.setText(
            _(
                "We found an auto saved ROM from the last session. Do you want to open it?"
            )
        )
        self.setIcon(QMessageBox.Icon.Warning)

        self.discard_rom_button = self.addButton(
            _("Discard Auto Save"), QMessageBox.ButtonRole.DestructiveRole
        )
        self.use_auto_save_button = self.addButton(
            _("Load Auto Save"), QMessageBox.ButtonRole.AcceptRole
        )
        self.setDefaultButton(self.use_auto_save_button)
