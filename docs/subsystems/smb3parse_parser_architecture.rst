SMB3Parse Parser Architecture
=============================

Problem and Context
-------------------

The :mod:`smb3parse.util.parser` family is the orchestration layer that walks
from ROM-backed pointers and addresses to parsed level results. It exists
because some SMB3 questions are not answered by a single table lookup or model
construction step. Foundry needs this family when it must discover levels
across a ROM, follow jump destinations, measure serialized object or enemy
data lengths, or aggregate parsed records into one level result.

Goals
-----

* Provide parser-side aggregates such as
  :class:`smb3parse.util.parser.level.ParsedLevel`.
* Discover levels across world maps and jump destinations through
  :func:`smb3parse.util.parser.gen_levels_in_rom`.
* Keep CPU, memory, and object parsing concerns separated into focused modules.
* Preserve enough provenance that later tools know which ROM origins reach the
  same canonical level.

Non-Goals
---------

* Replacing the narrower address and model layers in
  :mod:`smb3parse.data_points`, :mod:`smb3parse.levels`, or
  :mod:`smb3parse.objects`.
* Owning editor rendering or Foundry UI state.
* Hiding ROM-specific control flow behind a single monolithic parser object.

Current State
-------------

The parser family is split into a few focused modules:

* :mod:`smb3parse.util.parser` provides discovery entry points plus the
  :class:`smb3parse.util.parser.FoundLevel` and
  :class:`smb3parse.util.parser.FoundLevelRecord` handoff types.
* :mod:`smb3parse.util.parser.level` defines
  :class:`smb3parse.util.parser.level.ParsedLevel`, the aggregate parse result
  for one stage.
* :mod:`smb3parse.util.parser.object` holds parsed object and enemy record
  types used by that aggregate.
* :mod:`smb3parse.util.parser.cpu` and
  :mod:`smb3parse.util.parser.memory` emulate the SMB3 load path closely enough
  to measure level payloads and follow control-flow-sensitive parsing steps.
* :mod:`smb3parse.util.parser.examples` contains example entry points for
  parser-driven workflows.

Current code keeps discovery, object parsing, and ROM-emulation responsibilities
separate rather than collapsing them into one parser class.

Data Flow
---------

The main data path is:

1. Discovery starts from world-map pointers or known world-specific slots.
2. Each origin becomes a
   :class:`smb3parse.util.parser.FoundLevelRecord` with object-set and pointer
   provenance attached.
3. Parser helpers load the level through CPU and memory helpers so object and
   enemy streams can be measured and decoded.
4. The parsed result becomes a
   :class:`smb3parse.util.parser.level.ParsedLevel`.
5. Repeated discoveries that reach the same level address merge into one
   canonical :class:`smb3parse.util.parser.FoundLevel` while preserving every
   origin offset.

Control Flow
------------

The highest-level control flow today is centered on
:func:`smb3parse.util.parser.gen_levels_in_rom`:

1. Enumerate worlds and their overworld entries.
2. Seed discovery from world-map pointers and static world-specific slots.
3. Parse each discovered level and inspect its objects for jump destinations.
4. Feed new destinations back into the discovery queue until the reachable ROM
   graph for that world has been explored.
5. Group and return the canonical results for downstream tools.

Below that orchestration layer, object parsing, CPU stepping, and parsed-level
aggregation remain in separate modules.

Architectural Decisions
-----------------------

* Discovery records and canonical parsed results are separate types so the
  parser can merge many origins onto one level without losing provenance.
* CPU and memory helpers remain explicit modules because level discovery needs
  behavior that is closer to SMB3's runtime load path than to a static table
  read.
* :class:`smb3parse.util.parser.level.ParsedLevel` stays close to decoded
  record shapes instead of becoming an editor object model; this keeps parser
  outputs reusable by validation, export, and higher-level editing code.
* Examples live inside the parser package so maintainers can follow real entry
  paths when debugging discovery or parse behavior.

Read This Next
--------------

Use these routes to move outward from the parser family:

* For the model layer that parser results build on, read
  :mod:`smb3parse.levels.level` and :mod:`smb3parse.levels.world_map`.
* For the object-decoding layer consumed during parsing, read
  :mod:`smb3parse.objects.level_object`,
  :mod:`smb3parse.objects.enemy_item`, and
  :mod:`smb3parse.objects.object_set`.
* For the API index that exposes this family in Sphinx, read
  :doc:`../api/smb3parse`.
