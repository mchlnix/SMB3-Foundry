ROM Data and Persistence
========================

Start here for ROM-backed structures, editor-only metadata, and features that
preserve or rebuild state across save, reload, and migration boundaries.

- :mod:`foundry.game.additional_data` persists editor-managed metadata that
  does not live directly in the ROM streams.
- :mod:`foundry.game.Data` is one of the remaining low-level bridges between
  raw ROM payloads and richer editor-facing level objects, and it is therefore
  part of the persistence story even though it is small.
- :mod:`foundry.game.ObjectDefinitions` and :mod:`foundry.game.ObjectSet` bridge
  ROM identifiers, richer object-definition tables, and renderer-facing
  metadata.
- :mod:`foundry.features.rom_reload` preserves editor workflows while
  ROM-backed bytes are reloaded or accepted from disk.
- :mod:`foundry.game.File` and related modules own low-level ROM file
  boundaries.
- :mod:`smb3parse.util.rom` owns the package-level ROM reader and writer
  helpers that normalize PRG-bank addresses, expose byte and nibble access, and
  preserve the iNES header boundary while other layers decode or rewrite SMB3
  structures.
- :mod:`smb3parse._default_constants` and :mod:`smb3parse.constants` stage the
  symbol-address bootstrap that decides which ROM label set later pointer and
  parser code will read from.
- :mod:`smb3parse.data_points` and :mod:`smb3parse.util.parser` document the
  ROM tables, address calculations, and lookup helpers that feed both Foundry
  and Scribe before editor code stages those values for save, reload, or
  export.

Read this next:
:doc:`/subsystems/foundry_features_architecture`,
:doc:`/subsystems/smb3parse_data_points_architecture`,
:doc:`/subsystems/smb3parse_parser_architecture`
