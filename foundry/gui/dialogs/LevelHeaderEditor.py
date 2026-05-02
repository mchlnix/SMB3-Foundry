"""Edit the encoded SMB3 level header through undo-aware dialog controls.

This module owns the dialog that maps Qt controls onto the level header fields
exposed by ``LevelRef``: gameplay flags, Mario start state, graphics and
palette selections, and the next-area pointers that branch into another level.
It is the dialog-layer bridge between human-readable header controls and the
command objects that preserve undo, replay, and dirty-state behavior.

See Also
--------
foundry.game.level.LevelRef
    Header-backed level view edited by this dialog.
foundry.gui.commands
    Command layer that receives staged header changes from this dialog.
foundry.gui.dialogs.level_selector.LevelSelector
    Source of next-area destination data when the user picks another level.
"""

from enum import IntEnum

from PySide6.QtGui import Qt, QUndoStack
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from foundry import make_macro
from foundry.game.gfx.GraphicsSet import GRAPHIC_SET_NAMES
from foundry.game.level.LevelRef import LevelRef
from foundry.gui import OBJECT_SET_ITEM_KEYS, OBJECT_SET_ITEMS
from foundry.gui.commands import (
    SetLevelAttribute,
    SetNextAreaEnemyAddress,
    SetNextAreaObjectAddress,
    SetNextAreaObjectSet,
)
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.dialogs.level_selector.LevelSelector import LevelSelector
from foundry.gui.localization import tr, tr_data_name
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJECT_SET_NAMES
from smb3parse.levels import ENEMY_BASE_OFFSET
from smb3parse.levels.level_header import MARIO_X_POSITIONS, MARIO_Y_POSITIONS

LEVEL_LENGTHS = [0x10 * (i + 1) for i in range(0, 2**4)]
TR_KEY_CONTEXT = "foundry.level_header_editor"


class HeaderStartAction(IntEnum):
    """Map Mario start-action UI choices to encoded header values.

    The SMB3 level header owns these integer values through
    ``LevelRef.start_action``. ``LevelHeaderEditor`` stores the values as combo
    user data, refreshes only their translated labels, and writes the integer
    payload back with ``SetLevelAttribute``. Keep values stable and in encoded
    order; the enum names are code-facing identifiers, while user-visible text
    belongs in ``START_ACTION_LABELS`` and the translation catalog.
    The enum is the data-flow boundary between the Qt selection state and the
    ROM-backed level header field, so translation updates must never replace
    the stored value.

    Attributes
    ----------
    NONE : HeaderStartAction
        No special start action.
    SLIDING : HeaderStartAction
        Mario begins sliding.
    OUT_OF_PIPE_UP : HeaderStartAction
        Mario exits a pipe upward.
    OUT_OF_PIPE_DOWN : HeaderStartAction
        Mario exits a pipe downward.
    OUT_OF_PIPE_RIGHT : HeaderStartAction
        Mario exits a pipe toward the right.
    OUT_OF_PIPE_LEFT : HeaderStartAction
        Mario exits a pipe toward the left.
    RUNNING_AND_CLIMBING_UP_SHIP : HeaderStartAction
        Airship transition start behavior.
    SHIP_AUTO_SCROLLING : HeaderStartAction
        Airship autoscroll start behavior.
    """

    NONE = 0x0
    SLIDING = 0x1
    OUT_OF_PIPE_UP = 0x2
    OUT_OF_PIPE_DOWN = 0x3
    OUT_OF_PIPE_RIGHT = 0x4
    OUT_OF_PIPE_LEFT = 0x5
    RUNNING_AND_CLIMBING_UP_SHIP = 0x6
    SHIP_AUTO_SCROLLING = 0x7


class HeaderMusic(IntEnum):
    """Map music dropdown choices to encoded header indexes.

    The SMB3 level header owns these values through ``LevelRef.music_index``.
    Combo boxes sort by ``int(option)`` so display order follows encoded order,
    and undo/replay records the stable integer rather than a translated label.
    Duplicate visible labels are intentional for distinct encoded values, so
    the enum members and ``MUSIC_LABELS`` entries must not be collapsed.

    Attributes
    ----------
    PLAIN_LEVEL : HeaderMusic
        Plain level music index.
    UNDERGROUND : HeaderMusic
        Underground music index.
    WATER_LEVEL : HeaderMusic
        Water level music index.
    FORTRESS : HeaderMusic
        Fortress music index.
    BOSS : HeaderMusic
        Boss music index.
    SHIP : HeaderMusic
        Airship music index.
    BATTLE : HeaderMusic
        Battle music index.
    P_SWITCH_MUSHROOM_HOUSE_1 : HeaderMusic
        First encoded P-Switch or Mushroom House music value.
    HILLY_LEVEL : HeaderMusic
        Hilly level music index.
    CASTLE_ROOM : HeaderMusic
        Castle room music index.
    CLOUDS_SKY : HeaderMusic
        Clouds or sky music index.
    P_SWITCH_MUSHROOM_HOUSE_2 : HeaderMusic
        Second encoded P-Switch or Mushroom House music value.
    P_SWITCH_MUSHROOM_HOUSE_1_DUPLICATE : HeaderMusic
        Duplicate encoded value with the same display label as the first entry.
    NO_MUSIC_1, NO_MUSIC_2 : HeaderMusic
        Distinct encoded no-music values.
    WORLD_7_MAP : HeaderMusic
        World 7 map music index.
    """

    PLAIN_LEVEL = 0x0
    UNDERGROUND = 0x1
    WATER_LEVEL = 0x2
    FORTRESS = 0x3
    BOSS = 0x4
    SHIP = 0x5
    BATTLE = 0x6
    P_SWITCH_MUSHROOM_HOUSE_1 = 0x7
    HILLY_LEVEL = 0x8
    CASTLE_ROOM = 0x9
    CLOUDS_SKY = 0xA
    P_SWITCH_MUSHROOM_HOUSE_2 = 0xB
    NO_MUSIC_1 = 0xC
    P_SWITCH_MUSHROOM_HOUSE_1_DUPLICATE = 0xD
    NO_MUSIC_2 = 0xE
    WORLD_7_MAP = 0xF


