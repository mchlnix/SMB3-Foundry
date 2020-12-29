

from dataclasses import dataclass
from typing import Set

from PySide2.QtGui import QMouseEvent

from foundry.core.geometry.Position.Position import Position
from foundry.core.util import LEFT_CLICK, RIGHT_CLICK, MIDDLE_CLICK, BACK_CLICK, FORWARD_CLICK, CUSTOM_CLICK


@dataclass
class MouseEvent:
    """A class to hold data from a mouse event"""
    button_sender: str
    button_pressed: Set[str]
    relative_position: Position
    absolute_position: Position

    @classmethod
    def from_qt_mouse_event(cls, event: QMouseEvent) -> "MouseEvent":
        """Makes a mouse event from a q mouse event"""
        prefab_buttons = [LEFT_CLICK, RIGHT_CLICK, MIDDLE_CLICK, BACK_CLICK, FORWARD_CLICK]

        def get_button_pressed():
            """Returns the button pressed"""
            button = event.button()
            idx = 0
            while True:
                if button & 0b01:
                    break
                idx += 1
                button >>= 1
            if 0 <= idx < 5:
                return prefab_buttons[idx]
            else:
                return f"{CUSTOM_CLICK}_{idx - 5}"

        def get_buttons():
            """Returns the buttons pressed"""
            buttons = set()
            buttons_bits = event.buttons()
            for i, button in enumerate(prefab_buttons):
                if (buttons_bits >> i) & 0b01:
                    buttons.update({button})
            buttons_bits >>= 5
            idx = 0
            while buttons_bits != 0:
                if buttons_bits & 0b01:
                    buttons.update({f"{CUSTOM_CLICK}_{idx}"})
                idx += 1
                buttons_bits >>= 1
            return buttons

        return MouseEvent(
            get_button_pressed(),
            get_buttons(),
            Position(event.x(), event.y()),
            Position(event.globalX(), event.globalY())
        )
