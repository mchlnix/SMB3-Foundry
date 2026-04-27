SMB3Parse Objects Architecture
==============================

Problem and Context
-------------------

The :mod:`smb3parse.objects` family is the layer that turns SMB3's compact
object bytes into stable object identities, coordinates, and object-set-aware
metadata. Higher-level parsers need this package so they can talk about "the
decoded object at this level position" instead of repeatedly unpacking raw
bytes, domain values, and bank-specific lookup rules.

Goals
-----

* Define a shared decoded-object contract through
  :class:`smb3parse.objects.InLevelObject`.
* Resolve object-set metadata and bank offsets through
  :class:`smb3parse.objects.object_set.ObjectSet`.
* Decode terrain object records and enemy or item records through the concrete
  object modules.
* Keep the object layer small enough that parser and editor code can reuse it
  without importing GUI concerns.

Non-Goals
---------

* Drawing editor objects or managing Foundry palettes.
* Owning world-map pointer tables.
* Walking the full ROM graph to discover related levels.
* Replacing the parser-side aggregate records in
  :mod:`smb3parse.util.parser`.

Current State
-------------

The package is organized around one metadata helper plus concrete decoded
object families:

* :mod:`smb3parse.objects` defines the shared in-level object contract and the
  common numeric bounds used during decoding.
* :mod:`smb3parse.objects.object_set` translates an object-set number into the
  ROM bank offset, ending graphic family, and display name needed by later
  parsers.
* :mod:`smb3parse.objects.level_object` decodes normal level-object records.
* :mod:`smb3parse.objects.enemy_item` decodes enemy and item records that live
  in the separate enemy stream.

The family is parser-facing rather than editor-facing. It preserves raw bytes
and normalized fields, but it does not decide how those objects should be
rendered in Foundry.

Data Flow
---------

The normal data path is:

1. A level header or caller supplies an object-set number.
2. :class:`smb3parse.objects.object_set.ObjectSet` resolves bank metadata for
   that number.
3. Concrete object decoders read raw bytes from the relevant level or enemy
   stream.
4. Those decoders populate the shared fields exposed by
   :class:`smb3parse.objects.InLevelObject`, such as
   :attr:`smb3parse.objects.InLevelObject.id`,
   :attr:`smb3parse.objects.InLevelObject.domain`,
   :attr:`smb3parse.objects.InLevelObject.x`,
   :attr:`smb3parse.objects.InLevelObject.y`, and optional length state.
5. Parser-side or editor-side consumers read those normalized fields instead
   of revisiting the original byte layout.

Control Flow
------------

Control usually starts outside this package. A caller such as
:mod:`smb3parse.levels.level` or :mod:`smb3parse.util.parser.object` chooses an
object set and the relevant byte stream, then delegates decoding into the
appropriate object module. After that point, control becomes mostly local:
property access, validation helpers, and small decoder-specific decisions.

Architectural Decisions
-----------------------

* :class:`smb3parse.objects.object_set.ObjectSet` is the single translation
  point between numeric object-set ids and the ROM-bank metadata that later
  parsing needs.
* The base object contract stores raw bytes alongside normalized fields so
  consumers can both inspect decoded state and reconstruct serialized length.
* Enemy or item decoding stays separate from normal level-object decoding
  because SMB3 stores those records in a distinct stream with different rules.
* The package does not absorb Foundry-specific editor abstractions; that keeps
  it reusable by parser utilities and tests.

Read This Next
--------------

Follow these routes depending on the question you are chasing:

* For level models that own the object-set selection, read
  :mod:`smb3parse.levels.level`.
* For parser-side aggregate records that collect decoded objects and enemies,
  read :mod:`smb3parse.util.parser.object` and
  :mod:`smb3parse.util.parser.level`.
* For the higher-level Sphinx surface that indexes this package family, read
  :doc:`../api/smb3parse`.
