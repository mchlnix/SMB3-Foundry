"""Read and write SMB3 ROM bytes through normalized PRG addresses.

This module provides the low-level byte access layer used by parser, level,
and world-model code that reads SMB3 data out of an iNES ROM image. The
``INESHeader`` structure exposes the cartridge header fields needed to reason
about PRG and CHR size, while ``Rom`` normalizes vanilla PRG offsets so higher
level code can keep using stable SMB3 addresses even when the ROM has been
expanded. Parser modules, data-point wrappers, and editor-facing loaders read
raw bytes here first, then pass normalized offsets and decoded slices onward to
table readers, object decoders, and save-back routines.

See Also
--------
smb3parse.util.parser.level : Parses level records by reading normalized ROM data.
smb3parse.data_points.util : Wraps ROM byte access in typed data-point helpers.
"""

import pathlib
from ctypes import Structure, c_char, c_ubyte
from os import PathLike
from pathlib import Path

from smb3parse.constants import BASE_OFFSET, WORLD_MAP_TSA_INDEX, Constants
from smb3parse.types import NormalizedAddress
from smb3parse.util import little_endian

TSA_TABLE_SIZE = 0x400

PRG_BANK_SIZE = 0x2000


class INESHeader(Structure):
    """Store the 16-byte iNES header copied from the ROM image.

    ``Rom`` uses this structure to derive PRG sizing rules before any higher
    level parser starts converting SMB3 offsets into file offsets.

    Attributes
    ----------
    magic : bytes
        Four-byte iNES signature copied directly from the ROM header.
    prg_units : int
        Number of 16 KiB PRG units declared by the cartridge header.
    chr_units : int
        Number of 8 KiB CHR units declared by the cartridge header.
    flags6 : bytes
        Mapper and mirroring control bits from the iNES header.
    unused_flags : bytes
        Remaining legacy header bytes preserved for round-tripping.
    unused_pad : bytes
        Final padding bytes in the 16-byte iNES header.
    PRG_UNIT_SIZE : int
        Size in bytes of one PRG unit declared by the iNES header.
    CHR_UNIT_SIZE : int
        Size in bytes of one CHR unit declared by the iNES header.
    LENGTH : int
        Total header length in bytes.
    """

    _fields_ = [
        ("magic", c_char * 4),
        ("prg_units", c_ubyte),
        ("chr_units", c_ubyte),
        ("flags6", c_char),
        ("unused_flags", c_char * 4),
        ("unused_pad", c_char * 5),
    ]
    PRG_UNIT_SIZE = 0x4000
    CHR_UNIT_SIZE = 0x2000
    LENGTH = 0x10

    @property
    def prg_size(self):
        """Compute the PRG payload size implied by the header.

        ``Rom`` reads this value during normalization setup to decide whether
        logical SMB3 addresses that target the last vanilla PRG banks must be
        shifted forward before later table reads touch the underlying file
        bytes. The result therefore feeds :meth:`Rom.prg_normalize`, which all
        later byte, pointer, nibble, and table readers depend on. The property
        does not mutate any header state; it reports the fixed PRG capacity
        copied from the 16-byte iNES header.

        Returns
        -------
        int
            Total PRG size in bytes.
        """
        return self.prg_units * INESHeader.PRG_UNIT_SIZE

    @property
    def chr_size(self):
        """Compute the CHR payload size implied by the header.

        ``Rom`` and higher-level graphics tooling read this during cartridge
        inspection before any later parser decides whether CHR-backed tile or
        sprite resources are available. Nothing mutates the value; it is the
        public handoff from the copied header state to later graphics-capacity
        checks, and it stays paired with :attr:`prg_size` whenever loader code
        reports what data families the ROM can satisfy.

        Returns
        -------
        int
            Total CHR size in bytes.
        """
        return self.chr_units * INESHeader.CHR_UNIT_SIZE


