from smb3parse.constants import PAGE_A000_ByTileset, PAGE_C000_ByTileset

OFFSET_BY_OBJECT_SET_A000 = PAGE_A000_ByTileset
"""
A list of values, which specify which ROM page should be loaded into addresses 0xA000 - 0xBFFF for a given object set.
This is necessary, since the ROM is larger then the addressable RAM in the NES. The offsets of levels are always into
the RAM, which means, to address levels at different parts in the ROM these parts need to be loaded into the RAM first.
"""

OFFSET_BY_OBJECT_SET_C000 = PAGE_C000_ByTileset
"""
Same with the ROM page and addresses 0xC000 - 0xFFFF.
"""
