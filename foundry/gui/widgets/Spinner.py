"""Shared numeric spinner for ROM-facing editor fields.

This module provides :class:`Spinner`, Foundry's common bounded integer editor
for dialogs and widgets that expose SMB3 values directly. The class keeps ROM
addresses, header fields, object bytes, and similar low-level values on one
display/parsing convention so maintainers and users can move between editors
without translating between inconsistent numeric controls.

See Also
--------
foundry.gui.SpinnerPanel
    Combines spinners like this with object-field editing workflows.
"""

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QSpinBox

SPINNER_MAX_VALUE = 0xFF_FF_FF  # arbitrary; 16,7 MB


class Spinner(QSpinBox):
    """Hex-friendly spin box used for ROM addresses and byte fields.

    The widget defaults to a hexadecimal display with a ``0x`` prefix, matching
    how Foundry presents ROM offsets and encoded SMB3 data. Callers can switch
    to decimal by passing ``base=10``. In practice it is the editor's common
    numeric-entry control for low-level values: ROM addresses, object bytes,
    header fields, and other values that are usually discussed in hexadecimal
    during SMB3 hacking and debugging. Using one shared class also keeps
    parsing and presentation rules aligned across dialogs, so users do not have
    to mentally switch between different numeric conventions while moving
    between viewers, settings panes, and low-level editors.

    Parameters
    ----------
    parent : QWidget | None, optional
        Parent Qt widget that owns this object.
    maximum : int, optional
        Maximum accepted value.
    base : int, optional
        Numeric base used for spinner display and parsing.

    Attributes
    ----------
    valueChanged : SignalInstance
        Standard Qt signal emitted after the spinner value changes.

    Notes
    -----
    Using one shared spinner class keeps hexadecimal presentation consistent
    across dialogs and inspection tools, which matters when users compare UI
    values with ROM offsets, disassembly notes, or debug output. It is a small
    but important piece of Foundry's "speak the same language as the ROM"
    interface design.

    See Also
    --------
    foundry.gui.SpinnerPanel.SpinnerPanel
        Pairs low-level numeric editors like this with object and enemy field
        editing workflows.
    """

    valueChanged: SignalInstance

    def __init__(self, parent=None, maximum=SPINNER_MAX_VALUE, base=16):
        """Create a bounded integer spinner with ROM-oriented formatting.

        The constructor establishes the shared numeric-entry policy that the
        rest of the editor relies on: values are clamped to a caller-supplied
        range, displayed in the chosen base, and prefixed for hexadecimal
        entry so dialogs can hand ROM-facing fields to users without repeating
        formatting setup. Later workflows treat the widget as a drop-in field
        editor, so this setup keeps parsing and presentation rules aligned
        across level settings, object editors, and ROM-inspection surfaces.

        Parameters
        ----------
        parent : QWidget | None, optional
            Parent Qt widget that owns this object.
        maximum : int, optional
            Maximum accepted value.
        base : int, optional
            Numeric base used for spinner display and parsing.
        """
        super(Spinner, self).__init__(parent)

        self.setRange(0, maximum)
        self.setDisplayIntegerBase(base)

        if base == 16:
            self.setPrefix("0x")
