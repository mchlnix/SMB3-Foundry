SMB3Parse Levels Architecture
=============================

Problem and Context
-------------------

The :mod:`smb3parse.levels` family is the package boundary where raw SMB3 ROM
addresses start becoming level-shaped and overworld-shaped models. Foundry and
other higher-level tooling need one place to answer questions like "which
object set decodes this layout?", "where is the header for this stage?", and
"which world-map tile produced this level?" without forcing every caller to
repeat pointer arithmetic or header parsing.

Goals
-----

* Provide a shared layout contract through :class:`smb3parse.levels.LevelBase`.
* Decode playable stage identity through :class:`smb3parse.levels.level.Level`.
* Decode header geometry and routing metadata through
  :class:`smb3parse.levels.level_header.LevelHeader`.
* Expose overworld models and positions through
  :class:`smb3parse.levels.world_map.WorldMap` and related world-map records.
* Keep object-set-aware address provenance attached to every decoded layout.

Non-Goals
---------

* Rendering editor objects or Qt surfaces.
* Persisting Foundry-specific editor metadata.
* Emulating the full CPU-level parse walk used by
  :mod:`smb3parse.util.parser`.
* Owning low-level pointer-table storage rules; those stay in
  :mod:`smb3parse.data_points`.

Current State
-------------

Today this package is split between shared constants plus a few narrow model
types:

* :mod:`smb3parse.levels` defines shared geometry constants and
  :class:`smb3parse.levels.LevelBase`.
* :mod:`smb3parse.levels.level` binds object-set context, layout address,
  enemy address, and a parsed :class:`~smb3parse.levels.level_header.LevelHeader`
  into one stage-level handoff object.
* :mod:`smb3parse.levels.level_header` decodes the nine-byte SMB3 level header
  that determines geometry, palette, and routing behavior.
* :mod:`smb3parse.levels.world_map` and
  :mod:`smb3parse.levels.WorldMapPosition` expose overworld tile lookup,
  pointer resolution, and world-level navigation state.

The family is intentionally small. It does not decode full object streams on
its own, but it preserves the address, header, and object-set state that later
parsers need.

Data Flow
---------

The normal data path is:

1. A caller starts with either an overworld tile or a known ROM address tuple.
2. :class:`smb3parse.levels.world_map.WorldMap` or
   :class:`smb3parse.levels.WorldMapPosition` resolves a level pointer when the
   source is an overworld tile.
3. :class:`smb3parse.levels.level.Level` binds the chosen object set, layout
   address, and enemy address together.
4. :class:`smb3parse.levels.level.Level` reads the header bytes immediately
   before the layout stream and constructs
   :class:`smb3parse.levels.level_header.LevelHeader`.
5. Downstream object and parser layers consume the resulting model as the
   stable handoff for deeper decoding.

Control Flow
------------

The package supports two main entry paths:

* ``world map -> world map position -> level pointer ->``
  :meth:`~smb3parse.levels.level.Level.from_world_map`
* ``known ROM addresses ->``
  :meth:`~smb3parse.levels.level.Level.from_memory`

After construction, downstream callers mostly use properties and helper
methods. The package avoids long orchestration flows of its own and instead
acts as the integration layer between pointer discovery, header decoding, and
later object parsing.

Architectural Decisions
-----------------------

* :class:`smb3parse.levels.LevelBase` stays narrow. It owns address
  provenance, object-set identity, and rectangular bounds checks, but not
  header parsing or object decoding.
* :class:`smb3parse.levels.level.Level` is a handoff model, not a full parse
  result. It deliberately stops after attaching header state.
* World-map resolution remains separate from level construction so callers can
  preserve overworld provenance only when it exists.
* Shared constants for screen widths, heights, and map boundaries live in the
  package root so stage and overworld decoders reference the same geometry.

Read This Next
--------------

Start here when you need the next layer after a level or world-map model:

* For pointer-table ownership and serialized overworld entries, read
  :mod:`smb3parse.data_points.world_map_data` and
  :mod:`smb3parse.data_points.level_pointer_data`.
* For object-set-aware level parsing beyond the header, read
  :mod:`smb3parse.objects.object_set` and
  :mod:`smb3parse.util.parser.level`.
* For the higher-level API surface that exposes these modules in Sphinx, read
  :doc:`../api/smb3parse`.
