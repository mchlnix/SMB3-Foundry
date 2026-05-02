"""Manage Foundry's shared SMB3 ROM image and appended editor metadata.

This module owns the process-wide ROM state that Foundry's parsers, renderers,
and save flows operate on. ``ROM`` wraps ``smb3parse``'s lower-level ROM helper
while keeping the active bytearray, parsed iNES header, extra Foundry
``AdditionalData``, and ROM-derived global offsets synchronized.

Loading a file splits the raw bytes into the playable ROM image and the
optional metadata payload stored after ``ROM.MARKER_VALUE``. The same module
also resets graphics caches and parser globals so other subsystems observe the
new ROM consistently after a load or reload.

See Also
--------
foundry.game.additional_data.AdditionalData
    Serializer for the editor metadata block appended after ROM bytes.
foundry.game.gfx
    Graphics caches that must be invalidated when a different ROM becomes
    active.
smb3parse.util.rom.Rom
    Lower-level ROM access API that ``ROM`` extends with Foundry-specific
    lifecycle management.

Examples
--------
Load a ROM, inspect a shared property, and save it back with the appended
metadata block preserved::

    >>> from pathlib import Path
    >>> from foundry.game.File import ROM
    >>> rom_path = Path("smb3.nes")
    >>> ROM.load_from_file(rom_path)
    >>> ROM.is_loaded()
    True
    >>> rom = ROM()
    >>> isinstance(rom.header.program_banks, int)
    True
    >>> ROM.save_to_file(rom_path.with_name("smb3-copy.nes"))

Notes
-----
The example illustrates the workflow shape but is not suitable as a doctest in
the repository by default because it requires a valid SMB3 ROM on disk.
"""

from os.path import basename
from pathlib import Path

from foundry.game.additional_data import AdditionalData
from smb3parse.constants import reset_global_offsets
from smb3parse.util.rom import PRG_BANK_SIZE, INESHeader, Rom


