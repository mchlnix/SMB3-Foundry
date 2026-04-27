"""Edit SMB3 autoscroll through the level-settings dialog.

``AutoScrollMixin`` is the level-settings slice that maps the special
``OBJ_AUTOSCROLL`` enemy record to a checkbox, a path-byte spinner, and the
status label shown in the dialog. It consumes ``level_ref.enemies`` to find
any existing autoscroll object, the parent window's ``level_view`` to build
``AddEnemyAt`` commands, and the persisted ``level_view/draw_autoscroll``
setting so the preview overlay can be restored when editing ends.

The mixin stages dialog output directly in the loaded level by inserting,
removing, or mutating the autoscroll ``EnemyItem`` returned by
``_get_autoscroll()``. When the widget closes, ``closeEvent()`` rewinds those
temporary mutations back to the opening state and emits the final undoable
result as ``RemoveObject``, ``AddEnemyAt``, or a ``make_macro()`` replacement
that preserves the user's chosen autoscroll path.

Notes
-----
Autoscroll is not stored as a standalone level flag. The staged object in
``level_ref.enemies`` is the preview state, while the undo stack commands
created during ``closeEvent()`` are the durable editor output. Changes to this
module should keep those two phases distinct.

See Also
--------
foundry.gui.level_settings.settings_mixin.SettingsMixin
    Provides the shared dialog state, including ``level_ref`` and the undo
    stack used here.
foundry.gui.commands
    Contains ``AddEnemyAt`` and ``RemoveObject``, the commands that receive the
    final staged autoscroll result.
"""

from typing import TYPE_CHECKING

from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QCheckBox, QGroupBox, QLabel, QVBoxLayout

from foundry import make_macro
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.gui import label_and_widget
from foundry.gui.commands import AddEnemyAt, RemoveObject
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJ_AUTOSCROLL

if TYPE_CHECKING:
    from foundry.gui.FoundryMainWindow import FoundryMainWindow

AUTOSCROLL_LABELS = {
    -1: "No Autoscroll in Level.",
    0: "Horizontal Autoscroll",
    1: "Horizontal Autoscroll",
    2: "Moves Level up and right; screen wraps, vertically",
    3: "Moves ceiling down and up (Fortress Spike Levels)",
    4: "Moves ground up, until a door hits the ground",
    5: "Moves ground up and down, used for changes in over-water Levels",
}


