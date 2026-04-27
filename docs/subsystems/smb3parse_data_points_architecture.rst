SMB3Parse Data Points Architecture
==================================

Problem and Context
-------------------

The :mod:`smb3parse.data_points` family exists to model ROM tables as mutable,
address-aware records rather than anonymous offsets. Foundry and parser tools
need this layer when they want to inspect or rewrite pointer-table entries,
world-map coordinates, sprite metadata, or fortress effects while keeping the
serialized storage format visible and reversible.

Goals
-----

* Represent ROM-backed table entries as small objects with stable addresses.
* Keep decoded values synchronized with the bytes or nibbles they came from.
* Provide reusable position and indexed-entry helpers for table families.
* Expose world-map and level-pointer records in a form later level loaders can
  consume directly.

Non-Goals
---------

* Parsing full playable levels or enemy streams.
* Rendering world maps or editor widgets.
* Hiding all ROM layout details behind opaque abstractions.
* Replacing the higher-level world-map and level models in
  :mod:`smb3parse.levels`.

Current State
-------------

The package currently centers on a few ROM-table families:

* :mod:`smb3parse.data_points.util` provides the base data-point lifecycle and
  shared helpers for indexed and positioned records.
* :mod:`smb3parse.data_points.world_map_data` owns the table starts and shared
  world-level pointer metadata for one overworld.
* :mod:`smb3parse.data_points.level_pointer_data` models individual playable
  stage pointers within those world tables.
* :mod:`smb3parse.data_points.sprite_data`,
  :mod:`smb3parse.data_points.pipe_data`, and
  :mod:`smb3parse.data_points.fortress_fx_data` cover other ROM-backed table
  families that Foundry reads or edits.

The package is intentionally close to the serialized ROM shape. Most classes
calculate addresses first and then load or write back values through a common
data-point lifecycle.

Data Flow
---------

The typical data path is:

1. A higher-level caller chooses the owning world or table family.
2. A data-point object computes the concrete ROM addresses for one entry.
3. The object reads the serialized values from the ROM and normalizes them
   into attributes such as screen, x, y, object set, or pointer offsets.
4. Downstream code mutates those normalized fields.
5. The same data-point object writes the values back into the original ROM
   layout when persistence is requested.

Control Flow
------------

The control flow usually follows the
:class:`smb3parse.data_points.util.DataPoint` lifecycle:

1. Construction records the owning ROM and any table-specific context.
2. :meth:`~smb3parse.data_points.util.DataPoint.calculate_addresses` maps an
   entry index or world-level base address to concrete ROM positions.
3. :meth:`~smb3parse.data_points.util.DataPoint.read_values` loads the current
   table state.
4. Callers inspect or mutate the normalized attributes.
5. :meth:`~smb3parse.data_points.util.DataPoint.write_back` pushes those
   changes into ROM storage.

That flow is repeated across table families so higher-level tooling can treat
many ROM-backed records the same way even when SMB3 stores them differently.

Architectural Decisions
-----------------------

* Address calculation and value loading are explicit steps because ROM tables
  often split one logical record across multiple lists or nibble-packed bytes.
* World-map pointer ownership is split between table-level objects and
  per-entry objects so callers can preserve both shared table context and
  entry-local mutation logic.
* The package keeps storage-shape details visible instead of normalizing
  everything into opaque models; maintainers often need to reason about exact
  ROM addresses.
* Data points stop at table-entry semantics and hand off richer layout or
  parsing behavior to :mod:`smb3parse.levels` and :mod:`smb3parse.util.parser`.

Read This Next
--------------

For the next layer above these ROM-table models, read:

* :mod:`smb3parse.levels.world_map` for overworld models that consume world-map
  pointer data.
* :mod:`smb3parse.levels.level` for the stage model that consumes decoded level
  and enemy addresses.
* :mod:`smb3parse.util.parser` when you need the package family that walks from
  pointer tables into parsed object and enemy records.