class HeaderTime(IntEnum):
    """Map timer dropdown choices to encoded header values.

    The SMB3 level header owns these values through ``LevelRef.time_index``.
    They are stored as integer combo payloads and displayed through
    ``TIME_LABELS`` plus ``tr`` so live translation never changes the saved
    header value. Keep the member values stable and in encoded order.

    Attributes
    ----------
    SECONDS_300 : HeaderTime
        300-second timer value.
    SECONDS_400 : HeaderTime
        400-second timer value.
    SECONDS_200 : HeaderTime
        200-second timer value.
    UNLIMITED : HeaderTime
        Unlimited timer value.
    """

    SECONDS_300 = 0x0
    SECONDS_400 = 0x1
    SECONDS_200 = 0x2
    UNLIMITED = 0x3


class CameraMovement(IntEnum):
    """Map camera-scroll choices to encoded header values.

    The SMB3 level header owns these values through ``LevelRef.scroll_type``.
    ``LevelHeaderEditor`` uses the enum as stable combo user data, refreshes
    translated display labels from ``CAMERA_MOVEMENT_LABELS``, and writes only
    the integer value through undo commands. ``SHOULD_NOT_APPEAR`` is retained
    for compatibility with rare or invalid ROM data even though the UI warns
    against choosing it.

    Attributes
    ----------
    LOCKED_UNLESS_CLIMBING_FLYING : CameraMovement
        Camera is mostly locked, with climbing or flying exceptions.
    FREE_VERTICAL_SCROLLING : CameraMovement
        Free vertical camera movement.
    LOCKED_BY_START_COORDINATES : CameraMovement
        Camera lock driven by Mario start-coordinate behavior.
    SHOULD_NOT_APPEAR : CameraMovement
        Compatibility value preserved for round-trip safety.
    """

    LOCKED_UNLESS_CLIMBING_FLYING = 0x0
    FREE_VERTICAL_SCROLLING = 0x1
    LOCKED_BY_START_COORDINATES = 0x2
    SHOULD_NOT_APPEAR = 0x3


START_ACTION_LABELS = {
    HeaderStartAction.NONE: "None",
    HeaderStartAction.SLIDING: "Sliding",
    HeaderStartAction.OUT_OF_PIPE_UP: "Out of pipe ↑",
    HeaderStartAction.OUT_OF_PIPE_DOWN: "Out of pipe ↓",
    HeaderStartAction.OUT_OF_PIPE_RIGHT: "Out of pipe →",
    HeaderStartAction.OUT_OF_PIPE_LEFT: "Out of pipe ←",
    HeaderStartAction.RUNNING_AND_CLIMBING_UP_SHIP: "Running and climbing up ship",
    HeaderStartAction.SHIP_AUTO_SCROLLING: "Ship auto scrolling",
}

MUSIC_LABELS = {
    HeaderMusic.PLAIN_LEVEL: "Plain level",
    HeaderMusic.UNDERGROUND: "Underground",
    HeaderMusic.WATER_LEVEL: "Water level",
    HeaderMusic.FORTRESS: "Fortress",
    HeaderMusic.BOSS: "Boss",
    HeaderMusic.SHIP: "Ship",
    HeaderMusic.BATTLE: "Battle",
    HeaderMusic.P_SWITCH_MUSHROOM_HOUSE_1: "P-Switch/Mushroom house (1)",
    HeaderMusic.HILLY_LEVEL: "Hilly level",
    HeaderMusic.CASTLE_ROOM: "Castle room",
    HeaderMusic.CLOUDS_SKY: "Clouds/Sky",
    HeaderMusic.P_SWITCH_MUSHROOM_HOUSE_2: "P-Switch/Mushroom house (2)",
    HeaderMusic.NO_MUSIC_1: "No music",
    HeaderMusic.P_SWITCH_MUSHROOM_HOUSE_1_DUPLICATE: "P-Switch/Mushroom house (1)",
    HeaderMusic.NO_MUSIC_2: "No music",
    HeaderMusic.WORLD_7_MAP: "World 7 map",
}

TIME_LABELS = {
    HeaderTime.SECONDS_300: "300s",
    HeaderTime.SECONDS_400: "400s",
    HeaderTime.SECONDS_200: "200s",
    HeaderTime.UNLIMITED: "Unlimited",
}

CAMERA_MOVEMENT_LABELS = {
    CameraMovement.LOCKED_UNLESS_CLIMBING_FLYING: "Locked, unless climbing/flying",
    CameraMovement.FREE_VERTICAL_SCROLLING: "Free vertical scrolling",
    CameraMovement.LOCKED_BY_START_COORDINATES: "Locked 'by start coordinates'?",
    CameraMovement.SHOULD_NOT_APPEAR: "Shouldn't appear in game, do not use.",
}


SPINNER_MAX_VALUE = 0x0F_FF_FF


