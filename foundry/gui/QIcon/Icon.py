

from multipledispatch import dispatch
from PySide2.QtGui import QIcon, QIconEngine, QPixmap


class Icon(QIcon):
    """
    An Icon can generate smaller, larger, active, and disabled Pixmaps from the set of Pixmaps it is given.
    Such Pixmaps are used by Widgets to show an icon representing a particular action.
    """

    @dispatch(object, QIconEngine)
    def __init__(self, engine: QIconEngine):
        super(Icon, self).__init__(engine)

    @dispatch(object, QPixmap)
    def __init__(self, pixmap: QPixmap):
        super(Icon, self).__init__(pixmap)

    @dispatch(object, QIcon)
    def __init__(self, icon: QIcon):
        super(Icon, self).__init__(icon)

    @dispatch(object, str)
    def __init__(self, filename: str):
        super(Icon, self).__init__(filename)