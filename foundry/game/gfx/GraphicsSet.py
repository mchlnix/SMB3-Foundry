"""Load SMB3 CHR page selections into render-ready graphics data.

This module translates the graphics-set number chosen by a level header or
world-map renderer into the CHR ROM segments that Foundry uses while decoding
tiles, blocks, and larger objects. It is the narrow bridge between SMB3's
page-table metadata and the higher-level rendering workflow that expects a
stable byte source for tile extraction, so level loading can hand one
graphics-set number to the renderer and reuse the resulting CHR bytes across
many draw operations without repeating ROM lookup state.

See Also
--------
foundry.game.ObjectSet
    Supplies the object-set metadata that selects which graphics set to use.
foundry.game.gfx.drawable.Block
    Consumes the resolved CHR data while composing 16x16 block previews.
"""

from functools import lru_cache

from foundry.game.File import ROM
from smb3parse.constants import (
    STOCK_LEVEL_BG_PAGES1_BYTES,
    STOCK_LEVEL_BG_PAGES2_BYTES,
    Constants,
)

CHR_ROM_OFFSET = 0x40010
CHR_ROM_SEGMENT_SIZE = 0x400

WORLD_MAP = 0
SPADE_ROULETTE = 16
N_SPADE = 17
VS_2P = 18

# TODO: Can that be changed, or are save to cache this value here?
BG_PAGE_COUNT = Constants.Level_BG_Pages2 - Constants.Level_BG_Pages1  # 23 in stock rom

GRAPHIC_SET_NAMES = [
    "Mario graphics (1)",
    "Plain",
    "Dungeon",
    "Underground (1)",
    "Sky",
    "Pipe/Water (1, Piranha Plant)",
    "Pipe/Water (2, Water)",
    "Mushroom house (1)",
    "Pipe/Water (3, Pipe)",
    "Desert",
    "Ship",
    "Giant",
    "Ice",
    "Clouds",
    "Underground (2)",
    "Spade bonus room",
    "Spade bonus",
    "Mushroom house (2)",
    "Pipe/Water (4)",
    "Hills",
    "Plain 2",
    "Tank",
    "Castle",
    "Mario graphics (2)",
    "Animated graphics (1)",
    "Animated graphics (2)",
    "Animated graphics (3)",
    "Animated graphics (4)",
    "Animated graphics (P-Switch)",
    "Game font/Course Clear graphics",
    "Animated graphics (5)",
    "Animated graphics (6)",
]


