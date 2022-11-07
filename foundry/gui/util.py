from itertools import filterfalse, tee

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        item.widget().deleteLater()


def center_widget(widget: QWidget):
    center_offset = QPoint(widget.width() // 2, widget.height() // 2)

    widget.move(QApplication.primaryScreen().availableGeometry().center() - center_offset)


# from https://docs.python.org/3/library/itertools.html
def partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true entries"""
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)
