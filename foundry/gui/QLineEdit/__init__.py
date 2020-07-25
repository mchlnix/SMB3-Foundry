"""
This module contains the base functionality for spinners
Spinner: A generic spinner with extended functionality
"""

from typing import Optional
from PySide2.QtWidgets import QWidget, QLineEdit, QSizePolicy, QFormLayout

from foundry.decorators.Observer import Observed
from foundry.gui.QCore import LABEL_TINY, MARGIN_TIGHT
from foundry.gui.QLabel import Label


class LineEdit(QLineEdit):
    """A generic spinner with extended functionality"""
    def __init__(self, parent, text):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setText(text)
        self.on_text_update = Observed(lambda value: value)
        self.textEdited.connect(self.on_text_update.notify_observers)
        self.parent = parent

    @property
    def the_text(self):
        """Returns the text of the line editor as a property"""
        return self.text()


class LineEditPanel(QWidget):
    """A spinner panel with a basic form layout"""
    def __init__(self, parent: Optional[QWidget], name: str, line_edit: LineEdit):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.parent = parent
        self.line_edit = line_edit
        self.on_text_update = self.line_edit.on_text_update
        panel_layout = QFormLayout()
        panel_layout.setContentsMargins(MARGIN_TIGHT, 0, MARGIN_TIGHT, 0)
        self.label = Label(self, name)
        panel_layout.addRow(self.label, self.line_edit)
        self.setLayout(panel_layout)







