"""
This module adds mouse tracking abilities to QWidgets
PartialTrackingObject: A partial implementation of the tracking object to be installed into preexisting widgets
TrackingObject: A fully working widget with the implementation
"""


from typing import List, Optional
from PySide2.QtWidgets import QWidget, QApplication
from PySide2.QtGui import QMouseEvent
from PySide2.QtCore import QTimer, Qt

from .Action import Action, AbstractActionObject

from foundry.gui.QCore import SINGLE_CLICK, DOUBLE_CLICK

from foundry.gui.QWidget import Widget

from foundry.core.Observables.ObservableDecorator import ObservableDecorator


class PartialTrackingObject:
    """
    This class provides the partial implementation of the a tracking object
    Note: must implement setMouseTracking
    This is mainly meant to extend QWidgets and not cause inheritance issues
    """
    def __init__(self):
        self.last = None
        self.setMouseTracking(True)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("pressed", ObservableDecorator(lambda button: button)),
            Action("released", ObservableDecorator(lambda button: button)),
            Action("single_clicked", ObservableDecorator(lambda button: button)),
            Action("double_clicked", ObservableDecorator(lambda button: button)),
            Action("mouse_moved", ObservableDecorator(lambda pos: pos))
        ]

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles a button being pressed"""
        self.pressed_action.observer(event.button())
        self.last = SINGLE_CLICK

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handles a button being released"""
        self.released_action.observer(event.button())
        if self.last == SINGLE_CLICK:
            button = event.button()
            QTimer.singleShot(QApplication.instance().doubleClickInterval(), lambda *_: self.single_click_event(button))
        else:
            self.double_click_event(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handles the mouse moving"""
        self.mouse_moved_action.observer(event.pos())

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handles a button being double pressed"""
        self.last = DOUBLE_CLICK

    def double_click_event(self, event: QMouseEvent):
        """Handles a button being double clicked"""
        self.double_clicked_action.observer(event.button())

    def single_click_event(self, button: Qt.MouseButton):
        """Handles a button being single clicked"""
        self.single_clicked_action.observer(button)


class TrackingObject(Widget, PartialTrackingObject, AbstractActionObject):
    """Adds button functionality to action objects"""
    def __init__(self, parent: Optional[QWidget]):
        super(Widget, self).__init__(parent)
        super(PartialTrackingObject, self).__init__()
        super(AbstractActionObject, self).__init__()
