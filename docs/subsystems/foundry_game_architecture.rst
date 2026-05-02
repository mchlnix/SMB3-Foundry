Foundry Game Architecture
=========================

Problem and Context
-------------------

The :mod:`foundry.game` family is the editor's ROM-backed model layer. It has
to convert SMB3 addresses, object-set metadata, level tables, and world data
into stable editor objects that the GUI, renderer, and save workflows can all
share. Maintainers usually need this page when a bug sits below Qt but above
raw parsing.

Goals
-----

- Provide editor-facing level and world abstractions with stable contracts.
- Keep ROM, object-definition, and graphics metadata available without forcing
  the GUI to parse SMB3 structures directly.
- Preserve the encoded SMB3 state needed for save, reload, and replay-aware
  editing.
- Offer clear seams into :mod:`foundry.game.level`, :mod:`foundry.game.gfx`,
  and low-level ROM helpers.

Non-Goals
---------

- Replace all low-level parsing performed by :mod:`smb3parse`.
- Flatten every ROM concern into one universal model type.
- Make graphics rendering own persistence or session policy.

Current State
-------------

The package currently centers on :class:`foundry.game.level.Level` and
:class:`foundry.game.level.WorldMap`, with smaller metadata bridges such as
:mod:`foundry.game.Data`, :mod:`foundry.game.ObjectDefinitions`, and
:class:`foundry.game.ObjectSet`. :mod:`foundry.game.File` owns the active ROM
file boundary, while :mod:`foundry.game.gfx` adapts graphics and palette data
for rendering rather than for persistence.

Data Flow
---------

1. :mod:`foundry.game.File` and related ROM helpers expose the active byte
   source.
2. :mod:`foundry.game.level` loaders assemble that byte-oriented data into
   level or world objects.
3. :class:`foundry.game.ObjectSet` and :mod:`foundry.game.ObjectDefinitions`
   translate SMB3 identifiers into richer editor metadata.
4. :mod:`foundry.game.gfx` consumes those model identifiers plus graphics and
   palette context to produce renderable forms.
5. Save and replay workflows query the updated model objects for serialized
   bytes or persistence-facing state.

Control Flow
------------

Most control enters this layer from the GUI or feature modules. A session loads
ROM state, constructs a level or world model, then routes edits through model
objects and supporting metadata helpers. Renderers and commands revisit the
same model objects repeatedly rather than re-decoding the ROM from scratch.

Architectural Decisions
-----------------------

- :mod:`foundry.game` is the editor's stateful model layer, not just a bag of
  parser helpers.
- Level and world ownership are separated because their encoded structures and
  editing workflows differ materially.
- Object-set and definition metadata stay explicit so renderer and model code
  can share one interpretation of SMB3 type identifiers.
- Small bridge modules such as :mod:`foundry.game.Data` remain valuable when
  they keep ROM lookup tables or compatibility shims out of heavier model
  classes.
- Graphics concerns are adjacent to, but not collapsed into, the core model so
  persistence and drawing can evolve separately.

Read This Next
--------------

- Start with :class:`foundry.game.level.Level` for in-level object, header, and
  enemy ownership.
- Read :class:`foundry.game.level.WorldMap` for overworld-specific data and
  routing.
- Continue to :class:`foundry.game.ObjectSet` and
  :mod:`foundry.game.ObjectDefinitions` when object identity or behavior looks
  wrong.
- Move into :mod:`foundry.game.gfx` when the model is correct but rendering is
  not.
- Follow :mod:`foundry.game.File` when the problem is really at the ROM
  boundary.
- Keep :doc:`../api/foundry_game` open beside this page when you need generated
  reference for the model modules named above.
