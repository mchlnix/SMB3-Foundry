"""
This module contains a generic dialog class
Dialog: The extended dialog of QDialog
"""

from PySide2.QtGui import Qt, QKeyEvent
from PySide2.QtWidgets import QDialog

from foundry.core.Settings.util import _main_container
from foundry.core.util.get_gui_style import get_gui_style

from foundry.gui.QCore.util import DefaultSizePartial


class Dialog(QDialog, DefaultSizePartial):
    """This class makes the default Dialog window"""
    def __init__(self, parent, title="Title"):
        QDialog.__init__(self, parent)
        DefaultSizePartial.__init__(self)
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setStyleSheet(get_gui_style())
        # Basically updates the dialog whenever the setting changes, very magical
        _main_container.observe_setting("gui_style", lambda *_: self.setStyleSheet(get_gui_style()))

    def keyPressEvent(self, event: QKeyEvent):
        """The action when a key is pressed"""
        if event.key() == Qt.Key_Escape:
            self.on_exit()

    def on_exit(self):
        """When the dialog is being exited"""
        self.hide()

    def closeEvent(self, event):
        """When the dialog is being closed"""
        self.on_exit()
