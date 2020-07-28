

from PySide2.QtWidgets import QSizePolicy


def set_tight_size_policy(instance):
    """Sets a tight size policy"""
    try:
        instance.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    except AttributeError as err:
        print(f"{err}: {instance} does not have function setSizePolicy")
    try:
        instance.setContentsMargins(0, 0, 0, 0)
    except AttributeError as err:
        print(f"{err}: {instance} does not have function setContentsMargin")


class DefaultSizePartial:
    """A partial class for setting the default size to the widget"""
    def __init__(self):
        self.set_size_policy()

    def set_size_policy(self):
        """Sets the size policy of the widget"""
        set_tight_size_policy(self)
