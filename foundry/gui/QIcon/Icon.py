

import yaml
from yaml import CLoader as Loader
from multipledispatch import dispatch
from PySide2.QtGui import QIcon, QIconEngine, QPixmap, QImage, QColor, Qt

from foundry import icon_dir, data_dir
from foundry.core.geometry.Position.Position import Position
from foundry.core.geometry.Size.Size import Size
from foundry.game.Rect import Rect
from foundry.game.gfx.objects.EnemyItem import MASK_COLOR
from foundry.core.util.safe_eval import safe_eval

with open(data_dir.joinpath("icons.yaml")) as f:
    _CUSTOM_ICONS = yaml.load(f, Loader=Loader)

sprite_sheet = QImage(str(data_dir / "gfx.png"))
sprite_sheet.convertTo(QImage.Format_RGB888)


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

    @classmethod
    def from_pixmap(cls, pixmap: QPixmap):
        """A more pythonic way to call the init function that is using multiple dispatch"""
        return cls(pixmap)

    @classmethod
    def from_image(cls, image: QImage):
        """Generates an icon from a QImage"""
        return cls.from_pixmap(QPixmap.fromImage(image))

    @classmethod
    def from_image_and_mask_color(cls, image: QImage, mask_color: QColor):
        """Masks out a given color and generates the icon from the QImage"""
        mask = image.createMaskFromColor(mask_color, Qt.MaskOutColor)
        image.setAlphaChannel(mask)
        return cls.from_image(image)

    @classmethod
    def as_custom(cls, name: str):
        """Generates a predefined icon"""
        return cls(str(icon_dir.joinpath(_CUSTOM_ICONS[name]["file"])))
    @classmethod
    def from_sprite_sheet(cls, name: str):
        """Generates an icon from a region from gfx.png"""
        icon_info = _CUSTOM_ICONS[name]
        try:
            x, y = safe_eval(str(icon_info["offset"]["x"])), safe_eval(str(icon_info["offset"]["y"]))
            pos = Position(x, y)
        except ValueError:
            print(f"Invalid offset parameters: {icon_info['offset']}")
            raise ValueError
        try:
            width, height = safe_eval(str(icon_info["size"]["width"])), safe_eval(str((icon_info["size"]["height"])))
            size = Size(width, height)
        except ValueError:
            print(f"Invalid offset parameters: {icon_info['size']}")
            raise ValueError

        image = sprite_sheet.copy(Rect(pos.x, pos.y, size.width, size.height))
        return cls.from_image_and_mask_color(image, QColor(*MASK_COLOR).rgb())
