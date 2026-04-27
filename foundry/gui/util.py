from itertools import filterfalse, tee, zip_longest

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget


def clear_layout(layout):
    """Clear layout.

    It connects Qt UI behavior with the editor model and command workflow. The method delegates lower-level work while keeping the public workflow focused.

    Parameters
    ----------
    layout : Any
        Layout that receives the widget.
    """
    while layout.count():
        item = layout.takeAt(0)
        item.widget().deleteLater()


def center_widget(widget: QWidget):
    """Center widget.

    It connects Qt UI behavior with the editor model and command workflow. The method delegates lower-level work while keeping the public workflow focused.

    Parameters
    ----------
    widget : QWidget
        Widget added to the layout.
    """
    center_offset = QPoint(widget.width() // 2, widget.height() // 2)

    widget.move(QApplication.primaryScreen().availableGeometry().center() - center_offset)


# from https://docs.python.org/3/library/itertools.html
def partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true entries

    It connects Qt UI behavior with the editor model and command workflow. The return value exposes the Qt state or editor action result expected by the caller.

    Parameters
    ----------
    pred : Any
        Predicate used to classify each item.
    iterable : Any
        Iterable consumed by the helper.

    Returns
    -------
    Any
        Items split according to the predicate result.
    """
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)


def grouper(iterable, n, *, incomplete="fill", fillvalue=None):
    """Collect data into non-overlapping fixed-length chunks or blocks

    It connects Qt UI behavior with the editor model and command workflow. The return value exposes the Qt state or editor action result expected by the caller.

    Parameters
    ----------
    iterable : Any
        Iterable consumed by the helper.
    n : Any
        Group size.
    incomplete : Any, optional
        How incomplete groups are handled.
    fillvalue : Any, optional
        Value used to pad incomplete groups.

    Returns
    -------
    Any
        Tuples grouped from the iterable.

    Raises
    ------
    ValueError
        If the input data or current state is invalid.
    """
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    if incomplete == "fill":
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == "strict":
        return zip(*args, strict=True)
    if incomplete == "ignore":
        return zip(*args)
    else:
        raise ValueError("Expected fill, strict, or ignore")