def _add_enum_options(dropdown: QComboBox, labels: dict[IntEnum, str]) -> None:
    """Populate an enum-backed combo with stable SMB3 payloads.

    This helper is used during header-editor setup, before any user action has
    staged an undo command. It establishes the state-flow contract for later
    callbacks: Qt rows show localized labels, while row user data carries the
    encoded SMB3 value that is written back to the ROM-backed header.

    Parameters
    ----------
    dropdown : QComboBox
        Combo box that will receive translated display labels.
    labels : dict[IntEnum, str]
        Enum-to-English-source label map. Each enum value is stored as row user
        data so later UI translation updates cannot change the encoded header
        value written by undo commands.
    """
    for option in sorted(labels, key=int):
        dropdown.addItem(
            tr(TR_KEY_CONTEXT, f"{option.__class__.__name__}.{option.name}".casefold(), labels[option]),
            int(option),
        )


def _set_current_data(dropdown: QComboBox, value: int) -> None:
    """Select the row whose user data stores ``value``.

    Legacy index-backed combos may not have explicit user data for every row,
    so the raw encoded value remains the fallback index when no data match is
    found.

    Parameters
    ----------
    dropdown : QComboBox
        Combo box whose selected row should be restored.
    value : int
        Encoded SMB3 header value to match against row user data.
    """
    index = dropdown.findData(value)
    dropdown.setCurrentIndex(index if index >= 0 else value)


def _set_combo_texts(dropdown: QComboBox, labels: list[str]) -> None:
    """Replace combo-box display text without changing encoded selection.

    This is the live-translation path for index-backed header controls such as
    level length and Mario start coordinates. The row order is already the
    SMB3 encoding, so the function refreshes only Qt display text and restores
    the selected index after signals are blocked.

    Parameters
    ----------
    dropdown : QComboBox
        Combo box whose visible row labels should be refreshed.
    labels : list[str]
        Localized labels ordered to match the existing encoded row indexes.
    """
    current_index = dropdown.currentIndex()
    signals_were_blocked = dropdown.blockSignals(True)

    for index, label in enumerate(labels):
        if index < dropdown.count():
            dropdown.setItemText(index, label)

    dropdown.setCurrentIndex(current_index)
    dropdown.blockSignals(signals_were_blocked)


def _set_enum_combo_texts(dropdown: QComboBox, labels: dict[IntEnum, str]) -> None:
    """Refresh enum-backed combo display text in place.

    Each row keeps its stored integer user data, and only the visible text is
    replaced from the enum label map. The selected payload is restored after
    the text update so live language switching cannot change header values.

    Parameters
    ----------
    dropdown : QComboBox
        Combo box whose rows store encoded enum values in ``Qt.UserRole``.
    labels : dict[IntEnum, str]
        Enum-to-English-source label map used as the translation source. The
        enum values remain the SMB3 header identity; translated text is only a
        display boundary.
    """
    current_data = dropdown.currentData()
    signals_were_blocked = dropdown.blockSignals(True)
    labels_by_value = {int(option): label for option, label in labels.items()}
    options_by_value = {int(option): option for option in labels}

    for index in range(dropdown.count()):
        value = dropdown.itemData(index)
        if value is not None:
            option = options_by_value[int(value)]
            dropdown.setItemText(
                index,
                tr(
                    TR_KEY_CONTEXT, f"{option.__class__.__name__}.{option.name}".casefold(), labels_by_value[int(value)]
                ),
            )

    if current_data is not None:
        _set_current_data(dropdown, int(current_data))

    dropdown.blockSignals(signals_were_blocked)


def _translated_level_lengths() -> list[str]:
    """Build localized labels for encoded level-length indexes.

    ``LevelHeaderEditor`` uses this list when constructing or retranslating
    the level tab's length combo.

    Returns
    -------
    list[str]
        Labels ordered to match ``LEVEL_LENGTHS``. The state flow is
        index-backed: combo indexes remain the SMB3 header values while the
        visible block counts follow the active catalog.
    """
    return [
        tr("LevelHeaderEditor", "last_block_length_blocks", "{last_block} / {length} Blocks").format(
            last_block=f"{length - 1:0=#4X}".replace("X", "x"),
            length=length,
        )
        for length in LEVEL_LENGTHS
    ]


def _translated_x_positions() -> list[str]:
    """Build localized labels for Mario start-x header values.

    ``LevelHeaderEditor`` uses this list when constructing or retranslating
    the Mario tab's start-coordinate combo.

    Returns
    -------
    list[str]
        Labels ordered to match ``MARIO_X_POSITIONS``. The state flow is
        index-backed: the list text is display-only, while the combo index
        remains the encoded x-position value used by the level header.
    """
    return [
        tr("LevelHeaderEditor", "block_block_position", "{block}. Block ({position})").format(
            block=position >> 4,
            position=f"{position:0=#4X}".replace("X", "x"),
        )
        for position in MARIO_X_POSITIONS
    ]


def _translated_y_positions() -> list[str]:
    """Build localized labels for Mario start-y header values.

    ``LevelHeaderEditor`` uses this list when constructing or retranslating
    the Mario tab's start-coordinate combo.

    Returns
    -------
    list[str]
        Labels ordered to match ``MARIO_Y_POSITIONS``. The state flow is
        index-backed: the list text is display-only, while the combo index
        remains the encoded y-position value used by the level header.
    """
    return [
        tr("LevelHeaderEditor", "block_block_position", "{block}. Block ({position})").format(
            block=position,
            position=f"{position:0=#4X}".replace("X", "x"),
        )
        for position in MARIO_Y_POSITIONS
    ]


