"""Decode and compose SMB3 metatile blocks for editor rendering.

This module turns a TSA entry, palette selection, and graphics set into the
16x16 block images reused across Foundry's previews, level rendering, and
inspection tools. It is the point where SMB3 tile-map structure becomes a Qt
image the rest of the editor can cache, scale, and annotate.

See Also
--------
foundry.game.gfx.GraphicsSet
    Supplies the CHR bytes decoded into the block's four tiles.
foundry.gui.visualization.level.LevelDrawer
    Draws many blocks into the larger level-view surfaces.
"""

from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QImage, QPainter, Qt

from foundry.game.gfx.drawable import MASK_COLOR, apply_selection_overlay
from foundry.game.gfx.drawable.Tile import Tile
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import NESPalette, PaletteGroup
from smb3parse.constants import CLOUDY_GRAPHICS_SET

TSA_BANK_0_START = 0 * 256
TSA_BANK_1_START = 1 * 256
TSA_BANK_2_START = 2 * 256
TSA_BANK_3_START = 3 * 256


def get_tile(index, palette_group, palette_index, graphics_set):
    """Decode a tile from the active graphics set.

    Parameters
    ----------
    index : int
        Tile number within the graphics set.
    palette_group : PaletteGroup
        Four palette rows selected by the level object set and header.
    palette_index : int
        Palette row used to resolve the tile's two-bit pixel indexes.
    graphics_set : GraphicsSet
        CHR data source for the tile bytes.

    Returns
    -------
    Tile
        Decoded tile ready to be converted into a Qt image.
    """
    return Tile(index, palette_group, palette_index, graphics_set)


BlockId = tuple[int, str, int]