class Rom:
    """Expose normalized byte-level access to an SMB3 ROM image.

    The rest of ``smb3parse`` mostly works in terms of SMB3 PRG offsets rather
    than raw file offsets. ``Rom`` keeps that contract stable by translating
    addresses that point into the last vanilla PRG banks so parsers, typed data
    points, and save-back code all keep targeting the same logical structures
    after the cartridge image has been expanded.

    Parameters
    ----------
    rom_data : bytearray
        Full ROM image, including the 16-byte iNES header.
    header : INESHeader or None, optional
        Parsed iNES header to reuse. When omitted, the header is copied from
        the first 16 bytes of ``rom_data``.

    Attributes
    ----------
    VANILLA_PRG_SIZE : int
        Total PRG size in bytes for an unexpanded SMB3 ROM.

    Notes
    -----
    Expanded SMB3 ROMs insert extra PRG data before the last two vanilla PRG
    banks. Normalization keeps call sites free to use the same bank-30 and
    bank-31 offsets regardless of whether the ROM has been expanded.
    """

    VANILLA_PRG_SIZE = 0x40000

    def __init__(self, rom_data: bytearray, header: INESHeader | None = None):
        """Create a ROM access wrapper around the raw image bytes.

        Construction captures the shared bytearray in ``self._data``, resolves
        the iNES header into ``self._header``, and fixes the normalization
        policy that every later accessor in this class reuses. After this
        point, :meth:`read`, :meth:`int`, :meth:`little_endian`,
        :meth:`tsa_data_for_object_set`, and the write helpers all operate over
        one consistent in-memory ROM image while callers continue to speak in
        SMB3 logical addresses. The constructor is the only place where this
        wrapper establishes those two backing state objects.

        Parameters
        ----------
        rom_data : bytearray
            Full ROM contents, including the iNES header.
        header : INESHeader or None, optional
            Parsed header to reuse for repeated wrappers over the same data.
            When ``None``, the header is parsed from ``rom_data``.
        """
        self._data = rom_data

        if header is None:
            header = INESHeader.from_buffer_copy(bytes(rom_data))

        self._header = header

    @property
    def prg_units(self):
        """Expose the header PRG unit count to ROM clients.

        Higher-level parsers use this when they need cartridge capacity data
        without reaching into the private header structure while deciding how
        later normalized reads and bank calculations fit inside the available
        PRG image. In practice it is the public handoff from constructor-owned
        header state into the rest of the ROM access lifecycle: once
        :meth:`__init__` captures ``self._header``, loaders inspect the 16 KiB
        unit count here, :attr:`prg_banks` converts it into the 8 KiB bank
        model SMB3 code expects, and later read paths reuse those bank counts
        while routing logical offsets through :meth:`prg_normalize`. Nothing is
        recomputed or mutated here; the property forwards the stored header
        field that downstream bank math and capacity checks consult before
        later parsers choose addresses and move ROM bytes through normalized
        read helpers.

        Returns
        -------
        int
            Count of 16 KiB PRG units in the cartridge image.
        """
        return self._header.prg_units

    @property
    def prg_banks(self):
        """Expose the number of addressable 8 KiB PRG banks.

        SMB3 bank calculations use 8 KiB pages, so this property bridges the
        iNES header unit count into the bank size used by parser code when it
        calculates which normalized offsets and table lookups belong to a later
        banked read. It is the last conversion step before higher-level code
        chooses a PRG bank and feeds the resulting offset back into
        :meth:`read` or related helpers, again without mutating ROM state.

        Returns
        -------
        int
            Count of 8 KiB banks derived from :attr:`prg_units`.
        """
        return self.prg_units * 2

    def prg_normalize(self, offset: int | NormalizedAddress) -> NormalizedAddress:
        """Translate a vanilla SMB3 offset into this ROM's physical PRG layout.

        Every public read, write, and search helper routes through this
        translation step before touching the bytearray, which keeps parser and
        save-back code aligned on the same logical SMB3 address map.

        Parameters
        ----------
        offset : int or NormalizedAddress
            SMB3 PRG offset or already-normalized file offset.

        Returns
        -------
        NormalizedAddress
            File offset that points at the same logical SMB3 data in this ROM.

        Notes
        -----
        SMB3 expansion inserts data between vanilla PRG banks 29 and 30. Any
        address that targets the last two vanilla banks must be shifted forward
        by the number of inserted bytes so parsing and patching keep hitting the
        bank SMB3 expects.
        """
        if type(offset) == NormalizedAddress:  # noqa: E721  isinstance doesn't work with type alias
            return offset

        # data in expanded Roms is inserted between PRG29 and PRG30
        # (0-indexed); so any offset, that goes beyond PRG29 needs
        # to be adjusted by adding however much data was inserted
        if offset < (BASE_OFFSET + (30 * PRG_BANK_SIZE)):
            return NormalizedAddress(offset)

        # we need to normalize this bank 30 or 31 or CHR
        # offset to the correct bank based on PRG size
        no_bytes_added_to_rom = self._header.prg_size - Rom.VANILLA_PRG_SIZE

        return NormalizedAddress(offset + no_bytes_added_to_rom)

    def tsa_data_for_object_set(self, object_set: int) -> bytearray:
        """Load the 1 KiB TSA table used by one object set.

        This is the bridge from SMB3 object-set metadata to the metatile table
        consumed by object rendering and object decoding code after the object
        set index has already been chosen by a higher-level table reader. The
        method turns that logical object-set choice into the TSA index, bank
        start address, and final byte slice that later metatile decoders and
        renderers consume. The workflow is: take the caller's object-set id,
        read the TSA index table, substitute the hard-coded overworld bank when
        object set ``0`` is targeting world-map tiles instead of ordinary level
        tiles, and then fetch the final 1 KiB byte block through :meth:`read`
        so ROM expansion normalization still applies. It does not decode the
        returned bytes itself; it hands the raw TSA payload to later object-set
        consumers.

        Parameters
        ----------
        object_set : int
            SMB3 object-set index whose metatile table should be read.

        Returns
        -------
        bytearray
            Raw TSA bytes for the object set that downstream metatile readers
            will decode.

        Notes
        -----
        The world map does not use the same page-A000 lookup path as ordinary
        level object sets, so object set ``0`` is redirected to the hard-coded
        world-map TSA bank instead of the regular per-tileset table.
        """
        # TSA_OS_LIST offset value assumes vanilla ROM size, so normalize it

        tsa_index = self.int(Constants.TSA_OS_LIST + object_set)

        if object_set == 0:
            # Note that for the World Map, PAGE_A000 is set to bank 11, but
            # the actual drawing of the map and the map tiles are defined
            # in bank 12. prg030.asm handles swapping hard-coded to bank 12
            # and drawing the initial map via Map_Reload_with_Completions.
            # Therefore, the PAGE_A000_ByTileset doesn't have the TSA data for
            # the map tiles.
            tsa_index = WORLD_MAP_TSA_INDEX

        # INES header size + (bank with tsa data * sizeof(bank))
        tsa_start = BASE_OFFSET + tsa_index * PRG_BANK_SIZE

        return self.read(tsa_start, TSA_TABLE_SIZE)

    def little_endian(self, offset: int | NormalizedAddress) -> int:
        """Read a two-byte pointer-sized value from the ROM.

        Data-point classes use this helper when SMB3 stores addresses and table
        entries as little-endian byte pairs that then drive later object, level,
        or world parsing after the bytes have been normalized, sliced, and
        reassembled into one integer address. Callers typically feed the
        returned integer straight into later ROM reads or typed address
        properties. The method itself delegates the byte fetch to :meth:`read`
        and only performs the two-byte integer decode, so address normalization
        and byte extraction stay in the shared read path. In practice this is
        the standard raw-bytes-to-pointer handoff for structured readers:
        world-map, level-pointer, and parser data-point classes call it to turn
        one stored pointer pair into the next absolute or bank-relative address
        that their decode workflow follows.

        Parameters
        ----------
        offset : int or NormalizedAddress
            Address of the low byte.

        Returns
        -------
        int
            Decoded 16-bit integer.
        """
        return little_endian(self.read(offset, 2))

    def write_little_endian(self, offset: int | NormalizedAddress, integer: int):
        """Write a two-byte little-endian value back into the ROM.

        This keeps save-back code aligned with the same pointer encoding that
        :meth:`little_endian` decodes during parsing, so edited pointer tables
        still feed later ROM consumers correctly.

        Parameters
        ----------
        offset : int or NormalizedAddress
            Address where the low byte should be written.
        integer : int
            Value to store in two little-endian bytes.
        """
        right_byte = (integer & 0xFF00) >> 8
        left_byte = integer & 0x00FF

        self.write(offset, bytes([left_byte, right_byte]))

    def read(self, offset: int | NormalizedAddress, length: int) -> bytearray:
        """Read bytes from a logical SMB3 offset.

        Callers hand this method SMB3-facing offsets; the method normalizes the
        address and then slices the underlying ROM image that later parser
        stages interpret as higher-level records, pointer tables, or packed
        flags. It is the public entry point for the raw-byte -> normalized-
        address -> decoded-structure pipeline used across ``smb3parse``. The
        narrower helpers :meth:`int`, :meth:`little_endian`, :meth:`nibbles`,
        and :meth:`tsa_data_for_object_set` all build on this step. State does
        not change here; the method translates the caller's logical address and
        delegates the actual slice to :meth:`_read`.

        Parameters
        ----------
        offset : int or NormalizedAddress
            Logical ROM offset to read.
        length : int
            Number of bytes to return.

        Returns
        -------
        bytearray
            Slice of ROM data starting at the normalized offset.
        """
        offset = self.prg_normalize(offset)

        return self._read(offset, length)

    def _read(self, offset: NormalizedAddress, length: int) -> bytearray:
        """Read bytes from an already-normalized file offset.

        This is the raw bytearray access step once PRG expansion adjustments
        have already been resolved, letting the public helpers share one common
        low-level read primitive before callers decode the returned slice into
        typed SMB3 data. Keeping this step separate lets public helpers decide
        which logical address contract they expose without duplicating the final
        file-slice operation. It never performs additional normalization; that
        boundary stays in :meth:`read` and the other public logical-address
        helpers.

        Parameters
        ----------
        offset : NormalizedAddress
            File offset that has already been normalized for expansion.
        length : int
            Number of bytes to return.

        Returns
        -------
        bytearray
            Slice of the stored ROM bytearray.
        """
        return self._data[offset : offset + length]

    def read_until(self, offset: int | NormalizedAddress, delimiter: bytes | int):
        """Read bytes until a delimiter byte sequence is encountered.

        This helper combines :meth:`find` and :meth:`read` for variable-length
        SMB3 byte runs that end at a terminator value before a later parser
        converts the slice into structured data such as names or byte streams.
        It preserves the same logical-offset contract as :meth:`read` while
        adding the delimiter search step needed for variable-length records.

        Parameters
        ----------
        offset : int or NormalizedAddress
            Address where the scan should begin.
        delimiter : bytes or int
            Byte sequence, or single byte value, that terminates the read.

        Returns
        -------
        bytearray
            Bytes between ``offset`` and the first delimiter occurrence.
        """
        if isinstance(delimiter, int):
            delimiter = bytes([delimiter])

        end = self.find(delimiter, offset)

        return self.read(offset, end - offset)

    def write(self, offset: int | NormalizedAddress, data: bytes | int):
        """Write bytes to a logical SMB3 offset.

        Save-back code uses this entry point when it has logical SMB3 offsets
        and needs normalization handled before mutating the ROM bytearray that
        later save operations will persist unchanged.

        Parameters
        ----------
        offset : int or NormalizedAddress
            Logical ROM offset to overwrite.
        data : bytes or int
            Byte sequence, or single byte value, to write.

        Returns
        -------
        None
            This method updates the stored bytearray in place.
        """
        if isinstance(data, int):
            data = bytes([data])

        offset = self.prg_normalize(offset)

        return self._write(offset, data)

    def _write(self, offset: NormalizedAddress, data: bytes):
        """Write bytes to an already-normalized file offset.

        This is the final in-place mutation step after callers have resolved
        any expansion-dependent address translation, so all writes converge on
        one bytearray splice operation before :meth:`save_to` persists the ROM.

        Parameters
        ----------
        offset : NormalizedAddress
            File offset that already accounts for ROM expansion.
        data : bytes
            Raw bytes to splice into the ROM image.
        """
        self._data[offset : offset + len(data)] = data

    def find(
        self,
        needle: bytes | int,
        start: int | NormalizedAddress = NormalizedAddress(0),
        end: int | NormalizedAddress = NormalizedAddress(-1),
    ) -> NormalizedAddress:
        """Find a byte sequence within the ROM.

        Parser helpers use this when they need to scan the cartridge image from
        logical SMB3 offsets and then feed the located address into a later
        decode step or variable-length read. The public method keeps scan
        boundaries in SMB3 logical coordinates until the search window has been
        normalized into concrete file offsets.

        Parameters
        ----------
        needle : bytes or int
            Byte sequence, or single byte value, to search for.
        start : int or NormalizedAddress, optional
            Logical offset where the search begins.
        end : int or NormalizedAddress, optional
            Logical offset where the search stops. ``-1`` searches to EOF.

        Returns
        -------
        NormalizedAddress
            Normalized offset of the first match, or ``-1`` when not found.
        """
        if isinstance(needle, int):
            needle = bytes([needle])

        start = self.prg_normalize(start)

        if end == -1:
            end = NormalizedAddress(len(self._data))

        end = self.prg_normalize(end)

        return self._find(needle, start, end)

    def _find(self, needle: bytes, start: NormalizedAddress, end: NormalizedAddress) -> NormalizedAddress:
        """Find a byte sequence between normalized file offsets.

        This is the raw bytearray search step once logical offsets have already
        been converted into concrete file boundaries for a downstream parser or
        patching workflow.

        Parameters
        ----------
        needle : bytes
            Byte sequence to search for.
        start : NormalizedAddress
            First file offset to inspect.
        end : NormalizedAddress
            Exclusive upper bound for the search.

        Returns
        -------
        NormalizedAddress
            Normalized offset of the first match, or ``-1`` when not found.
        """
        return NormalizedAddress(self._data.find(needle, start, end))

    def nibbles(self, offset: int | NormalizedAddress) -> tuple[int, int]:
        """Read one byte and split it into high and low nibbles.

        SMB3 packs many small flags and indices into half-byte fields, so this
        helper feeds parser code that decodes those compact formats into later
        typed properties after a single byte has been fetched from the ROM. It
        is the byte-to-field bridge for data-point accessors that expose packed
        ROM state as separate logical values.

        Parameters
        ----------
        offset : int or NormalizedAddress
            Address of the byte to decode.

        Returns
        -------
        tuple[int, int]
            Two-element tuple of ``(high_nibble, low_nibble)``.
        """
        byte = self.int(offset)

        high_nibble = byte >> 4
        low_nibble = byte & 0x0F

        return high_nibble, low_nibble

    def write_nibbles(self, offset: int | NormalizedAddress, high_nibble: int, low_nibble: int = 0):
        """Write a byte assembled from two 4-bit values.

        This is the inverse of :meth:`nibbles` for save-back code that updates
        packed SMB3 fields without manually rebuilding the containing byte that
        later serialization writes back to disk.

        Parameters
        ----------
        offset : int or NormalizedAddress
            Address of the byte to overwrite.
        high_nibble : int
            Upper four bits to store.
        low_nibble : int, optional
            Lower four bits to store.

        Raises
        ------
        ValueError
            If either nibble is larger than ``0x0F``.
        """
        if any(nibble > 0x0F for nibble in [high_nibble, low_nibble]):
            raise ValueError(f"{high_nibble=} or {low_nibble=} was larger than 0x0F.")

        byte = (high_nibble << 4) + low_nibble

        self.write(offset, byte)

    @staticmethod
    def from_file(path: PathLike):
        """Load a ROM image from disk.

        This factory is the normal entry point for tools that begin with a ROM
        path rather than an already-loaded bytearray and need the normalization
        policy initialized immediately before parser or editor code starts
        reading tables through :class:`Rom`. It collapses file I/O and wrapper
        setup into one step so downstream code enters the normalized ROM view
        immediately and can hand the returned instance directly to parser,
        world-model, or editor loaders. Its whole job is to materialize the
        shared bytearray and pass it into :class:`Rom` construction, which then
        establishes the reusable header and normalization state for all later
        reads and writes.

        Parameters
        ----------
        path : os.PathLike
            Filesystem path to the ROM image.

        Returns
        -------
        Rom
            New ROM wrapper around the file contents.
        """
        return Rom(bytearray(pathlib.Path(path).read_bytes()))

    def save_to(self, path: PathLike):
        """Write the ROM image back to disk.

        The full in-memory image, including the iNES header, is emitted so
        later parser or editor runs see the same normalized layout.

        Parameters
        ----------
        path : os.PathLike
            Destination path for the full ROM byte stream.
        """
        Path(path).open("wb").write(self._data)

    def int(self, offset: int | NormalizedAddress) -> int:
        """Read a single ROM byte as an integer value.

        This is the smallest convenience read and underpins helpers that decode
        nibble fields, pointer tables, and one-byte SMB3 flags before higher
        level code turns them into typed structures or chooses a later ROM
        lookup path. In practice it is the one-byte counterpart to
        :meth:`little_endian`, feeding accessor properties that promote raw
        ROM bytes into parser-facing integers. Many data-point getters stop at
        this method when the stored byte already is the final logical value.
        Like the other public readers, it delegates the actual byte fetch to
        :meth:`read` and only performs the integer extraction step locally, so
        higher-level byte accessors all reuse the same normalization boundary.

        Parameters
        ----------
        offset : int or NormalizedAddress
            Address of the byte to read.

        Returns
        -------
        int
            Unsigned byte value stored at ``offset``.
        """
        read_bytes = self.read(offset, 1)

        return read_bytes[0]
