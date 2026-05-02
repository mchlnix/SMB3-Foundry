"""Raw SMB3 field editors for one selected in-level object.

This module owns ``SpinnerPanel``, the low-level editor surface that mirrors a
single selected object's encoded SMB3 fields into Qt spinners. Selection flows
in from ``LevelRef``, the panel stages visible raw values, and user edits flow
back out through ``object_change`` so the rest of the editor can apply domain,
id, and length changes to the selected object.

See Also
--------
foundry.game.level.LevelRef.LevelRef : Selection source that drives spinner repopulation.
foundry.gui.ObjectStatusBar.ObjectStatusBar : Read-only companion that shows object diagnostics.
foundry.gui.widgets.Spinner.Spinner : Hex-oriented spinner widget used for each raw SMB3 field.
"""

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtWidgets import QFormLayout, QLabel, QSizePolicy, QWidget

from foundry.game.gfx.objects import LevelObject
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.localization import tr
from foundry.gui.widgets.Spinner import Spinner

MAX_DOMAIN = 0x07
MAX_TYPE = 0xFF
MAX_LENGTH = 0xFF
TR_CONTEXT = "SpinnerPanel"


class SpinnerPanel(QWidget):
    """Expose raw selected-object fields through bounded spinners.

    The panel shows the SMB3 domain, object/enemy id, and optional fourth-byte
    length for the single selected in-level object. Signals are blocked while
    the widgets mirror selection state so only user edits emit
    ``object_change``. In practice this is Foundry's low-level escape hatch for
    advanced users: it surfaces the same encoded fields the object factories
    and definitions use, without forcing the rest of the UI to expose every raw
    byte directly.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the edited level.

    Attributes
    ----------
    domain_label : QLabel
        Display-only label for the raw domain spinner. It is refreshed by
        :meth:`retranslate_ui` and is not used as model data.
    length_label : QLabel
        Display-only label for the fourth-byte length spinner. It is refreshed
        by :meth:`retranslate_ui` and is not used as model data.
    level_ref : LevelRef
        Reference that owns the edited level and selection.
    object_change : SignalInstance
        Signal emitted when a user-visible spinner value changes. The emitted
        integer is a raw SMB3 field value staged in the spinner, not localized
        display text.
    spin_domain : Spinner
        Spinner for a level object's domain/bank field.
    spin_length : Spinner
        Spinner for a four-byte level object's length field.
    spin_type : Spinner
        Spinner for the object or enemy/item id.
    type_label : QLabel
        Display-only label for the raw object/enemy id spinner. It is refreshed
        by :meth:`retranslate_ui` and is not used as model data.
    zoom_in_triggered : SignalInstance
        Signal reserved for zoom-in shortcuts.
    zoom_out_triggered : SignalInstance
        Signal reserved for zoom-out shortcuts.
    """

    object_change: SignalInstance = Signal(int)

    zoom_in_triggered: SignalInstance = Signal()
    zoom_out_triggered: SignalInstance = Signal()

    def __init__(self, parent: QWidget | None, level_ref: LevelRef):
        """Create the raw object-field spinner panel.

        Construction wires the panel into Foundry's single-selection editing
        path. It subscribes to ``LevelRef.data_changed`` so selection or object
        mutations can repopulate the spinners from the live object, builds one
        spinner for each raw SMB3 field the panel exposes, and leaves those
        controls disabled until a compatible selection exists. Once populated,
        user edits leave through ``object_change`` for the higher-level editor
        flow to translate back into object mutations. The setup therefore runs
        in three phases: create disabled widgets, attach change signals, then
        wait for ``update`` to stage values from a single selected object.
        After that handoff, later ``update`` calls either repopulate the raw
        bytes from one compatible selection or clear and disable the controls
        again when the selection becomes ambiguous. In practice the lifecycle
        is: build an inert panel, bind it to ``LevelRef``, let selection
        changes stage bytes into the spinners, and then let user edits emit raw
        values back into the rest of the editor.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the edited level.
        """
        super(SpinnerPanel, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.level_ref = level_ref
        self.level_ref.data_changed.connect(self.update)

        self.spin_domain = Spinner(self, maximum=MAX_DOMAIN)
        self.spin_domain.setEnabled(False)
        self.spin_domain.valueChanged.connect(self.object_change.emit)

        self.spin_type = Spinner(self, maximum=MAX_TYPE)
        self.spin_type.setEnabled(False)
        self.spin_type.valueChanged.connect(self.object_change.emit)

        self.spin_length = Spinner(self, maximum=MAX_LENGTH)
        self.spin_length.setEnabled(False)
        self.spin_length.valueChanged.connect(self.object_change.emit)

        self.domain_label = QLabel()
        self.type_label = QLabel()
        self.length_label = QLabel()

        spinner_layout = QFormLayout()
        spinner_layout.addRow(self.domain_label, self.spin_domain)
        spinner_layout.addRow(self.type_label, self.spin_type)
        spinner_layout.addRow(self.length_label, self.spin_length)

        self.setLayout(spinner_layout)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh spinner labels and help text from the active catalog.

        The bank/domain, index, and length captions plus the explanatory
        ``WhatsThis`` text are rebuilt in place. The current spinner values,
        enabled state, and selected object payload remain untouched so the raw
        object bytes still describe the same ROM data after the language switch.
        """
        self.domain_label.setText(tr(TR_CONTEXT, "bank_domain", "Bank/Domain:"))
        self.type_label.setText(tr(TR_CONTEXT, "index", "Index:"))
        self.length_label.setText(tr(TR_CONTEXT, "length", "Length:"))
        self.setWhatsThis(
            tr(
                TR_CONTEXT,
                "help.spinner_panel",
                "<b>Spinner Panel</b><br/>The Spinner Panel gives raw byte access to objects for advanced users. The values are shown in hexadecimal notation.<br/>Level objects and enemies/items are categorized using domains and indexes. Which domain an object is in, doesn't hold much information about the object, if at all.<br/>As for the index, the only important information is, that all objects from 0x00 - 0x0F can not be resized. They have fixed dimensions, like the background bushes in Level 1-1.<br/>All other objects have 16 different iterations, meaning 0x10 - 0x1F, for example, is one object, with 16 different sizes, going from smallest to largest. In what way these objects expand, depends on their particular expansion type.<br/>Some '4-byte' objects can expand in a second way, since they have an additional byte holding that information. For example a platform, which can be sized vertically using the index and horizontally using the 4th byte.",
            )
        )

    def update(self):
        """Refresh spinner values from the active single selection.

        The panel only exposes values when exactly one in-level object is
        selected. Multiple selections or empty selections clear the raw-field
        view so spinner edits cannot apply to an ambiguous target.
        """
        if len(self.level_ref.selected_objects) == 1:
            selected_object = self.level_ref.selected_objects[0]

            if isinstance(selected_object, InLevelObject):
                self._populate_spinners(selected_object)

        else:
            self.disable_all()

        super(SpinnerPanel, self).update()

    def _populate_spinners(self, obj: InLevelObject):
        """Populate controls from an in-level object.

        Parameters
        ----------
        obj : InLevelObject
            Object being inspected or modified.
        """
        self.blockSignals(True)

        self.set_type(obj.obj_index)

        self.enable_domain(isinstance(obj, LevelObject), obj.domain)

        if isinstance(obj, LevelObject) and obj.is_4byte:
            self.set_length(obj.length)
        else:
            self.enable_length(False)

        self.blockSignals(False)

    def get_type(self):
        """Expose the staged SMB3 object-id field to edit handlers.

        Higher-level editor code calls this accessor after a spinner edit so it
        can translate the staged id byte back into an object-definition or
        enemy-definition mutation for the selected object.

        Returns
        -------
        int
            Staged object or enemy/item id byte.
        """
        return self.spin_type.value()

    def set_type(self, object_type: int):
        """Stage the SMB3 object-id field for the selected object.

        Repopulation calls this after selection changes so the type spinner
        reflects the encoded id before the user edits it. Enabling the spinner
        at the same time marks that the selected object supports raw id edits
        through this panel.

        Parameters
        ----------
        object_type : int
            SMB3 object or enemy/item id.
        """
        self.spin_type.setValue(object_type)
        self.spin_type.setEnabled(True)

    def get_domain(self):
        """Expose the staged SMB3 domain byte for level-object edits.

        Domain is only meaningful for level objects, so edit handlers read this
        accessor when they need the staged domain byte that will be written
        back into the selected level object.

        Returns
        -------
        int
            Staged domain byte.
        """
        return self.spin_domain.value()

    def set_domain(self, domain: int):
        """Stage the SMB3 level-object domain for the selected object.

        Repopulation uses this setter only for level objects because enemy and
        item selections do not carry the same domain field. Enabling the
        spinner here signals that the selected object can safely route raw
        domain edits back through the editor workflow.

        Parameters
        ----------
        domain : int
            Object domain that determines how the object is interpreted.
        """
        self.spin_domain.setValue(domain)
        self.spin_domain.setEnabled(True)

    def get_length(self) -> int:
        """Expose the staged fourth-byte length for a resizable object.

        Only four-byte SMB3 level objects expose this extra dimension, so edit
        handlers read this accessor when they need the staged length byte for
        the selected resizable object.

        Returns
        -------
        int
            Staged fourth-byte length value.
        """
        return self.spin_length.value()

    def set_length(self, length: int):
        """Stage the fourth-byte length field for the selected object.

        Repopulation uses this setter only when the selected level object has a
        meaningful fourth-byte size component. Enabling the spinner marks that
        the selected object can accept raw length edits without inventing a
        field that does not exist in the encoded object data.

        Parameters
        ----------
        length : int
            Object length value.
        """
        self.spin_length.setValue(length)
        self.spin_length.setEnabled(True)

    def enable_type(self, enable: bool, value: int = 0):
        """Enable or suppress raw id edits for the selected object.

        The type spinner is this panel's direct editor for the SMB3 object or
        enemy/item id field. Repopulation and clearing both use this helper so
        the spinner shows the right staged value while also reflecting whether
        the selected object should permit raw id edits at all.

        Parameters
        ----------
        enable : bool
            Whether the spinner accepts user edits.
        value : int, optional
            Value to display.
        """
        self.spin_type.setValue(value)
        self.spin_type.setEnabled(enable)

    def enable_domain(self, enable: bool, value: int = 0):
        """Enable or suppress raw domain edits for the selected object.

        Domain editing only applies to SMB3 level objects, not enemies or
        items. This helper keeps the domain spinner synchronized with that
        boundary by staging the visible value and disabling edits whenever the
        selected object does not own a meaningful domain field.

        Parameters
        ----------
        enable : bool
            Whether the spinner accepts user edits.
        value : int, optional
            Value to display.
        """
        self.spin_domain.setValue(value)
        self.spin_domain.setEnabled(enable)

    def enable_length(self, enable: bool, value: int = 0):
        """Enable or suppress fourth-byte length edits for the selected object.

        The length spinner is only valid for four-byte SMB3 level objects.
        This helper stages the visible length byte and disables the control
        whenever the selected object does not expose that encoded size field.

        Parameters
        ----------
        enable : bool
            Whether the spinner accepts user edits.
        value : int, optional
            Value to display.
        """
        self.spin_length.setValue(value)
        self.spin_length.setEnabled(enable)

    def clear_spinners(self):
        """Reset all spinner values to zero."""
        self.set_type(0x00)
        self.set_domain(0x00)
        self.set_length(0x00)

    def disable_all(self):
        """Reset and disable every spinner without emitting edits."""
        self.blockSignals(True)

        self.clear_spinners()

        self.enable_type(False)
        self.enable_domain(False)
        self.enable_length(False)

        self.blockSignals(False)
