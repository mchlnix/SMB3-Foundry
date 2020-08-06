from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices


def open_url(url: str):
    """Opens a given URL"""
    QDesktopServices.openUrl(QUrl(url))