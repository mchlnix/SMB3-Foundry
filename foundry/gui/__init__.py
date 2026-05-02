"""Shared GUI constants and small layout helpers.

This module holds lightweight values reused across Foundry's dialog and
settings code, including display labels for worlds/object sets and a helper
for building consistent label-plus-control rows.
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

WORLD_ITEMS = [
    "World 1",
    "World 2",
    "World 3",
    "World 4",
    "World 5",
    "World 6",
    "World 7",
    "World 8",
    "Lost Levels",
    "World Maps",
]
WORLD_ITEM_KEYS = [
    "world_1",
    "world_2",
    "world_3",
    "world_4",
    "world_5",
    "world_6",
    "world_7",
    "world_8",
    "lost_levels",
    "world_maps",
]

OBJECT_SET_ITEMS = [
    "0 Overworld",
    "1 Plains",
    "2 Dungeon",
    "3 Hilly",
    "4 Sky",
    "5 Piranha Plant",
    "6 Water",
    "7 Mushroom",
    "8 Pipe",
    "9 Desert",
    "A Ship",
    "B Giant",
    "C Ice",
    "D Cloudy",
    "E Underground",
    "F Spade Bonus",
]
OBJECT_SET_ITEM_KEYS = [
    "object_set.0x0_overworld",
    "object_set.0x1_plains",
    "object_set.0x2_dungeon",
    "object_set.0x3_hilly",
    "object_set.0x4_sky",
    "object_set.0x5_piranha_plant",
    "object_set.0x6_water",
    "object_set.0x7_mushroom",
    "object_set.0x8_pipe",
    "object_set.0x9_desert",
    "object_set.0xa_ship",
    "object_set.0xb_giant",
    "object_set.0xc_ice",
    "object_set.0xd_cloudy",
    "object_set.0xe_underground",
    "object_set.0xf_spade_bonus",
]


def label_and_widget(label_text: str, widget: QWidget, *widgets: QWidget, add_stretch=True, tooltip="") -> QHBoxLayout:
    """Build a labeled horizontal control row.

    Settings dialogs reuse the same small row pattern over and over: a text
    label on the left, one or more widgets on the right, and optional stretch
    between them so controls stay aligned. The helper centralizes that layout
    so dialogs can share the same spacing and tooltip behavior without
    reassembling the row by hand each time.

    Parameters
    ----------
    label_text : str
        Text displayed by the label.
    widget : QWidget
        Primary widget added to the row.
    *widgets : QWidget
        Additional widgets appended after the primary widget.
    add_stretch : bool, optional
        Whether to insert stretch between the label and the widgets.
    tooltip : str, optional
        Tooltip text assigned to the label.

    Returns
    -------
    QHBoxLayout
        Layout containing the label and widget row.
    """
    label = QLabel(label_text)

    if tooltip:
        label.setToolTip(tooltip)

    layout = QHBoxLayout()

    layout.addWidget(label)

    if add_stretch:
        layout.addStretch(1)

    layout.addWidget(widget)

    for additional_widget in widgets:
        layout.addWidget(additional_widget)

    return layout