class AutoScrollMixin(SettingsMixin):
    """Edit the special enemy item that controls autoscrolling.

    SMB3 autoscroll is encoded as an enemy/item object. The mixin lets users
    enable that object and choose its path byte, while temporarily forcing the
    level view to draw autoscroll guides whenever the setting is active.

    Parameters
    ----------
    parent : 'FoundryMainWindow'
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _autoscroll_visual_setting_before : object
        User's original level-view autoscroll visualization setting.
    _parent : FoundryMainWindow
        Parent window that owns settings, level view, and undo stack.
    auto_scroll_type_label : QLabel
        Human-readable description for the selected autoscroll path.
    auto_scroll_type_spinner : Spinner
        Editor for the encoded autoscroll path byte.
    enabled_checkbox : QCheckBox
        Toggle for adding or removing the autoscroll object.
    original_autoscroll_item : EnemyItem | None
        Autoscroll object present when the dialog opened.
    original_scroll_type : int
        Original encoded autoscroll path byte.
    """

    def __init__(self, parent: "FoundryMainWindow"):
        """Create autoscroll controls from the loaded level state.

        The original autoscroll item and path byte are captured so close
        handling can translate the net result into undoable commands.

        Parameters
        ----------
        parent : 'FoundryMainWindow'
            Parent Qt widget that owns this object.
        """
        super(AutoScrollMixin, self).__init__(parent)

        self._parent = parent

        self.original_autoscroll_item = _get_autoscroll(self.level_ref.enemies)
        self.original_scroll_type = (
            self.original_autoscroll_item.auto_scroll_type if self.original_autoscroll_item else -1
        )

        # Autoscroll
        auto_scroll_group = QGroupBox("Autoscrolling", self)
        QVBoxLayout(auto_scroll_group)

        self.enabled_checkbox = QCheckBox("Enable Autoscroll in Level", self)
        self.enabled_checkbox.toggled.connect(self._insert_autoscroll_object)

        self.auto_scroll_type_spinner = Spinner(self, maximum=0x60 - 1)
        self.auto_scroll_type_spinner.valueChanged.connect(self._update_auto_scroll_type)

        self.auto_scroll_type_label = QLabel(self)

        auto_scroll_group.layout().addWidget(self.enabled_checkbox)
        auto_scroll_group.layout().addLayout(label_and_widget("Scroll Type: ", self.auto_scroll_type_spinner))
        auto_scroll_group.layout().addWidget(self.auto_scroll_type_label)

        self.layout().addWidget(auto_scroll_group)

        self._autoscroll_visual_setting_before = self._parent.settings.value("level_view/draw_autoscroll")

    def update(self):
        # auto scroll
        """Synchronize autoscroll controls and preview settings.

        When autoscroll is enabled, the view setting for drawing autoscroll
        guides is forced on so the user can see the path being edited.
        """
        autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        self.enabled_checkbox.setChecked(autoscroll_item is not None)
        self.auto_scroll_type_spinner.setEnabled(autoscroll_item is not None)

        if autoscroll_item is None:
            self.auto_scroll_type_label.setText(AUTOSCROLL_LABELS[-1])
        else:
            self.auto_scroll_type_spinner.setValue(autoscroll_item.auto_scroll_type)
            self.auto_scroll_type_label.setText(AUTOSCROLL_LABELS[autoscroll_item.auto_scroll_type >> 4])

        super(AutoScrollMixin, self).update()

        if self.enabled_checkbox.isChecked():
            self._parent.settings.setValue("level_view/draw_autoscroll", True)
        else:
            self._parent.settings.setValue("level_view/draw_autoscroll", self._autoscroll_visual_setting_before)

    def _update_auto_scroll_type(self, _):
        """Write the spinner value into the temporary autoscroll object.

        The close handler later converts the difference from the original path
        into an undo command.

        Parameters
        ----------
        _ : object
            Ignored Qt signal value.
        """
        autoscroll_item = _get_autoscroll(self.level_ref.enemies)
        assert autoscroll_item is not None

        autoscroll_item.auto_scroll_type = self.auto_scroll_type_spinner.value()

        self.level_ref.data_changed.emit()

        self.update()

    def _insert_autoscroll_object(self, should_insert: bool):
        """Add or remove the temporary autoscroll object.

        The object list is changed immediately so the preview can update, but
        undo commands are deferred until close.

        Parameters
        ----------
        should_insert : bool
            Whether the level should contain an autoscroll object.
        """
        autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        if autoscroll_item is not None:
            self.level_ref.enemies.remove(autoscroll_item)

        if should_insert:
            self.level_ref.enemies.insert(0, self._create_autoscroll_object())

        self.level_ref.data_changed.emit()

        self.update()

    def _create_autoscroll_object(self):
        """Create an autoscroll enemy item from the staged spinner value.

        The helper builds the temporary enemy record inserted while the dialog
        is open. Close handling later decides whether that staged object becomes
        an undoable add or is discarded.

        Returns
        -------
        EnemyItem
            New autoscroll object with the selected path byte.
        """
        return self.level_ref.level.enemy_item_factory.from_properties(
            OBJ_AUTOSCROLL, 0, self.auto_scroll_type_spinner.value()
        )

    def closeEvent(self, event: QMouseEvent):
        """Commit staged autoscroll edits and restore preview settings.

        The method restores the model to its opening state before pushing undo
        commands that reproduce the user's final enable/disable/path selection.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        current_autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        autoscroll_kept_disabled = self.original_autoscroll_item is current_autoscroll_item is None
        autoscroll_was_disabled = self.original_autoscroll_item is not None and current_autoscroll_item is None
        autoscroll_was_enabled = self.original_autoscroll_item is None and current_autoscroll_item is not None

        if autoscroll_kept_disabled:
            # nothing to do
            pass
        elif autoscroll_was_disabled:
            assert self.original_autoscroll_item is not None

            self.level_ref.level.enemies.insert(0, self.original_autoscroll_item)
            self.undo_stack.push(RemoveObject(self.level_ref, self.original_autoscroll_item))
        elif autoscroll_was_enabled:
            assert current_autoscroll_item is not None
            self.level_ref.level.remove_object(current_autoscroll_item)
            self.undo_stack.push(
                AddEnemyAt(
                    self._parent.level_view,
                    self._parent.level_view.from_level_point(*current_autoscroll_item.get_position()),
                    OBJ_AUTOSCROLL,
                    auto_scroll_type=current_autoscroll_item.auto_scroll_type,
                )
            )
        else:
            # autoscroll object might have been changed, first reset state from the start
            assert self.original_autoscroll_item is not None

            if current_autoscroll_item is self.original_autoscroll_item:
                current_autoscroll_item = self.original_autoscroll_item.copy()
            else:
                self.level_ref.level.remove_object(current_autoscroll_item)
                self.level_ref.level.enemies.insert(0, self.original_autoscroll_item)

            assert current_autoscroll_item is not None

            if self.original_scroll_type != current_autoscroll_item.auto_scroll_type:
                assert self.original_autoscroll_item is not current_autoscroll_item

                make_macro(
                    self.undo_stack,
                    "Change Autoscroll Path",
                    RemoveObject(self.level_ref, self.original_autoscroll_item),
                    AddEnemyAt(
                        self._parent.level_view,
                        self._parent.level_view.from_level_point(*current_autoscroll_item.get_position()),
                        OBJ_AUTOSCROLL,
                        auto_scroll_type=current_autoscroll_item.auto_scroll_type,
                    ),
                )

        super(AutoScrollMixin, self).closeEvent(event)

        self._parent.settings.setValue("level_view/draw_autoscroll", self._autoscroll_visual_setting_before)


def _get_autoscroll(enemy_items: list[EnemyItem]) -> EnemyItem | None:
    """Return the level's autoscroll enemy item.

    Parameters
    ----------
    enemy_items : list[EnemyItem]
        Enemy and item objects in the level.

    Returns
    -------
    EnemyItem | None
        Autoscroll object, or ``None`` when the level has no autoscroll.
    """
    for item in enemy_items:
        if item.obj_index == OBJ_AUTOSCROLL:
            return item
    else:
        return None
