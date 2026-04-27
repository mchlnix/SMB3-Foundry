"""Provide a shared horizontal divider widget for Qt-based editor layouts.

This file participates in Foundry's widget-construction workflow. Dialogs,
panels, and settings editors import :class:`HorizontalLine` while assembling a
Qt layout, instantiate it, and insert the configured frame between control
groups so the finished surface presents separate editing stages as distinct
sections. Centralizing that tiny frame setup keeps the visual break consistent
across editor surfaces instead of repeating one-off ``QFrame`` configuration in
each caller.

See Also
--------
foundry.gui.widgets.Spinner
    Another small reusable widget helper used throughout editor-facing forms.
foundry.gui.widgets.table_widget
    Widget utilities that package common Qt presentation patterns for Foundry's
    editor surfaces.
"""

from PySide6.QtWidgets import QFrame


# taken from https://stackoverflow.com/a/41068447/4252230
class HorizontalLine(QFrame):
    """Provide a reusable sunken horizontal divider for Qt layouts.

    Foundry uses this tiny helper anywhere a dialog or panel needs a plain Qt
    separator without repeating the frame-shape setup in each caller. The
    class is intentionally small, but it still carries architectural value: it
    gives the UI code one shared way to ask for a visual section break instead
    of scattering one-off ``QFrame`` configuration across dialogs. That keeps
    presentational structure consistent in the same way other small widget
    helpers keep common editor affordances consistent.

    Notes
    -----
    The value here is mostly consistency and reuse rather than behavior. When a
    large Qt codebase shares tiny presentation helpers like this, dialogs stay
    easier to scan and to update together.
    """

    def __init__(self):
        """Create a horizontal divider with Foundry's default frame styling."""
        super(HorizontalLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
