

from multipledispatch import dispatch
from PySide2.QtGui import QIcon, QIconEngine, QPixmap


class Icon(QIcon):
    """
    An Icon can generate smaller, larger, active, and disabled Pixmaps from the set of Pixmaps it is given.
    Such Pixmaps are used by Widgets to show an icon representing a particular action.
    """

    @dispatch(QIconEngine)
    def __init__(self, engine: QIconEngine):
        QIcon.__init__(self, engine)

    @dispatch(QPixmap)
    def __init__(self, pixmap: QPixmap):
        QIcon.__init__(self, pixmap)

    @dispatch(QIcon)
    def __init__(self, icon: QIcon):
        QIcon.__init__(self, icon)

    @dispatch(str)
    def __init__(self, filename: str):
        QIcon.__init__(self, filename)

    @classmethod
    def from_filename(cls, filename: str):
        """A more pythonic way to call the init function that is using multiple dispatch"""
        return cls(filename)
