

import yaml
from yaml import CLoader as Loader
from PySide2.QtGui import QImage, QColor, Qt

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


class Image(QImage):
    """
    An Icon can generate smaller, larger, active, and disabled Pixmaps from the set of Pixmaps it is given.
    Such Pixmaps are used by Widgets to show an icon representing a particular action.
    """

    @classmethod
    def from_filename(cls, filename: str, format):
        """A more pythonic way to call the init function that is using multiple dispatch"""
        return cls(filename, format)

    @classmethod
    def from_image(cls, image: QImage):
        """Generates an icon from a QImage"""
        return cls(image)

    @classmethod
    def from_image_and_mask_color(cls, image: QImage, mask_color: QColor):
        """Masks out a given color and generates the icon from the QImage"""
        mask = image.createMaskFromColor(mask_color, Qt.MaskOutColor)
        image.setAlphaChannel(mask)
        return cls.from_image(image)

    @classmethod
    def as_custom(cls, name: str):
        """Generates a predefined icon"""
        action = _CUSTOM_ICONS[name]["type"]
        if action == "normal":
            return cls.from_filename(str(icon_dir.joinpath(_CUSTOM_ICONS[name]["file"])), QImage.Format_RGB888)
        elif action == "graphics_sheet":
            return cls.from_sprite_sheet(name)

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
        mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)
        image.setAlphaChannel(mask)

        return Image.from_image(image)
