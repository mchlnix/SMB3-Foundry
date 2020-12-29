from PySide2.QtGui import QIcon

from foundry import icon_dir, data_dir


def icon(icon_name: str):
    """Gets an icon"""
    icon_path = icon_dir / icon_name
    data_path = data_dir / icon_name

    if icon_path.exists():
        return QIcon(str(icon_path))
    elif data_path.exists():
        return QIcon(str(data_path))
    else:
        raise FileNotFoundError(icon_path)