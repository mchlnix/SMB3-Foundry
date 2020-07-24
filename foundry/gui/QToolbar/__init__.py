from PySide2.QtWidgets import QSizePolicy, QToolBar, QWidget
from PySide2.QtGui import Qt


class Toolbar(QToolBar):
    """Our custom toolbar to provide consistent functionality"""
    @classmethod
    def default_toolbox(cls, parent: QWidget, name: str, widget: QWidget, side: int) -> "Toolbar":
        """Makes a default toolbox"""
        toolbar = QToolBar(name, parent)
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        toolbar.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        toolbar.setOrientation(Qt.Horizontal)
        toolbar.setFloatable(True)
        toolbar.toggleViewAction().setChecked(True)
        toolbar.addWidget(widget)
        toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea | Qt.TopToolBarArea | Qt.BottomToolBarArea)
        parent.addToolBar(side)
        return toolbar
    