# change of object palette is always triggered for some reason
class LevelHeaderEditor(CustomDialog):
    """Edit the nine-byte SMB3 level header.

    The dialog maps user-facing controls onto the encoded header fields exposed
    by ``Level`` and ``LevelRef``: length, music, timer, scroll behavior, start
    position, palette indexes, graphics set, and next-area pointers. Changes are
    pushed as undo commands so header edits participate in the normal editor
    history.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the edited level.

    Attributes
    ----------
    _graphics_form_layout : QFormLayout
        Generated label/widget rows for graphics-set and palette controls.
        ``retranslate_ui`` uses this layout to refresh labels created by
        ``addRow(str, widget)`` without rebuilding the tab or touching encoded
        header values.
    _jump_form_layout : QFormLayout
        Generated label/widget rows for next-area pointer controls. The layout
        preserves the spinner and combo payload widgets while their translated
        labels are refreshed in place.
    _level_form_layout : QFormLayout
        Generated label/widget rows for length, music, timer, and camera
        behavior controls. It is kept as state solely for live translation of
        Qt-owned labels.
    _mario_form_layout : QFormLayout
        Generated label/widget rows for Mario start-position and start-action
        controls. The selected combo indexes and user-data payloads remain the
        encoded header identity during retranslation.
    _enemy_address_label : QLabel
        Resolved absolute enemy/item address for the next-area pointer.
    _level_address_label : QLabel
        Resolved absolute layout address for the next-area pointer.
    action_dropdown : QComboBox
        Player entry action selector.
    camera_movement_dropdown : QComboBox
        Scroll-type selector.
    enemy_palette_spinner : Spinner
        Enemy palette index editor.
    enemy_pointer_spinner : Spinner
        Next-area enemy offset editor.
    graphic_set_dropdown : QComboBox
        Graphics set selector.
    header_bytes_label : QLabel
        Raw header byte display.
    length_dropdown : QComboBox
        Level length selector.
    level_select_button : QPushButton
        Opens the level selector to stage next-area pointer fields.
    level : LevelRef
        Reference to the level being edited.
    level_is_vertical_cb : QCheckBox
        Vertical-level flag editor.
    level_pointer_spinner : Spinner
        Next-area layout offset editor.
    music_dropdown : QComboBox
        Music index selector.
    next_area_object_set_dropdown : QComboBox
        Object set selector for the next area.
    object_palette_spinner : Spinner
        Object palette index editor.
    pipe_ends_level_cb : QCheckBox
        Pipe-ends-level flag editor.
    current_level_select_button : QPushButton
        Copies active level identity into the next-area pointer fields.
    tab_widget : QTabWidget
        Tab container for grouped header controls.
    time_dropdown : QComboBox
        Timer index selector.
    x_position_dropdown : QComboBox
        Player start x selector.
    y_position_dropdown : QComboBox
        Player start y selector.

    Notes
    -----
    The dialog does not write header bytes directly on every widget change.
    Instead it stages field edits through undo commands so header changes stay
    mergeable, replayable, and visible to the rest of the editor through the
    normal undo-stack workflow.

    See Also
    --------
    SetLevelAttribute
        Base command used for most header-field edits.
    SetNextAreaObjectAddress, SetNextAreaEnemyAddress, SetNextAreaObjectSet
        Commands used for next-area pointer updates.
    """

    def __init__(self, parent: QWidget | None, level_ref: LevelRef):
        """Create controls for editing a level header.

        Widgets are grouped by gameplay concern: level behavior, player start,
        graphics/palettes, and next-area destination. Signal handlers route
        edits into undo commands rather than mutating header bytes directly from
        the form widgets, so the dialog stays aligned with the editor's merge,
        replay, and dirty-state workflow.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the edited level.
        """
        super(LevelHeaderEditor, self).__init__(
            parent, tr("LevelHeaderEditor", "level_header_editor", "Level Header Editor")
        )

        self.level = level_ref

        main_layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # level settings
        self.length_dropdown = QComboBox()
        self.length_dropdown.addItems(_translated_level_lengths())
        self.length_dropdown.activated.connect(self.on_combo)

        self.music_dropdown = QComboBox()
        _add_enum_options(self.music_dropdown, MUSIC_LABELS)
        self.music_dropdown.activated.connect(self.on_combo)

        self.time_dropdown = QComboBox()
        _add_enum_options(self.time_dropdown, TIME_LABELS)
        self.time_dropdown.activated.connect(self.on_combo)

        self.camera_movement_dropdown = QComboBox()
        _add_enum_options(self.camera_movement_dropdown, CAMERA_MOVEMENT_LABELS)
        self.camera_movement_dropdown.activated.connect(self.on_combo)

        self.level_is_vertical_cb = QCheckBox(tr("LevelHeaderEditor", "level_is_vertical", "Level is Vertical"))
        self.level_is_vertical_cb.clicked.connect(self.on_check_box)

        self.pipe_ends_level_cb = QCheckBox(tr("LevelHeaderEditor", "pipe_ends_level", "Pipe ends Level"))
        self.pipe_ends_level_cb.clicked.connect(self.on_check_box)

        check_box_layout = QHBoxLayout()
        check_box_layout.setContentsMargins(0, 0, 0, 0)
        check_box_layout.addWidget(self.level_is_vertical_cb)
        check_box_layout.addWidget(self.pipe_ends_level_cb)

        check_box_widget = QWidget()
        check_box_widget.setLayout(check_box_layout)

        self._level_form_layout = QFormLayout()
        self._level_form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        self._level_form_layout.addRow(tr("LevelHeaderEditor", "level_length", "Level Length:"), self.length_dropdown)
        self._level_form_layout.addRow(tr("LevelHeaderEditor", "music", "Music:"), self.music_dropdown)
        self._level_form_layout.addRow(tr("LevelHeaderEditor", "time", "Time:"), self.time_dropdown)
        self._level_form_layout.addRow(
            tr("LevelHeaderEditor", "vertical_camera_movement", "Vertical Camera Movement:"),
            self.camera_movement_dropdown,
        )

        self._level_form_layout.addWidget(check_box_widget)

        widget = QWidget()
        widget.setLayout(self._level_form_layout)

        self.tab_widget.addTab(widget, tr("LevelHeaderEditor", "level", "Level"))

        # player settings

        self.x_position_dropdown = QComboBox()
        self.x_position_dropdown.addItems(_translated_x_positions())
        self.x_position_dropdown.activated.connect(self.on_combo)

        self.y_position_dropdown = QComboBox()
        self.y_position_dropdown.addItems(_translated_y_positions())
        self.y_position_dropdown.activated.connect(self.on_combo)

        self.action_dropdown = QComboBox()
        _add_enum_options(self.action_dropdown, START_ACTION_LABELS)
        self.action_dropdown.activated.connect(self.on_combo)

        self._mario_form_layout = QFormLayout()
        self._mario_form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        self._mario_form_layout.addRow(tr("LevelHeaderEditor", "starting_x", "Starting X:"), self.x_position_dropdown)
        self._mario_form_layout.addRow(tr("LevelHeaderEditor", "starting_y", "Starting Y:"), self.y_position_dropdown)
        self._mario_form_layout.addRow(tr("LevelHeaderEditor", "action", "Action:"), self.action_dropdown)

        widget = QWidget()
        widget.setLayout(self._mario_form_layout)

        self.tab_widget.addTab(widget, tr("LevelHeaderEditor", "mario", "Mario"))

        # graphic settings

        self.object_palette_spinner = Spinner(self, maximum=7)
        self.object_palette_spinner.valueChanged.connect(self.on_spin)

        self.enemy_palette_spinner = Spinner(self, maximum=3)
        self.enemy_palette_spinner.valueChanged.connect(self.on_spin)

        self.graphic_set_dropdown = QComboBox()
        self.graphic_set_dropdown.addItems(
            [tr_data_name("GraphicsSet", graphics_set) for graphics_set in GRAPHIC_SET_NAMES]
        )
        self.graphic_set_dropdown.activated.connect(self.on_combo)

        self._graphics_form_layout = QFormLayout()
        self._graphics_form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        self._graphics_form_layout.addRow(
            tr("LevelHeaderEditor", "object_palette", "Object Palette:"), self.object_palette_spinner
        )
        self._graphics_form_layout.addRow(
            tr("LevelHeaderEditor", "enemy_palette", "Enemy Palette:"), self.enemy_palette_spinner
        )
        self._graphics_form_layout.addRow(
            tr("LevelHeaderEditor", "graphic_set", "Graphic Set:"), self.graphic_set_dropdown
        )

        widget = QWidget()
        widget.setLayout(self._graphics_form_layout)

        self.tab_widget.addTab(widget, tr("LevelHeaderEditor", "graphics", "Graphics"))

        # next area settings
        self.level_pointer_spinner = Spinner(self)
        self.level_pointer_spinner.valueChanged.connect(self.on_spin)
        self.level_pointer_spinner.setMinimum(0)
        self.level_pointer_spinner.setMaximum(0xFFFF)

        self._level_address_label = QLabel()
        self._level_address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.enemy_pointer_spinner = Spinner(self)
        self.enemy_pointer_spinner.valueChanged.connect(self.on_spin)
        self.enemy_pointer_spinner.setMinimum(0)
        self.enemy_pointer_spinner.setMaximum(0xFFFF)

        self._enemy_address_label = QLabel()
        self._enemy_address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_area_object_set_dropdown = QComboBox()
        self.next_area_object_set_dropdown.addItems(
            [
                tr("Common", object_set_key, object_set_item)
                for object_set_item, object_set_key in zip(OBJECT_SET_ITEMS, OBJECT_SET_ITEM_KEYS)
            ]
        )
        self.next_area_object_set_dropdown.activated.connect(self.on_combo)

        self.level_select_button = QPushButton(
            tr("LevelHeaderEditor", "set_from_level_selector", "Set from Level Selector")
        )
        self.level_select_button.clicked.connect(self._set_jump_destination)

        self.current_level_select_button = QPushButton(
            tr("LevelHeaderEditor", "use_current_level", "Use current Level")
        )
        self.current_level_select_button.clicked.connect(self._set_from_current_level)

        self._jump_form_layout = QFormLayout()
        self._jump_form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        self._jump_form_layout.addRow(
            tr("LevelHeaderEditor", "offset_of_level_objects", "Offset of Level Objects:"),
            self.level_pointer_spinner,
        )
        self._jump_form_layout.addRow(
            tr("LevelHeaderEditor", "address_of_level_objects", "Address of Level Objects:"),
            self._level_address_label,
        )
        self._jump_form_layout.addRow(
            tr("LevelHeaderEditor", "offset_of_enemies", "Offset of Enemies:"), self.enemy_pointer_spinner
        )
        self._jump_form_layout.addRow(
            tr("LevelHeaderEditor", "address_of_enemies", "Address of Enemies:"), self._enemy_address_label
        )
        self._jump_form_layout.addRow(
            tr("LevelHeaderEditor", "object_set", "Object Set:"), self.next_area_object_set_dropdown
        )

        self._jump_form_layout.addRow(QLabel(""))
        self._jump_form_layout.addRow(self.level_select_button)
        self._jump_form_layout.addRow(self.current_level_select_button)

        widget = QWidget()
        widget.setLayout(self._jump_form_layout)

        self.tab_widget.addTab(widget, tr("LevelHeaderEditor", "jump_destination", "Jump Destination"))

        self.header_bytes_label = QLabel()

        main_layout.addWidget(self.header_bytes_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.update()

    @staticmethod
    def _set_form_label_text(form: QFormLayout, field: QWidget, text: str) -> None:
        """Refresh a translated ``QFormLayout`` label for one header field.

        Qt owns labels created by ``addRow(str, widget)``, so live language
        switching has to recover the label through the form layout and replace
        only its display text. The edited SMB3 header widget state and undo
        command payloads remain unchanged.

        Parameters
        ----------
        form : QFormLayout
            Form layout that owns the generated label.
        field : QWidget
            Field widget whose paired label should be updated.
        text : str
            Localized label text to display.
        """
        label = form.labelForField(field)
        if isinstance(label, QLabel):
            label.setText(text)

    def retranslate_ui(self) -> None:
        """Refresh all visible header-editor text after a language change.

        The refresh walks each tab, generated form label, checkbox, button,
        enum-backed combo row, and data-backed combo row. It deliberately
        updates only Qt display text; selected indexes, combo user data,
        next-area offsets, palette values, and undo-stack state continue to
        carry the same encoded SMB3 header fields.
        """
        self.setWindowTitle(tr("LevelHeaderEditor", "level_header_editor", "Level Header Editor"))

        self.tab_widget.setTabText(0, tr("LevelHeaderEditor", "level", "Level"))
        self.tab_widget.setTabText(1, tr("LevelHeaderEditor", "mario", "Mario"))
        self.tab_widget.setTabText(2, tr("LevelHeaderEditor", "graphics", "Graphics"))
        self.tab_widget.setTabText(3, tr("LevelHeaderEditor", "jump_destination", "Jump Destination"))

        self._set_form_label_text(
            self._level_form_layout,
            self.length_dropdown,
            tr("LevelHeaderEditor", "level_length", "Level Length:"),
        )
        self._set_form_label_text(
            self._level_form_layout, self.music_dropdown, tr("LevelHeaderEditor", "music", "Music:")
        )
        self._set_form_label_text(self._level_form_layout, self.time_dropdown, tr("LevelHeaderEditor", "time", "Time:"))
        self._set_form_label_text(
            self._level_form_layout,
            self.camera_movement_dropdown,
            tr("LevelHeaderEditor", "vertical_camera_movement", "Vertical Camera Movement:"),
        )
        self.level_is_vertical_cb.setText(tr("LevelHeaderEditor", "level_is_vertical", "Level is Vertical"))
        self.pipe_ends_level_cb.setText(tr("LevelHeaderEditor", "pipe_ends_level", "Pipe ends Level"))

        self._set_form_label_text(
            self._mario_form_layout,
            self.x_position_dropdown,
            tr("LevelHeaderEditor", "starting_x", "Starting X:"),
        )
        self._set_form_label_text(
            self._mario_form_layout,
            self.y_position_dropdown,
            tr("LevelHeaderEditor", "starting_y", "Starting Y:"),
        )
        self._set_form_label_text(
            self._mario_form_layout, self.action_dropdown, tr("LevelHeaderEditor", "action", "Action:")
        )

        self._set_form_label_text(
            self._graphics_form_layout,
            self.object_palette_spinner,
            tr("LevelHeaderEditor", "object_palette", "Object Palette:"),
        )
        self._set_form_label_text(
            self._graphics_form_layout,
            self.enemy_palette_spinner,
            tr("LevelHeaderEditor", "enemy_palette", "Enemy Palette:"),
        )
        self._set_form_label_text(
            self._graphics_form_layout,
            self.graphic_set_dropdown,
            tr("LevelHeaderEditor", "graphic_set", "Graphic Set:"),
        )

        self._set_form_label_text(
            self._jump_form_layout,
            self.level_pointer_spinner,
            tr("LevelHeaderEditor", "offset_of_level_objects", "Offset of Level Objects:"),
        )
        self._set_form_label_text(
            self._jump_form_layout,
            self._level_address_label,
            tr("LevelHeaderEditor", "address_of_level_objects", "Address of Level Objects:"),
        )
        self._set_form_label_text(
            self._jump_form_layout,
            self.enemy_pointer_spinner,
            tr("LevelHeaderEditor", "offset_of_enemies", "Offset of Enemies:"),
        )
        self._set_form_label_text(
            self._jump_form_layout,
            self._enemy_address_label,
            tr("LevelHeaderEditor", "address_of_enemies", "Address of Enemies:"),
        )
        self._set_form_label_text(
            self._jump_form_layout,
            self.next_area_object_set_dropdown,
            tr("LevelHeaderEditor", "object_set", "Object Set:"),
        )
        self.level_select_button.setText(tr("LevelHeaderEditor", "set_from_level_selector", "Set from Level Selector"))
        self.current_level_select_button.setText(tr("LevelHeaderEditor", "use_current_level", "Use current Level"))

        _set_combo_texts(self.length_dropdown, _translated_level_lengths())
        _set_enum_combo_texts(self.music_dropdown, MUSIC_LABELS)
        _set_enum_combo_texts(self.time_dropdown, TIME_LABELS)
        _set_enum_combo_texts(self.camera_movement_dropdown, CAMERA_MOVEMENT_LABELS)
        _set_combo_texts(self.x_position_dropdown, _translated_x_positions())
        _set_combo_texts(self.y_position_dropdown, _translated_y_positions())
        _set_enum_combo_texts(self.action_dropdown, START_ACTION_LABELS)
        _set_combo_texts(
            self.graphic_set_dropdown,
            [tr_data_name("GraphicsSet", graphics_set) for graphics_set in GRAPHIC_SET_NAMES],
        )
        _set_combo_texts(
            self.next_area_object_set_dropdown,
            [
                tr("Common", object_set_key, object_set_item)
                for object_set_item, object_set_key in zip(OBJECT_SET_ITEMS, OBJECT_SET_ITEM_KEYS)
            ],
        )

    @property
    def undo_stack(self) -> QUndoStack:
        """Expose the shared undo stack used for header-field commands.

        Header changes are pushed here as command objects rather than mutating
        the level directly from callbacks, which keeps dialog edits merged into
        the same history and dirty-state lifecycle as viewport commands.

        Returns
        -------
        QUndoStack
            Undo stack named ``undo_stack`` in the owning window.
        """
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def update(self):
        """Synchronize controls from the loaded level header.

        The method mirrors encoded header fields into widgets, blocks signals
        while converting next-area addresses back into displayed offsets, then
        refreshes the raw-byte preview and emits repaint signals for dependent
        editor surfaces. This is the inbound data-flow path from the active
        ``LevelRef`` into the Qt controls; outbound edits still go through
        undo commands so replay and dirty-state behavior stay consistent.
        """
        length_index = LEVEL_LENGTHS.index(self.level.length)

        self.length_dropdown.setCurrentIndex(length_index)
        _set_current_data(self.music_dropdown, self.level.music_index)
        _set_current_data(self.time_dropdown, self.level.time_index)
        _set_current_data(self.camera_movement_dropdown, self.level.scroll_type)
        self.level_is_vertical_cb.setChecked(self.level.is_vertical)
        self.pipe_ends_level_cb.setChecked(self.level.pipe_ends_level)

        self.x_position_dropdown.setCurrentIndex(self.level.start_x_index)
        self.y_position_dropdown.setCurrentIndex(self.level.start_y_index)
        _set_current_data(self.action_dropdown, self.level.start_action)

        self.object_palette_spinner.setValue(self.level.object_palette_index)
        self.enemy_palette_spinner.setValue(self.level.enemy_palette_index)
        self.graphic_set_dropdown.setCurrentIndex(self.level.graphic_set)

        self.blockSignals(True)

        self.level_pointer_spinner.setValue(self.level.header.jump_level_offset)
        self._level_address_label.setText(
            hex(self.level.header.jump_object_set.level_offset + self.level_pointer_spinner.value())
        )
        self.enemy_pointer_spinner.setValue(self.level.header.jump_enemy_offset)
        self._enemy_address_label.setText(hex(ENEMY_BASE_OFFSET + self.enemy_pointer_spinner.value()))
        self.next_area_object_set_dropdown.setCurrentIndex(self.level.next_area_object_set_no)

        self.blockSignals(False)

        self.header_bytes_label.setText(" ".join(f"{number:0=#4X}"[2:] for number in self.level.header_bytes))

        self.level.palette_changed.emit()
        self.level.data_changed.emit()

    def _set_level_attr(self, name: str, value, display_name="", display_value=""):
        """Push a command that changes one level header attribute.

        ``display_name`` and ``display_value`` let the command present more
        readable undo text than the raw property name or integer value. The
        helper is the dialog's bridge from form widgets to undoable header
        mutations, keeping undo text, command coalescing, and replay behavior
        aligned across combo boxes, check boxes, and spinners.

        Parameters
        ----------
        name : str
            ``LevelRef`` attribute to update.
        value : object
            New value for the attribute.
        display_name : str, optional
            Human-readable field name for undo text.
        display_value : str, optional
            Display text shown in the UI.
        """
        self.undo_stack.push(SetLevelAttribute(self.level, name, value, display_name, display_value))

    def _set_jump_destination(self):
        """Open the level selector and use its choice as next-area data.

        The selected layout address, enemy address, and object set are committed
        as one undo macro.
        """
        level_selector = LevelSelector(self)

        if self.level:
            level_selector.goto_world(self.level.world)

        level_was_selected = level_selector.exec() == QDialog.DialogCode.Accepted

        if not level_was_selected:
            return

        level_address = level_selector.object_data_offset
        enemy_address = level_selector.enemy_data_offset
        object_set_number = level_selector.object_set

        self._set_jump_destination_values(enemy_address, level_address, object_set_number)

        self.update()

    def _set_from_current_level(self):
        """Use the loaded ROM-backed level as the next area.

        Detached levels may not have useful ROM addresses yet. The method warns
        in that case, then still mirrors the level's current address fields so
        existing attached-level workflows keep one direct shortcut path.
        """
        if not self.level.level.attached_to_rom:
            QMessageBox.warning(
                self,
                tr("LevelHeaderEditor", "warning", "Warning"),
                tr(
                    "LevelHeaderEditor",
                    "error.jump_destination_unattached_level",
                    "The current level is not attached to the ROM and does not have a level or enemy address yet.\n\nThat's why you can't set it as a Jump Destination yet.",
                ),
            )

        level_address = self.level.level.header_offset
        enemy_address = self.level.level.enemy_offset
        object_set_number = self.level.level.object_set.number

        self._set_jump_destination_values(enemy_address, level_address, object_set_number)

        self.update()

    def _set_jump_destination_values(self, enemy_offset: int, level_offset: int, object_set_number: int):
        """Commit next-area destination values as one undo macro.

        The three encoded fields are coupled: object set affects how the layout
        pointer is resolved, while the enemy pointer uses a separate base.

        Parameters
        ----------
        enemy_offset : int
            ROM enemy offset.
        level_offset : int
            ROM level offset.
        object_set_number : int
            Object set number that selects graphics and object definitions.
        """
        self.blockSignals(True)

        self.next_area_object_set_dropdown.setCurrentIndex(object_set_number)
        self.level_pointer_spinner.setValue(level_offset)
        self.enemy_pointer_spinner.setValue(enemy_offset)

        self.blockSignals(False)

        make_macro(
            self.undo_stack,
            tr(
                "LevelHeaderEditor",
                "command.set_next_area",
                "Set Next Area to {level_offset}/{enemy_offset}, {object_set}",
            ).format(
                level_offset=f"{level_offset:#x}",
                enemy_offset=f"{enemy_offset:#x}",
                object_set=tr_data_name("ObjectSet", OBJECT_SET_NAMES[object_set_number]),
            ),
            SetNextAreaObjectSet(self.level, object_set_number),
            SetNextAreaObjectAddress(self.level, level_offset),
            SetNextAreaEnemyAddress(self.level, enemy_offset),
        )

    def on_spin(self, new_value):
        """Respond to spinner changes for palette and pointer fields.

        Palette spinners map to ordinary header attributes. Pointer spinners are
        stored as offsets in the UI and converted back to absolute addresses for
        commands.

        Parameters
        ----------
        new_value : int
            Replacement setting value.
        """
        if not self.level or self.signalsBlocked():
            return

        spinner = self.sender()

        if spinner == self.object_palette_spinner:
            self._set_level_attr("object_palette_index", new_value)

        elif spinner == self.enemy_palette_spinner:
            self._set_level_attr("enemy_palette_index", new_value)

        elif spinner == self.level_pointer_spinner and new_value != self.level.header.jump_level_offset:
            self.undo_stack.push(
                SetNextAreaObjectAddress(
                    self.level,
                    self.level.header.jump_object_set.level_offset + new_value,
                )
            )

        elif spinner == self.enemy_pointer_spinner and new_value != self.level.header.jump_enemy_offset:
            self.undo_stack.push(SetNextAreaEnemyAddress(self.level, ENEMY_BASE_OFFSET + new_value))

        self.update()

    def on_combo(self, new_index):
        """Respond to dropdown changes for encoded header fields.

        Each dropdown maps its selected index to the corresponding ``LevelRef``
        property and pushes an undo command when the value actually changes.

        Parameters
        ----------
        new_index : int
            Selected dropdown index.
        """
        if not self.level or self.signalsBlocked():
            return

        dropdown = self.sender()
        assert isinstance(dropdown, QComboBox)

        text = dropdown.currentText()
        current_data = dropdown.currentData()
        encoded_value = new_index if current_data is None else int(current_data)

        if dropdown == self.length_dropdown and (new_length := LEVEL_LENGTHS[new_index]) != self.level.length:
            self._set_level_attr("length", new_length, display_value=text)

        elif dropdown == self.music_dropdown and encoded_value != self.level.music_index:
            self._set_level_attr("music_index", encoded_value, display_value=text)

        elif dropdown == self.time_dropdown:
            self._set_level_attr("time_index", encoded_value, display_value=text)

        elif dropdown == self.camera_movement_dropdown:
            self._set_level_attr(
                "scroll_type",
                encoded_value,
                display_name=tr("LevelHeaderEditor", "camera_movement", "Camera Movement"),
                display_value=text,
            )

        elif dropdown == self.x_position_dropdown:
            self._set_level_attr(
                "start_x_index",
                new_index,
                display_name=tr("LevelHeaderEditor", "mario_start_x", "Mario Start X"),
                display_value=text,
            )

        elif dropdown == self.y_position_dropdown:
            self._set_level_attr(
                "start_y_index",
                new_index,
                display_name=tr("LevelHeaderEditor", "mario_start_y", "Mario Start Y"),
                display_value=text,
            )

        elif dropdown == self.action_dropdown:
            self._set_level_attr(
                "start_action",
                encoded_value,
                display_name=tr("LevelHeaderEditor", "mario_start_action", "Mario Start Action"),
                display_value=text,
            )

        elif dropdown == self.graphic_set_dropdown:
            self._set_level_attr("graphic_set", new_index, display_value=text)

        elif dropdown == self.next_area_object_set_dropdown and new_index != self.level.next_area_object_set_no:
            object_set_cmd = SetNextAreaObjectSet(self.level, new_index)

            # in case the level address changes based on the new object set, don't list that command separately
            make_macro(self.undo_stack, object_set_cmd.text(), object_set_cmd)

        self.update()

    def on_check_box(self, checked):
        """Respond to checkbox changes for boolean header flags.


        Parameters
        ----------
        checked : bool
            New checked state emitted by Qt.
        """
        if not self.level or self.signalsBlocked():
            return

        checkbox = self.sender()
        assert isinstance(checkbox, QCheckBox)
        assert checked == checkbox.isChecked()

        if checkbox == self.pipe_ends_level_cb:
            self._set_level_attr("pipe_ends_level", checked)
        elif checkbox == self.level_is_vertical_cb:
            self._set_level_attr(
                "is_vertical", checked, tr("LevelHeaderEditor", "level_is_vertical", "Level is Vertical")
            )

        self.update()
