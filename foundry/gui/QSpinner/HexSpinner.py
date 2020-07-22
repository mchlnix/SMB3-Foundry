"""
This module provides the base functionality for a base 16 spinner
HexSpinner: A spinner that displays numbers in base 16
"""

from . import Spinner


class HexSpinner(Spinner):
    """A spinner that displays numbers in base 16"""
    def __init__(self, parent, minimum=0, maximum=0xFFFFFF):
        super(HexSpinner, self).__init__(parent, minimum, maximum)
        self.setDisplayIntegerBase(16)
        self.setPrefix("0x")
