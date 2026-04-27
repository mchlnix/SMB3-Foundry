Graphics and Rendering
======================

Start here for SMB3 object expansion, block/tile drawing, and the editor's
rendering pipeline.

- :mod:`foundry.game.gfx` contains block, palette, graphics-set, and object
  rendering logic.
- :class:`~foundry.game.gfx.GraphicsSet.GraphicsSet` resolves level and
  world-map graphics-set numbers into the CHR bytes consumed by renderers.
- :mod:`foundry.game.gfx.drawable.Block` turns TSA data, palettes, and
  graphics bytes into reusable 16x16 block images.
- :mod:`foundry.game.gfx.objects.in_level` adapts ROM-backed object and enemy
  records into renderable editor objects.
- :doc:`enemy_sprite_catalog` shows the complete generated enemy/item sprite
  catalog that shares the editor's static sprite metadata.
- :mod:`foundry.game.gfx.objects.world_map` adapts overworld records into
  selectable world-map objects.
- :class:`~foundry.gui.visualization.level.LevelDrawer.LevelDrawer` draws level
  surfaces and overlays.
- :class:`~foundry.gui.visualization.world.WorldDrawer.WorldDrawer` draws
  world-map surfaces and overlays.

Read this next:
:doc:`/subsystems/foundry_game_gfx_architecture`,
:doc:`/subsystems/enemy_sprite_catalog`,
:doc:`/subsystems/level_world_model`,
:doc:`/api/foundry_game_gfx`
