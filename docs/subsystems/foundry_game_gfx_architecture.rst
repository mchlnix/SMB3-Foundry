Foundry Graphics Architecture
=============================

Problem and Context
-------------------

The :mod:`foundry.game.gfx` family turns SMB3 CHR bytes, palette rows, TSA
data, and object definitions into the renderable shapes the editor draws. It
has to preserve SMB3 semantics such as tile decoding and generator-driven
object expansion without forcing the GUI to know about bitplanes, palette
indexes, or object-set rendering rules.

Goals
-----

- Keep :class:`foundry.game.gfx.GraphicsSet` and :mod:`foundry.game.gfx.Palette`
  as the ROM-facing graphics inputs.
- Keep drawable primitives such as :class:`foundry.game.gfx.drawable.Tile` and
  :class:`foundry.game.gfx.drawable.Block` reusable across higher-level draw
  paths.
- Keep in-level and world-map object wrappers responsible for renderer-facing
  geometry.
- Support repeated repaint without re-decoding everything on every pass.

Non-Goals
---------

- Make Qt views responsible for tile decode or object expansion.
- Treat graphics primitives as the source of truth for ROM persistence.
- Collapse level-object and world-map rendering into one identical pipeline.

Current State
-------------

The current graphics architecture starts with
:class:`foundry.game.gfx.GraphicsSet` and :mod:`foundry.game.gfx.Palette`, then
builds upward through :class:`foundry.game.gfx.drawable.Tile` and
:class:`foundry.game.gfx.drawable.Block`. Above that, object wrappers in
:mod:`foundry.game.gfx.objects.in_level` and
:mod:`foundry.game.gfx.objects.world_map` adapt decoded game-model state into
renderer-facing geometry and block lists. GUI drawer classes consume those
renderable forms instead of reimplementing the pipeline.

Data Flow
---------

1. Graphics-set and palette modules provide CHR bytes and NES color indexes.
2. :class:`foundry.game.gfx.drawable.Tile` decodes one 8x8 tile into pixel
   data.
3. :class:`foundry.game.gfx.drawable.Block` composes tiles into reusable
   16x16 blocks using TSA data.
4. Object wrappers such as
   :class:`foundry.game.gfx.objects.in_level.level_object.LevelObject` and
   :mod:`foundry.game.gfx.objects.world_map.map_object` turn model data into
   rendered block footprints.
5. Drawer surfaces in the GUI paint those footprints and overlays.

Control Flow
------------

Model or ROM state identifies an object set, graphics set, and palette
context. From there, graphics primitives are decoded once, blocks are composed,
and object renderers expand generator rules into drawn geometry. Repaints
mainly traverse already-decoded state and cached block results rather than
performing fresh ROM interpretation.

Architectural Decisions
-----------------------

- Tile and block primitives are separated so multiple renderers can reuse the
  same decode logic.
- Object rendering is explicit in object-wrapper and renderer modules because
  generator behavior is more than a simple image lookup.
- Graphics decoding stays below the Qt layer so rendering logic remains
  testable without widget ownership.
- Cache-friendly primitives are preferred because the editor repaints the same
  structures often.
- Level-object and world-map render flows are parallel but distinct because
  their geometry rules diverge.

Read This Next
--------------

- Start with :class:`foundry.game.gfx.GraphicsSet` and
  :mod:`foundry.game.gfx.Palette` for graphics inputs.
- Read :class:`foundry.game.gfx.drawable.Tile` and
  :class:`foundry.game.gfx.drawable.Block` for primitive decode and composition.
- Continue to :mod:`foundry.game.gfx.objects.in_level.object_renderer` and
  :class:`foundry.game.gfx.objects.in_level.level_object.LevelObject` for
  in-level object expansion.
- Follow :mod:`foundry.game.gfx.objects.world_map.map_object` for overworld
  rendering.
- Move into :class:`foundry.gui.visualization.level.LevelDrawer` only after the
  graphics-side data shape looks correct.
- Keep :doc:`../api/foundry_game_gfx` open beside this page when you need the
  generated code reference, and use :doc:`enemy_sprite_catalog` when the
  question is visual enemy/item identity.
