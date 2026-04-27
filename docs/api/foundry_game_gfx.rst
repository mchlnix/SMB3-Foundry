Foundry Graphics Modules
========================

These pages cover CHR decoding, tile and block drawing, and object wrappers
used by the editor's rendering surfaces.

Start with :class:`~foundry.game.gfx.GraphicsSet` and
:class:`~foundry.game.gfx.Palette.PaletteGroup` when you need the ROM-side
graphics inputs that every renderer depends on. Follow the drawable modules
when you are tracking how those bytes become reusable tiles and blocks, and
then move into the in-level and world-map object wrappers when you need the
renderable forms that the editor views actually paint.

This surface is meant to explain the rendering pipeline from resources ->
drawable primitives -> selectable objects. The autosummary entries therefore
favor the modules that mark those transitions rather than trying to list every
graphics helper. It is also the main place where Foundry's rendering state and
data-flow boundaries become visible: ROM-backed graphics bytes are decoded,
palette and TSA choices become reusable draw primitives, and view-level
surfaces consume those primitives without owning the underlying graphics
policy.

Architecture Guides
-------------------

- :doc:`/subsystems/foundry_game_gfx_architecture` explains the graphics
  pipeline, ownership boundaries, and renderer-facing constraints for this
  family.
- :doc:`/subsystems/graphics_rendering` maps the broader render path from ROM
  resources into view-level drawing code.

.. autosummary::
   :toctree: generated

   foundry.game.gfx.GraphicsSet
   foundry.game.gfx.block_cache
   foundry.game.gfx.Palette
   foundry.game.gfx.drawable.Block
   foundry.game.gfx.drawable.Tile
   foundry.game.gfx.objects.object_like
   foundry.game.gfx.objects.in_level.in_level_object
   foundry.game.gfx.objects.in_level.enemy_item
   foundry.game.gfx.objects.in_level.enemy_item_factory
   foundry.game.gfx.objects.in_level.jump
   foundry.game.gfx.objects.in_level.level_object_factory
   foundry.game.gfx.objects.in_level.level_object
   foundry.game.gfx.objects.in_level.object_renderer
   foundry.game.gfx.objects.world_map.airship_point
   foundry.game.gfx.objects.world_map.level_pointer
   foundry.game.gfx.objects.world_map.locks
   foundry.game.gfx.objects.world_map.map_object
   foundry.game.gfx.objects.world_map.map_tile
   foundry.game.gfx.objects.world_map.sprite
   foundry.game.gfx.objects.world_map.start_posiiton
