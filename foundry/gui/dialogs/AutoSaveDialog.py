from PySide6.QtWidgets import QMessageBox


class AutoSaveDialog(QMessageBox):
    def __init__(self):
        super(AutoSaveDialog, self).__init__()

        self.setWindowTitle("Rom was recovered")
        self.setText("We found an auto saved ROM from the last session. Do you want to open it?")
        self.setIcon(QMessageBox.Warning)

        self.use_auto_save_button = self.addButton("Load Auto Save", QMessageBox.AcceptRole)
        self.setDefaultButton(self.use_auto_save_button)

        self.discard_rom_button = self.addButton("Discard Auto Save", QMessageBox.DestructiveRole)
