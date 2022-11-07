from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from foundry.gui import OBJECT_SET_ITEMS


class ObjectSetSelector(QDialog):
    def __init__(self, parent=None):
        super(ObjectSetSelector, self).__init__(parent)

        self.setWindowTitle("Object Set Selector")
        self.setModal(True)

        self.result = 1

        layout = QVBoxLayout(self)

        description = QLabel("Choose the object set for this new level.\nThis cannot be changed afterwards.\n")
        layout.addWidget(description)

        self.object_set_dropdown = QComboBox()
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS[1:-1])
        layout.addWidget(self.object_set_dropdown)

        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.on_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_button)

        button_group = QHBoxLayout()
        button_group.addWidget(self.ok_button)
        button_group.addWidget(self.cancel_button)

        layout.addLayout(button_group)

    def on_button(self):
        if self.sender() is self.ok_button:
            self.result = self.object_set_dropdown.currentIndex() + 1
            self.accept()
        elif self.sender() is self.cancel_button:
            self.reject()

    @staticmethod
    def get_object_set(parent=None, alternative_title=""):
        dialog = ObjectSetSelector(parent)

        if alternative_title:
            dialog.setWindowTitle(alternative_title)

        if dialog.exec() == QDialog.Accepted:
            return dialog.result
        else:
            return -1
