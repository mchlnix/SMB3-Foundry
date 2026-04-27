SMB3 Parse Modules
==================

These pages surface the ROM-decoding and parser-side modules that Foundry and
Scribe build on for level, world-map, and object extraction.

The level family covers decoded headers, world coordinates, and world-map
records. The object and data-point families describe the lower-level ROM tables
that feed those decoded models. The parser utilities bridge CPU, memory, and
record-oriented lookup flows when maintainers need to move from raw addresses
to higher-level SMB3 structures. Start with the family page that matches the
kind of state you are tracing, then follow the linked architecture guides when
you need the larger control flow from ROM bytes to decoded models.

Architecture Guides
-------------------

- :doc:`/subsystems/smb3parse_levels_architecture` explains decoded level and
  world-map state.
- :doc:`/subsystems/smb3parse_objects_architecture` covers shared object-record
  contracts.
- :doc:`/subsystems/smb3parse_data_points_architecture` captures the ROM-table
  layer that feeds the higher-level models.
- :doc:`/subsystems/smb3parse_parser_architecture` traces the parser-side
  control flow from raw ROM addresses toward decoded structures.

.. autosummary::
   :toctree: generated

   smb3parse
   smb3parse._default_constants
   smb3parse.types
   smb3parse.util
   smb3parse.util.rect
   smb3parse.util.rom
   smb3parse.data_points
   smb3parse.levels
   smb3parse.levels.level
   smb3parse.levels.level_header
   smb3parse.levels.WorldMapPosition
   smb3parse.levels.world_map
   smb3parse.objects
   smb3parse.objects.object_set
   smb3parse.objects.level_object
   smb3parse.objects.enemy_item
   smb3parse.data_points.util
   smb3parse.data_points.level_pointer_data
   smb3parse.data_points.world_map_data
   smb3parse.data_points.sprite_data
   smb3parse.data_points.pipe_data
   smb3parse.data_points.fortress_fx_data
   smb3parse.constants
   smb3parse.util.parser
   smb3parse.util.parser.constants
   smb3parse.util.parser.memory
   smb3parse.util.parser.cpu
   smb3parse.util.parser.object
   smb3parse.util.parser.level
   smb3parse.util.parser.examples
   smb3parse.util.parser.examples.canvas
   smb3parse.util.parser.examples.from_world
   smb3parse.util.parser.examples.from_addresses
