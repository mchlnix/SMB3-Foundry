from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

WORLD_ITEMS = [
    _("World 1"),
    _("World 2"),
    _("World 3"),
    _("World 4"),
    _("World 5"),
    _("World 6"),
    _("World 7"),
    _("World 8"),
    _("Lost Levels"),
    _("World Maps"),
]

OBJECT_SET_ITEMS = [
    _("0 Overworld"),
    _("1 Plains"),
    _("2 Dungeon"),
    _("3 Hilly"),
    _("4 Sky"),
    _("5 Piranha Plant"),
    _("6 Water"),
    _("7 Mushroom"),
    _("8 Pipe"),
    _("9 Desert"),
    _("A Ship"),
    _("B Giant"),
    _("C Ice"),
    _("D Cloudy"),
    _("E Underground"),
    _("F Spade Bonus"),
]


def label_and_widget(label_text: str, widget: QWidget, *widgets: QWidget, add_stretch=True, tooltip="") -> QHBoxLayout:
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
