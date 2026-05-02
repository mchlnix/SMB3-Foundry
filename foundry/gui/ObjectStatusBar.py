"""Status-bar summary for the object selected in the editor.

This module provides :class:`ObjectStatusBar`, the read-only status bar that
listens to :class:`foundry.game.level.LevelRef` and formats the selected
object's diagnostic fields into the main-window message area. It consumes the
current level selection plus each object's ``get_status_info`` output, then
shows the same object state that the editable panels are about to modify.

See Also
--------
foundry.gui.SpinnerPanel.SpinnerPanel : Editable companion panel for object properties.
foundry.game.level.LevelRef.LevelRef : Selection and level state source observed by the status bar.
"""

from PySide6.QtWidgets import QMainWindow, QStatusBar

from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.localization import tr, tr_object_name

TR_KEY_CONTEXT = "foundry.object_status"


class ObjectStatusBar(QStatusBar):
    """Show status fields for the last selected object.

    The status bar listens to ``LevelRef`` changes and formats the selected
    object's reported status information as compact key/value pairs. It is the
    lightweight read-only companion to the spinner panel: instead of exposing
    raw editable bytes, it mirrors whatever diagnostic fields an object chooses
    to publish through ``get_status_info``.

    Parameters
    ----------
    parent : QMainWindow
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the edited level.

    Attributes
    ----------
    _last_object : InLevelObject | None
        Last object used to render the status message. Live retranslation uses
        this object reference to rebuild display text without changing
        selection or object data.
    level_ref : LevelRef
        Reference that owns the edited level and selection.
    """

    def __init__(self, parent: QMainWindow, level_ref: LevelRef):
        """Create the object status bar.

        The status bar sits on the read-only side of the object-editing
        workflow. Construction therefore captures the shared ``LevelRef`` and
        immediately wires its ``data_changed`` signal into ``update`` so every
        selection or object-state change can refresh the displayed diagnostic
        fields without the main window manually pushing messages into the bar.

        Parameters
        ----------
        parent : QMainWindow
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the edited level.
        """
        super(ObjectStatusBar, self).__init__(parent=parent)

        self.level_ref = level_ref
        self._last_object: InLevelObject | None = None
        self.level_ref.data_changed.connect(self.update)

    def clear(self):
        """Clear the displayed status message."""
        self._last_object = None
        self.clearMessage()

    def update(self):
        """Refresh the message from the active selection.

        The last selected object wins so the status bar stays stable when the
        editor has a multi-selection.
        """
        selected_objects = self.level_ref.selected_objects

        if selected_objects:
            self._fill(selected_objects[-1])

    def retranslate_ui(self) -> None:
        """Refresh the displayed status message after a language change.

        The status payload remains the object's English ``get_status_info``
        output. Only the rendered field labels and the visible object name are
        localized, so status refreshes cannot change object identity or model
        data.
        """
        if self._last_object is not None:
            self._fill(self._last_object)
        else:
            self.update()

    def _fill(self, obj: InLevelObject):
        """Display localized status fields for an object.

        ``Name`` is the only status value translated through
        :func:`tr_object_name`; other values are numeric or technical status
        data and are displayed unchanged. Field labels are translated through
        stable ``foundry.object_status`` keys.

        Parameters
        ----------
        obj : InLevelObject
            Object being inspected or modified.
        """
        self._last_object = obj
        info = obj.get_status_info()

        message_parts = []
        for key, value in info:
            translated_key = tr(TR_KEY_CONTEXT, f"field.{str(key).casefold()}", str(key))
            translated_value = tr_object_name(obj) if key == "Name" else value
            message_parts.append(f"{translated_key}: {translated_value}")

        self.showMessage(" | ".join(message_parts))
