"""Shared cooperative-inheritance glue for level-settings mixins.

The level-settings dialog is assembled from mixins that each manage one family
of level metadata. This module provides the small shared contract those mixins
expect so update and close-event behavior can move staged UI state back into
the active editor session consistently.

See Also
--------
foundry.gui.level_settings.level_settings_dialog
    Hosts the concrete dialog assembled from these mixins.
foundry.game.level.LevelRef
    Supplies the loaded level state that the mixins stage and commit.
"""

from typing import Callable

from PySide6.QtGui import QMouseEvent, QUndoStack
from PySide6.QtWidgets import QLayout, QVBoxLayout

from foundry.game.level.LevelRef import LevelRef


class SettingsMixin:
    """Provide shared assumptions for level-settings dialog mixins.

    The level-settings dialog is assembled through cooperative multiple
    inheritance. Each mixin expects a parent window, a ``LevelRef`` for the
    loaded level, an undo stack, and an existing Qt layout. This base
    mixin stores the parent and creates the layout when the concrete dialog has
    not done so yet.

    Parameters
    ----------
    *args : object
        Positional arguments forwarded through the cooperative Qt constructor chain.
    **kwargs : object
        Keyword arguments forwarded through the cooperative Qt constructor chain.

    Attributes
    ----------
    _parent : object
        Parent widget that exposes the level view and application settings.
    closeEvent : Callable[[QMouseEvent], None]
        Next ``closeEvent`` implementation in the mixin chain.
    layout : Callable[[], QLayout]
        Qt layout accessor supplied by the concrete widget.
    level_ref : LevelRef
        Reference to the loaded level.
    undo_stack : QUndoStack
        Undo stack where close-time mutations are recorded.
    update : Callable[[], None]
        Next ``update`` implementation in the mixin chain.

    Notes
    -----
    ``SettingsMixin`` is the cooperative-inheritance glue for the level
    settings dialog. It establishes the small shared contract that lets each
    mixin focus on one setting family while still participating in the common
    update and close-event workflow. The data flow is shared dialog state in,
    mixin-specific controls staged locally, then cooperative update and close
    methods carrying those changes back to the editor.
    """

    layout: Callable[[], QLayout]
    update: Callable[[], None]
    closeEvent: Callable[[QMouseEvent], None]

    level_ref: LevelRef
    undo_stack: QUndoStack

    def __init__(self, *args, **kwargs):
        """Initialize shared level-settings mixin state.

        The first positional argument is treated as the owning widget or main
        window and is stored for mixins that need access to the level view.

        Parameters
        ----------
        *args : object
            Positional arguments forwarded through the cooperative constructor chain.
        **kwargs : object
            Keyword arguments forwarded through the cooperative constructor chain.
        """
        super(SettingsMixin, self).__init__(*args, **kwargs)

        self._parent = args[0]  # parent

        if self.layout() is None:
            QVBoxLayout(self)
