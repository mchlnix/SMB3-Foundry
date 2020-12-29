from PySide2.QtWidgets import QMessageBox


class AutoSaveDialog(QMessageBox):
    def __init__(self):
        super(AutoSaveDialog, self).__init__()

        self.setWindowTitle("Auto-Save was found")
        self.setText("We found an auto save from the last session. Do you want to open it?")
        self.setIcon(QMessageBox.Warning)

        self.use_auto_save_button = self.addButton("Load Autosave", QMessageBox.AcceptRole)
        self.setDefaultButton(self.use_auto_save_button)

        self.discard_rom_button = self.addButton("Discard Autosave", QMessageBox.DestructiveRole)
