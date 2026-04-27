Level and World Model
=====================

Start here for ROM-backed data structures, header decoding, object/enemy
streams, and overworld data.

- :class:`~foundry.game.level.Level.Level` owns in-level header, object, jump,
  and enemy state.
- :class:`~foundry.game.level.WorldMap.WorldMap` adapts overworld ROM records
  into editor-facing objects, special-level destinations, and renderable map
  state.
- :mod:`foundry.game.Data` is the small ROM-level payload container that
  several higher-level loaders still use as a bridge between raw level bytes
  and richer level-model construction.
- :mod:`foundry.game.ObjectSet` bridges ROM object-set metadata and Foundry's
  richer object-definition tables.
- :mod:`foundry.game.ObjectDefinitions` describes the richer object-definition
  tables consumed by object sets and renderers.
- :mod:`foundry.game.additional_data` documents editor-only metadata persisted
  beside ROM data.
- :mod:`smb3parse.levels` and :mod:`smb3parse.objects` decode the lower-level
  SMB3 level, world-map, and object structures that Foundry later adapts into
  its editor-facing model.
- :class:`~smb3parse.levels.WorldMapPosition.WorldMapPosition` describes one
  overworld tile's decoded level, sprite, and tile relationships before editor
  code wraps them in higher-level workflows.
- :mod:`smb3parse.data_points` contains the ROM tables that feed level
  pointers, world-map structure, pipes, and sprite data before those values are
  composed into fuller level and world objects.
- :mod:`smb3parse.data_points.world_map_data` is the main per-world metadata
  bundle that stages layout offsets, special-level destinations, fortress
  effects, and screen-scoped level-pointer partitions before editors or
  serializers write the world back.
- :mod:`smb3parse._default_constants` and :mod:`smb3parse.constants` document
  the address-bootstrap layer that feeds those data-point and parser modules
  before any level or world decode begins.
- :mod:`smb3parse.util.rom` owns the normalized ROM byte and pointer reads that
  every parser, data-point, and world-model layer builds on before it can
  decode higher-level SMB3 structures.
- :mod:`smb3parse.util.rect` provides the small geometry helpers that those
  parser-side and editor-side world structures reuse when they need rectangle
  and point calculations without pulling in a Qt widget dependency.
- :mod:`smb3parse.util.parser` connects CPU, memory, and record lookups when
  maintainers need to trace decoded structures back to the ROM-address search
  path that produced them.
- :mod:`smb3parse.util.parser.examples` and its concrete entry points show how
  those parser stages are composed when a maintainer needs to drive the lookup
  flow from a world number or from explicit ROM addresses.

Read this next:
:doc:`/subsystems/foundry_game_level_architecture`,
:doc:`/subsystems/smb3parse_levels_architecture`,
:doc:`/subsystems/smb3parse_data_points_architecture`