class ROM(Rom):
    """Wrap Foundry's single active SMB3 ROM image.

    ``ROM`` keeps the loaded file, iNES header, Foundry metadata block, and
    derived parser offsets in class-level state. Instances wrap that shared
    bytearray with the lower-level ``smb3parse`` ROM API so editors, parsers,
    and renderers operate on one active ROM image.

    Parameters
    ----------
    path : Path | str | None, optional
        ROM path to load if no ROM is already active.

    Attributes
    ----------
    MARKER_VALUE : bytes
        Separator before Foundry's appended metadata block.
    PRG030_INDEX : int
        Negative bank index for the stock PRG030 bank.
    PRG031_INDEX : int
        Negative bank index for the stock PRG031 bank.
    W_INIT_OS_LIST : list[int]
        Cached world-init object-set offsets from parser routines.
    additional_data : AdditionalData
        Foundry metadata appended after the ROM bytes.
    fns_path : str
        Path to fns.
    header : INESHeader | None
        Parsed iNES header for the active ROM.
    name : str
        Basename of the active ROM path.
    path : str
        Filesystem path for the active ROM.
    rom_data : bytearray
        Active ROM bytes without Foundry's appended metadata block.
    smb3_asm_path : str
        Path to smb3 asm.

    Raises
    ------
    ValueError
        If the input data or current state is invalid.

    Examples
    --------
    Load a ROM once, then reuse lightweight ``ROM`` wrappers for shared reads::

        >>> from foundry.game.File import ROM
        >>> ROM.load_from_file("smb3.nes")
        >>> rom = ROM()
        >>> ROM.is_loaded()
        True
        >>> rom.search_bank(b"ABC", ROM.PRG031_INDEX) >= -1
        True

    ``ROM`` stores the active bytes at class scope, so later wrappers observe
    the same loaded image until another file is loaded or saved.
    """

    MARKER_VALUE = bytes("SMB3FOUNDRY", "ascii")
    PRG030_INDEX = -2
    """The index passed to search_bank to search the vanilla prg030 bank, regardless of expanded ROM"""
    PRG031_INDEX = -1
    """The index passed to search_bank to search the vanilla prg031 bank, regardless of expanded ROM"""

    rom_data = bytearray()
    header: INESHeader | None = None

    additional_data: AdditionalData

    path: str = ""
    name: str = ""

    fns_path: str = ""
    smb3_asm_path: str = ""

    W_INIT_OS_LIST: list[int] = []

    def __init__(self, path: Path | str | None = None):
        """Create a ROM API wrapper for the active ROM bytes.

        If no ROM is currently loaded, ``path`` must point to a valid file and
        will be loaded before constructing the wrapper.

        Parameters
        ----------
        path : Path | str | None, optional
            ROM path to load if no ROM is already active.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if not ROM.rom_data:
            if path is None or not Path(path).is_file():
                raise ValueError("Rom was not loaded!")

            ROM.load_from_file(path, False)

        super(ROM, self).__init__(ROM.rom_data, ROM.header)

    @staticmethod
    def get_tsa_data(object_set: int) -> bytes:
        """Returns bytes, instead of bytearray, because bytes is hashable. FIXME?

        Block rendering caches TSA data by object set, so the mutable ROM slice
        is converted to ``bytes`` for use in cache keys and shared caches.

        Parameters
        ----------
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.

        Returns
        -------
        bytes
            TSA data for the object set.
        """
        rom = ROM()

        return bytes(rom.tsa_data_for_object_set(object_set))

    @staticmethod
    def load_from_file(path: Path | str, reset_globals=True):
        """Load a ROM file and its optional Foundry metadata.

        Bytes before ``MARKER_VALUE`` are treated as the ROM image. Bytes after
        the marker are decoded as Foundry ``AdditionalData``. Loading also
        resets graphics caches so renderers read from the new ROM.

        Parameters
        ----------
        path : Path | str
            ROM file path to read.
        reset_globals : bool, optional
            Whether to reset parser global offsets before reading the file.

        Examples
        --------
        Reload the shared ROM state from disk before constructing helpers that
        read from it::

            >>> from foundry.game.File import ROM
            >>> ROM.load_from_file("smb3.nes")
            >>> ROM.is_loaded()
            True
            >>> rom = ROM()
            >>> rom.header is not None
            True
        """
        with open(path, "rb") as rom:
            data = bytearray(rom.read())

        if reset_globals:
            ROM.reset_globals()

        ROM.header = INESHeader.from_buffer_copy(data)
        ROM.path = str(path)
        ROM.name = basename(path)

        additional_data_start = data.find(ROM.MARKER_VALUE)

        if additional_data_start == -1:
            ROM.rom_data = data
            ROM.additional_data = AdditionalData(ROM())
        else:
            ROM.rom_data = data[:additional_data_start]

            additional_data_start += len(ROM.MARKER_VALUE)

            ROM.additional_data = AdditionalData.from_str(data[additional_data_start:].decode("utf-8"), ROM())

        ROM.reset_graphics()

    @staticmethod
    def reset_graphics():
        """Clear graphics caches after loading a different ROM.

        This forces palette, graphics, and block data to be read from the
        newly loaded ROM instead of reusing cached render data from a previous
        file.
        """
        # circular import with ROM
        from foundry.game.gfx import BlockCache, restore_graphics

        restore_graphics()

        BlockCache.clear_cache()

    @staticmethod
    def reload_from_file():
        """Reload ROM bytes from the active ROM path.

        The existing ``AdditionalData`` object is preserved so editor-managed
        metadata survives a raw ROM reload while the shared ROM bytearray and
        parser offsets are refreshed from the active disk path.
        """
        additional_data = ROM.additional_data

        if ROM.path:
            ROM.load_from_file(ROM.path, reset_globals=False)

        ROM.additional_data = additional_data

    @staticmethod
    def save_to_file(path: Path | str, set_new_path=True):
        """Write the active ROM and Foundry metadata to disk.

        The ROM bytes are written first. If additional data exists, Foundry's
        marker and serialized metadata are appended after the ROM image.

        Parameters
        ----------
        path : Path | str
            Output file path.
        set_new_path : bool, optional
            Whether to make ``path`` the active ROM path after saving.
        """
        Path(path).open("wb").write(bytearray(ROM.rom_data))

        if ROM.additional_data:
            with open(path, "ab") as f:
                f.write(ROM.MARKER_VALUE)
                f.write(str(ROM.additional_data).encode("utf-8"))

        if set_new_path:
            ROM.path = str(path)
            ROM.name = basename(path)

    @staticmethod
    def is_loaded() -> bool:
        """Report whether Foundry has an active ROM path.

        This is the lightweight guard many UI and parsing paths use before they
        assume ROM-backed data and file reload operations are available.

        Returns
        -------
        bool
            ``True`` when a ROM has been loaded from or saved to a path.
        """
        return bool(ROM.path)

    def search_bank(self, needle: bytes, bank: int) -> int:
        """Search a specific bank given a zero-based bank index.
        If negative values are used, -1 is the last bank, -2 is the second-to-last bank, etc.

        This keeps PRG bank lookup logic centralized for routines that need to
        locate stock tables even when a ROM has been expanded. The returned
        offset is in global ROM coordinates, so callers can pass it straight
        into other ROM reads or pointer calculations.

        Parameters
        ----------
        needle : bytes
            Byte sequence to find.
        bank : int
            PRG bank index; negative values count from the end.

        Returns
        -------
        int
            Absolute ROM offset of the match, or ``-1`` when not found.
        """
        num_prg_banks = ROM().prg_banks
        # Mod here for negative banks (negative indices index from the end)
        bank = bank % num_prg_banks

        if bank not in range(num_prg_banks):
            return -1

        start = bank * PRG_BANK_SIZE
        return self.find(needle, start, start + PRG_BANK_SIZE)

    @classmethod
    def reset_globals(cls):
        """Reset Foundry and smb3parse global ROM-derived state.

        This is used before loading a fresh ROM so cached assembly paths and
        parser offsets do not leak across files.
        """
        ROM.fns_path = ROM.smb3_asm_path = ""
        reset_global_offsets()