class GraphicsSet:
    """Assemble CHR data for one SMB3 graphics set.

    SMB3 level graphics are built from CHR ROM segments selected by background
    page tables. This class resolves those segment indexes, reads the 0x400-byte
    CHR pages used by level and world-map rendering, and exposes frame-aware
    data for animated tiles.

    Parameters
    ----------
    graphic_set_number : int
        Graphics set number from the level header or world-map renderer.

    Attributes
    ----------
    GRAPHIC_SET_BG_PAGE_1 : bytearray
        Resolved first background-page table.
    GRAPHIC_SET_BG_PAGE_2 : bytearray
        Resolved second background-page table.
    _anim_data : list[bytearray]
        World-map animation CHR pages, one entry per animation frame.
    _data : bytearray
        Concatenated CHR data for static and animated tile pages.
    anim_frame : int
        Animation frame selected by renderers.
    number : int
        Graphics set number represented by this instance.

    Examples
    --------
    Load the graphics set chosen by a level header, then read the CHR bytes
    that block and object renderers decode into tiles::

        graphics_set = GraphicsSet.from_number(0)
        graphics_set.anim_frame = 0
        chr_bytes = graphics_set.data
        len(chr_bytes)
        4096

    ``chr_bytes`` is a ``bytearray`` containing the two 0x800-byte CHR pages
    for the active animation frame, ready for tile extraction without another
    ROM-table lookup.
    """

    GRAPHIC_SET_BG_PAGE_1 = bytearray()
    GRAPHIC_SET_BG_PAGE_2 = bytearray()

    def __init__(self, graphic_set_number):
        """Load CHR segments for a graphics set.

        Stock level sets use two ROM tables to choose base and common CHR pages.
        Special sets such as world maps, Spade rooms, and two-player mode append
        fixed segments that match the game's rendering needs. Initialization
        resolves those segment indexes once, then fills ``_data`` and
        ``_anim_data`` so downstream block and object renderers can decode tiles
        without touching the ROM tables again.

        Parameters
        ----------
        graphic_set_number : int
            Graphics set number from the level header or world-map renderer.

        Notes
        -----
        Initialization resolves the ROM page tables once per graphics-set
        number, then stores the static and animated CHR segments that later
        rendering code reuses while decoding many tiles from the same set. The
        constructor therefore does the one-time ROM lookup and cache setup work
        that lets block and object renderers keep their workflow focused on
        tile composition instead of page-selection state.
        """
        if not GraphicsSet.GRAPHIC_SET_BG_PAGE_1:
            GraphicsSet.GRAPHIC_SET_BG_PAGE_1 = self._heuristic_bg_pages(
                STOCK_LEVEL_BG_PAGES1_BYTES, Constants.Level_BG_Pages1
            )
            GraphicsSet.GRAPHIC_SET_BG_PAGE_2 = self._heuristic_bg_pages(
                STOCK_LEVEL_BG_PAGES2_BYTES, Constants.Level_BG_Pages2
            )

        self._data = bytearray()
        self._anim_data = []
        self.anim_frame = 0
        self.number = graphic_set_number

        segments = []

        if graphic_set_number == WORLD_MAP:
            segments = [0x16, 0x20, 0x21, 0x22, 0x23]

            for index in [0x14, 0x70, 0x72, 0x74]:
                self._anim_data.append(bytearray())

                self._read_in_chr_rom_segment(index, self._anim_data[-1])

        if graphic_set_number not in range(BG_PAGE_COUNT):
            self._read_in([graphic_set_number, graphic_set_number + 2])
        else:
            gfx_index = GraphicsSet.GRAPHIC_SET_BG_PAGE_1[graphic_set_number]
            common_index = GraphicsSet.GRAPHIC_SET_BG_PAGE_2[graphic_set_number]

            segments.append(gfx_index)
            segments.append(common_index)

            if graphic_set_number == SPADE_ROULETTE:
                segments.extend([0x20, 0x21, 0x22, 0x23])
            elif graphic_set_number == N_SPADE:
                segments.extend([0x28, 0x29, 0x5A, 0x31])
            elif graphic_set_number == VS_2P:
                segments.extend([0x04, 0x05, 0x06, 0x07])
            else:
                segments.extend(
                    [
                        common_index + 2,
                        common_index + 4,
                        common_index + 6,
                        common_index + 8,
                    ]
                )

        self._read_in(segments)

    @property
    def data(self):
        """Assemble CHR data for the active animation frame.

        Level sets keep the first page static and swap the animated second page
        by ``anim_frame``. World-map sets prepend their frame-specific animation
        data before the static pages.

        Returns
        -------
        bytearray
            Concatenated CHR bytes used by tile decoding. Block and object
            renderers treat this property as the boundary where graphics-set
            metadata becomes the byte stream consumed by ``Tile`` decoding,
            with the active animation-frame state already folded into the
            returned page layout for the rest of the render workflow.

        Examples
        --------
        Read the CHR byte buffer for the active frame::

            graphics_set = GraphicsSet.from_number(0)
            len(graphics_set.data)
            4096
        """
        if self.number == WORLD_MAP:
            return self._anim_data[self.anim_frame] + self._data
        else:
            # cycle through the second page containing the animated tiles for level objects
            page_1 = self._data[0 : 2 * CHR_ROM_SEGMENT_SIZE]

            start = 2 * CHR_ROM_SEGMENT_SIZE + self.anim_frame * 2 * CHR_ROM_SEGMENT_SIZE
            end = 2 * CHR_ROM_SEGMENT_SIZE + start + 2 * CHR_ROM_SEGMENT_SIZE

            page_2 = self._data[start:end]

            return page_1 + page_2

    def _read_in(self, segments):
        """Append CHR ROM data for the segment sequence chosen during setup.

        This helper is the small workflow step that turns the segment list
        assembled by ``__init__`` into cached byte state. Keeping the ROM read
        loop here lets setup logic choose pages separately from the lower-level
        byte-loading path.

        Parameters
        ----------
        segments : list[int]
            CHR segment indexes to append to ``_data``.
        """
        for segment in segments:
            self._read_in_chr_rom_segment(segment, self._data)

    def _heuristic_bg_pages(self, bg_page_bytes: bytes, fallback_addr: int) -> bytearray:
        """Searches through the ROM's PRG030 bank (second-to-last bank) for the main array responsible
        for rendering the correct graphics. Currently the heuristics in order of precedence are:

        1. Search for the bytes from the stock ROM (given as the bg_page_bytes argument)
            - When changing up the assembly, it's probably rare that this array changes, but it can
              easily change position in the bank, so this is most likely to be correct if it is found.

        2. Use the given `fallback_addr`.

        TODO: Do more/better heuristics than searching the stock bytes.

        Parameters
        ----------
        bg_page_bytes : bytes
            Stock table bytes to search for in PRG030.
        fallback_addr : int
            ROM address used when the stock byte pattern is not found.

        Returns
        -------
        bytearray
            Background page indexes selected by the heuristic.
        """
        bgpages_addr = ROM().search_bank(bg_page_bytes, ROM.PRG030_INDEX)
        if bgpages_addr == -1:
            bgpages_addr = fallback_addr
        return ROM().read(bgpages_addr, BG_PAGE_COUNT)

    @staticmethod
    def _read_in_chr_rom_segment(index, data):
        """Append one two-page CHR ROM segment to a bytearray.

        Each segment index points at two adjacent 0x400-byte CHR pages, so this
        helper is the low-level step that turns segment indexes into the byte
        stream cached on the graphics set.

        Parameters
        ----------
        index : int
            CHR segment index.
        data : bytearray
            Destination bytearray to extend.
        """
        offset = CHR_ROM_OFFSET + index * CHR_ROM_SEGMENT_SIZE
        chr_rom_data = ROM().read(offset, 2 * CHR_ROM_SEGMENT_SIZE)

        data.extend(chr_rom_data)

    @staticmethod
    @lru_cache(32)
    def from_number(graphic_set_number: int) -> "GraphicsSet":
        """Load or reuse a cached graphics set by number.

        Graphics sets are reused by block rendering, object previews, and world
        maps, so instances are cached by graphics-set number. This is the
        shared lookup boundary that keeps higher-level render workflows working
        with stable graphics-set state instead of repeating CHR setup.

        Parameters
        ----------
        graphic_set_number : int
            Graphics set number to load.

        Returns
        -------
        'GraphicsSet'
            Cached graphics set.
        """
        return GraphicsSet(graphic_set_number)
