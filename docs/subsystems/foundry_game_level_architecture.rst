Foundry Level Architecture
==========================

Problem and Context
-------------------

The :mod:`foundry.game.level` family has to hold SMB3 level and world-map data
in a form that supports editing, rendering, lookup, and serialization at the
same time. The hard part is preserving the encoded ROM meaning while still
giving the rest of the editor direct access to objects, headers, enemies, and
world structures.

Goals
-----

- Keep :class:`foundry.game.level.Level` as the main in-level aggregate for
  header, object, jump, and enemy data.
- Keep :class:`foundry.game.level.WorldMap` as the overworld counterpart with
  its own routing and special-level state.
- Preserve enough source metadata that edits can serialize back to ROM without
  re-discovering everything from scratch.
- Make level lookup and reference flows explicit for surrounding editor code.

Non-Goals
---------

- Use one class hierarchy to erase the difference between levels and world
  maps.
- Move all object rendering logic into the level aggregate itself.
- Push editor-only widget workflow into the model layer.

Current State
-------------

The current design uses :class:`foundry.game.level.Level` as the main aggregate
for active level editing, with helper loaders in :mod:`foundry.game.level`
bridging stock level lookup data from :mod:`foundry.game.Data`. World-map work
routes through :class:`foundry.game.level.WorldMap`. Lightweight references
such as :mod:`foundry.game.level.LevelRef` and editor-only metadata from
:mod:`foundry.game.additional_data` orbit those heavier objects instead of
being folded into them.

Data Flow
---------

1. ROM-backed level offsets and lookup tables are loaded from
   :mod:`foundry.game.Data` and related level loaders.
2. :class:`foundry.game.level.Level` decodes header, object, jump, and enemy
   state into one editable aggregate.
3. :mod:`foundry.game.gfx.objects.in_level` wraps object bytes in renderer- and
   editor-facing forms.
4. GUI surfaces and commands mutate the aggregate or its contained objects.
5. Serialization flows back through the same level-owned state into ROM-facing
   bytes.

Control Flow
------------

The normal flow is load -> inspect -> mutate -> serialize. A level session is
created from ROM addresses or imported data, enriched with object and enemy
wrappers, then read repeatedly by the GUI and renderer. World-map sessions
follow a similar pattern but branch into overworld-specific object and
destination handling.

Architectural Decisions
-----------------------

- :class:`foundry.game.level.Level` is a stateful aggregate because editor
  workflows need one place to keep header, object, and enemy streams in sync.
- World maps remain distinct because their data layout and editor workflows do
  not match in-level object editing.
- Stock lookup data stays in :mod:`foundry.game.Data` and level loaders rather
  than being baked into every level instance.
- Editor-only metadata stays adjacent in :mod:`foundry.game.additional_data`
  rather than pretending it came from the ROM.
- Rendering and visualization consume the level model, but they do not own it.

Read This Next
--------------

- Start with :class:`foundry.game.level.Level` for the main level-editing
  contract.
- Continue to :class:`foundry.game.level.WorldMap` for overworld ownership.
- Read :mod:`foundry.game.Data` when tracing stock level-address lookup or
  world-index metadata.
- Move into :mod:`foundry.game.gfx.objects.in_level.level_object` when the
  issue is inside decoded level objects rather than aggregate ownership.
- Follow :mod:`foundry.game.additional_data` when the confusing state is
  editor-managed rather than ROM-native.
