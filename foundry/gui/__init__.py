from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

WORLD_ITEMS = [
    "World Maps",
    "World 1",
    "World 2",
    "World 3",
    "World 4",
    "World 5",
    "World 6",
    "World 7",
    "World 8",
    "Lost Levels",
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


def label_and_widget(label_text: str, widget: QWidget) -> QHBoxLayout:
    label = QLabel(label_text)

    layout = QHBoxLayout()

    layout.addWidget(label)
    layout.addWidget(widget)

    return layout