class Block:
    """Represent one SMB3 16x16 metatile block.

    SMB3 level geometry is built from 16x16 tile-map entries. The lower six bits
    identify the TSA entry that names four 8x8 pattern tiles, while the upper
    two bits select which palette row colors those patterns. Foundry mirrors
    that layout by decoding four ``Tile`` instances and compositing them into a
    cached Qt image for object, level, and palette previews.

    Parameters
    ----------
    block_index : int
        SMB3 tile-map entry whose upper bits select the palette row.
    palette_group : PaletteGroup
        Four palette rows selected by the level object set and header.
    graphics_set : GraphicsSet
        CHR data source for the block's four tiles.
    tsa_data : bytes
        Four 256-byte TSA banks containing upper-left, lower-left, upper-right,
        and lower-right tile numbers.
    frame : int, optional
        Animation frame to read from animated graphics sets.

    Attributes
    ----------
    HEIGHT : int
        Block height in pixels.
    PIXEL_COUNT : int
        Number of pixels in the composited 16x16 block.
    SIDE_LENGTH : int
        Block side length in pixels.
    WIDTH : int
        Block width in pixels.
    _bg_color : QColor
        NES palette color used to fill masked pixels when transparency is off.
    _block_cache : dict[tuple[BlockId, int, bool, bool, int], QImage]
        Shared cache of scaled, selected, and transparency-adjusted block images.
    _images : dict[int, QImage]
        Per-animation-frame 16x16 base images before draw-time effects.
    _palette_group : PaletteGroup
        Palette rows used to resolve the block's tile pixels.
    _palette_index : int
        Palette row selected from the upper two bits of ``block_index``.
    _tsa_data : bytes
        TSA banks that map block indexes to four pattern tile numbers.
    frame : int
        Animation frame represented by the cached image.
    graphics_set : GraphicsSet
        CHR data source for the block's four tiles.
    index : int
        SMB3 tile-map entry used for TSA and palette selection.
    ld_tile : Tile
        Lower-left tile decoded for the represented animation frame.
    lu_tile : Tile
        Upper-left tile decoded for the represented animation frame.
    rd_tile : Tile
        Lower-right tile decoded for the represented animation frame.
    ru_tile : Tile
        Upper-right tile decoded for the represented animation frame.

    Notes
    -----
    ``Block`` is the bridge between ROM/TSA data and nearly every rendered
    editor surface. Once constructed, its base 16x16 image is reused by object
    previews, level views, and block-inspection tools.

    Examples
    --------
    Decode a block once and reuse the cached image in render-time views::

        block = Block(block_index, palette_group, graphics_set, tsa_data)
        image = block.image(scale_factor=2)
    """

    SIDE_LENGTH = 2 * Tile.SIDE_LENGTH
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT

    _tsa_data = bytes()

    _block_cache: dict[tuple[BlockId, int, bool, bool, int], QImage] = {}

    def __init__(
        self,
        block_index: int,
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        tsa_data: bytes,
        frame: int = 0,
    ):
        """Build a 16x16 block from TSA and graphics data.

        The upper two bits of ``block_index`` choose the SMB3 palette row. The
        remaining bits index the TSA banks that name the four 8x8 tiles that
        will be composited during rendering.

        Parameters
        ----------
        block_index : int
            SMB3 tile-map entry whose upper bits select the palette row.
        palette_group : PaletteGroup
            Four palette rows selected by the level object set and header.
        graphics_set : GraphicsSet
            CHR data source for the block's four tiles.
        tsa_data : bytes
            Four 256-byte TSA banks containing the tile numbers for each quadrant.
        frame : int, optional
            Animation frame to read from animated graphics sets.
        """
        self.index = block_index
        self.graphics_set = graphics_set

        self._palette_index = (block_index & 0b1100_0000) >> 6
        self._palette_group = palette_group

        self._tsa_data = tsa_data

        self._images: dict[int, QImage] = {}

        if graphics_set.number == CLOUDY_GRAPHICS_SET:
            self._bg_color = NESPalette[palette_group[self._palette_index][2]]
        else:
            self._bg_color = NESPalette[palette_group[self._palette_index][0]]

        self.frame = frame

        self._render()

    def _render(self):
        """Composite the block's four tiles into a cached image.

        The TSA banks are ordered as upper-left, lower-left, upper-right, and
        lower-right tile indexes. Rendering stores one base 16x16 image per
        animation frame; scaling, selection, and transparency effects are added
        later by ``draw``. This method is the render-stage boundary where a
        ROM-backed block id and palette choice become a reusable Qt image for
        every higher-level view that needs the same block.
        """
        if self.frame in self._images:
            return

        # can't hash a list, so turn it into a string instead
        # TODO can't use a tuple?
        self._block_id: BlockId = (
            self.index,
            str(self._palette_group),
            self.graphics_set.number,
        )

        lu = self._tsa_data[TSA_BANK_0_START + self.index]
        ld = self._tsa_data[TSA_BANK_1_START + self.index]
        ru = self._tsa_data[TSA_BANK_2_START + self.index]
        rd = self._tsa_data[TSA_BANK_3_START + self.index]

        self.graphics_set.anim_frame = self.frame

        self.lu_tile = get_tile(lu, self._palette_group, self._palette_index, self.graphics_set)
        self.ld_tile = get_tile(ld, self._palette_group, self._palette_index, self.graphics_set)

        self.ru_tile = get_tile(ru, self._palette_group, self._palette_index, self.graphics_set)
        self.rd_tile = get_tile(rd, self._palette_group, self._palette_index, self.graphics_set)

        image = QImage(Block.WIDTH, Block.HEIGHT, QImage.Format.Format_RGB888)

        painter = QPainter(image)

        painter.drawImage(QPoint(0, 0), tile_as_image(self.lu_tile))
        painter.drawImage(QPoint(Tile.WIDTH, 0), tile_as_image(self.ru_tile))
        painter.drawImage(QPoint(0, Tile.HEIGHT), tile_as_image(self.ld_tile))
        painter.drawImage(QPoint(Tile.WIDTH, Tile.HEIGHT), tile_as_image(self.rd_tile))

        painter.end()

        if _is_image_only_one_color(image) and image.pixelColor(0, 0) == QColor(*MASK_COLOR):
            self._whole_block_is_transparent = True
        else:
            self._whole_block_is_transparent = False

        self._images[self.frame] = image

    def rerender(self):
        """Ensure the selected animation frame has a rendered image.

        The method keeps the public refresh path explicit while allowing
        ``_render`` to skip frames that are already cached for this block while
        still giving callers one place to refresh the active frame image. It is
        the small cache-boundary method that higher-level preview and animation
        workflows use when they need the active frame image to exist.
        """
        self._render()

    def draw(self, painter: QPainter, x, y, block_length, selected=False, transparent=False):
        """Draw the block image with draw-time editor effects.

        This is the block-level rendering boundary used by object views and
        level views: it applies scaling, transparency fill, and selection
        overlay to the cached per-frame image before painting.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        x : int
            Destination x coordinate.
        y : int
            Destination y coordinate.
        block_length : int
            Drawn side length in pixels.
        selected : bool, optional
            Whether to apply the editor selection overlay.
        transparent : bool, optional
            Whether to preserve masked pixels as transparent.

        Examples
        --------
        Paint a decoded block into a preview image::

            target = QImage(32, 32, QImage.Format.Format_ARGB32)
            target.fill(QColor(0, 0, 0, 0))
            painter = QPainter(target)
            block.draw(painter, 0, 0, 16, transparent=True)
            painter.end()
        """
        block_attributes = (
            self._block_id,
            block_length,
            selected,
            transparent,
            self.frame,
        )

        if block_attributes not in Block._block_cache:
            self.rerender()
            image = self._images[self.frame].copy()

            if block_length != Block.WIDTH:
                image = image.scaled(block_length, block_length)

            # mask out the transparent pixels first
            mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskMode.MaskOutColor)
            image.setAlphaChannel(mask)

            if not transparent:  # or self._whole_block_is_transparent:
                image = self._replace_transparent_with_background(image)

            if selected:
                apply_selection_overlay(image, mask)

            Block._block_cache[block_attributes] = image

        painter.drawImage(x, y, Block._block_cache[block_attributes])

    def _replace_transparent_with_background(self, image):
        # draw image on background layer, to fill transparent pixels
        """Fill masked pixels with the block's background color.

        NES block graphics often rely on transparent pixels over the backdrop
        color. This helper composites the cached frame image onto the block's
        background color so draw-time callers can choose an opaque variant.

        Parameters
        ----------
        image : QImage
            Block image whose alpha channel marks transparent pixels.

        Returns
        -------
        QImage
            Copy of ``image`` composited over the NES backdrop color.
        """
        background = image.copy()
        background.fill(self._bg_color)

        _painter = QPainter(background)
        _painter.drawImage(QPoint(), image)
        _painter.end()

        return background

    @staticmethod
    def clear_cache():
        """Clear the shared draw-image cache for all blocks.

        The cache is shared across block instances because previews repeatedly
        draw the same block with the same scale, frame, selection, and
        transparency options. Clearing it resets shared render state after
        palette, graphics-set, or animation changes that would otherwise leave
        stale block images in later draw workflows.
        """
        Block._block_cache.clear()


def _is_image_only_one_color(image):
    """Return whether an image contains a single indexed color.

    Parameters
    ----------
    image : QImage
        Image to inspect after conversion to indexed color.

    Returns
    -------
    bool
        ``True`` when the converted image has only one color entry.
    """
    copy = image.copy()

    copy.convertTo(QImage.Format.Format_Indexed8)

    return copy.colorCount() == 1


def tile_as_image(tile: Tile, tile_length=8):
    """Convert a decoded tile into a scaled Qt image.

    Parameters
    ----------
    tile : Tile
        Tile whose RGB byte stream should be wrapped by ``QImage``.
    tile_length : int, optional
        Drawn side length in pixels.

    Returns
    -------
    QImage
        RGB image containing the tile pixels at the requested size.
    """
    width = height = tile_length

    image = QImage(tile.pixels, tile.WIDTH, tile.HEIGHT, QImage.Format.Format_RGB888)

    image = image.scaled(width, height)

    return image
