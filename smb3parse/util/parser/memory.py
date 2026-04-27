"""Model the parser's CPU-visible view of SMB3 PRG memory.

This module provides :class:`NESMemory`, a list-backed memory image that loads
selected PRG banks into the address windows the parser expects to inspect.
Parser helpers read and write this object as though they were traversing a
subset of the NES CPU address space while observer callbacks record reads and
writes around important addresses.

See Also
--------
smb3parse.util.rom.Rom
    Supplies the raw PRG bank bytes that populate the parser memory window.
smb3parse.util.parser.constants
    Defines mapper-facing addresses that the parser treats specially.
"""

from typing import Callable

from smb3parse.constants import BASE_OFFSET
from smb3parse.util.parser.constants import (
    MEM_Screen_Start_AddressH,
    MEM_Screen_Start_AddressL,
)
from smb3parse.util.rom import PRG_BANK_SIZE, Rom


class NESMemory(list):
    """Expose a banked ROM view through NES CPU-style addresses.

    The parser treats this object like a 64 KiB memory map whose switchable
    PRG windows can be reloaded as different subsystems inspect worlds, level
    headers, or object streams. Read and write observers let callers monitor
    address activity without changing the parser code that consumes the memory
    image directly.

    Parameters
    ----------
    backing_list : list
        Mutable 64 KiB backing storage that receives PRG bank bytes and later
        parser-side writes.
    rom : smb3parse.util.rom.Rom
        ROM reader that supplies PRG bank contents for the switchable windows.

    Attributes
    ----------
    rom : smb3parse.util.rom.Rom
        Source ROM used whenever the parser remaps a PRG bank into the memory
        image.
    _read_observers : dict[range, Callable]
        Callbacks keyed by address ranges that should be notified after reads.
    _write_observers : dict[range, Callable]
        Callbacks keyed by address ranges that should be notified before writes.

    Notes
    -----
    Construction preloads the last two PRG banks into the same fixed windows
    SMB3 uses for its always-available late-ROM code. Parser code can then swap
    the middle windows as it follows level and world metadata.
    """

    def __init__(self, backing_list: list, rom: Rom):
        """Initialize the parser memory image and fixed PRG windows.

        This constructor turns a raw 64 KiB list into the parser's live view of
        NES CPU memory. Later level and world parsers rely on that preloaded
        state so they can follow pointers through the same fixed and switchable
        bank layout that SMB3 code expects.

        Parameters
        ----------
        backing_list : list
            Mutable address space that this instance wraps and mutates in place.
        rom : smb3parse.util.rom.Rom
            ROM reader that exposes the PRG bank count and byte-reading API.

        Notes
        -----
        The parser starts from a CPU-style memory view instead of raw file
        offsets because later helpers read jump tables, pointers, and object
        data through NES addresses. Construction therefore installs the final
        two PRG banks into the fixed windows first, then leaves the switchable
        0xA000 and 0xC000 regions ready for later remapping.
        """
        super(NESMemory, self).__init__(backing_list)

        self.rom = rom

        self._read_observers: dict[range, Callable] = {}
        self._write_observers: dict[range, Callable] = {}

        last_prg_index = rom.prg_banks - 1

        # load second to last PRG (PRG_30 in the vanilla rom) into 0x8000 - 0x9FFF
        self._load_bank(last_prg_index - 1, 0x8000)

        # load last PRG (PRG_31 in the vanilla rom) into 0xE000 - 0xFFFF
        self._load_bank(last_prg_index, 0xE000)

    def load_a000_page(self, prg_index: int):
        """Map a PRG bank into the 0xA000-0xBFFF switchable window.

        Parameters
        ----------
        prg_index : int
            Zero-based PRG bank index to expose through the parser's A000 page.
        """
        self._load_bank(prg_index, 0xA000)

    def load_c000_page(self, prg_index: int):
        """Map a PRG bank into the 0xC000-0xDFFF switchable window.

        Parameters
        ----------
        prg_index : int
            Zero-based PRG bank index to expose through the parser's C000 page.
        """
        self._load_bank(prg_index, 0xC000)

    def _load_bank(self, prg_index: int, offset: int):
        """Copy one PRG bank from ROM into a CPU-visible memory window.

        The parser uses this helper whenever a discovery step changes which ROM
        bank should appear in one of the switchable address ranges. Keeping the
        remap logic here ensures both startup and later page swaps preserve the
        same ROM-offset-to-CPU-address translation.

        Parameters
        ----------
        prg_index : int
            Zero-based PRG bank index inside the ROM image.
        offset : int
            CPU address where the 8 KiB bank window begins.
        """
        prg_bank_position = BASE_OFFSET + prg_index * PRG_BANK_SIZE

        self[offset : offset + PRG_BANK_SIZE] = self.rom.read(prg_bank_position, PRG_BANK_SIZE)

    def add_read_observer(self, address_range: range, callback: Callable):
        """Register a callback for reads inside an address range.

        Observers let higher-level tooling trace parser activity around
        important addresses without threading extra bookkeeping through the code
        that consumes this memory image directly. Storing the callback in
        ``_read_observers`` changes the behavior of every later matching read,
        because :meth:`__getitem__` will publish the resolved byte through this
        registration before returning it to parser code.

        Parameters
        ----------
        address_range : range
            CPU-address interval to monitor.
        callback : Callable
            Observer invoked with ``(address, value)`` after a matching read.

        Notes
        -----
        Registration changes every later matching read that flows through
        :meth:`__getitem__`. Parser code still reads memory exactly the same
        way, but matching addresses now also publish the resolved byte to the
        observer, which is how higher-level tracing code watches level-load and
        pointer-following activity without forking the parser's control flow.
        In practice the lifecycle is: register one watched address interval,
        let parser code continue reading bytes normally, and receive callback
        notifications each time a later matching read crosses this memory
        boundary.
        """
        self._read_observers[address_range] = callback

    def add_write_observer(self, address_range: range, callback: Callable):
        """Register a callback for writes inside an address range.

        Write observers capture parser-side mutations before they land in the
        backing list, which makes them useful for tools that need to mirror or
        audit address-level state changes.

        Parameters
        ----------
        address_range : range
            CPU-address interval to monitor.
        callback : Callable
            Observer invoked with ``(address, value)`` before a matching write.
        """
        self._write_observers[address_range] = callback

    def __getitem__(self, address):
        """Read one CPU-visible address and notify interested observers.

        This method is the main read boundary for parser code that treats the
        object like live NES memory, so it resolves any parser-side overrides
        before exposing the final byte to both observers and callers.

        Parameters
        ----------
        address : int
            CPU address to read from the parser memory image.

        Returns
        -------
        int
            Byte value observed at ``address`` after applying parser-specific
            overrides such as the hard-coded controller-ready value at 0x10.

        Notes
        -----
        The special-case value at ``0x10`` lets parser code emulate a stable
        readiness flag without depending on live hardware state. Observer
        callbacks run after the value has been resolved so they see the same
        byte that parser code consumes.
        """
        if address == 0x10:
            return_value = 0b1000_0000
        else:
            return_value = super(NESMemory, self).__getitem__(address)

        for address_range, callback in self._read_observers.items():
            if address in address_range:
                callback(address, return_value)

        return return_value

    def __setitem__(self, address, value):
        """Write one CPU-visible address and notify interested observers.

        This method is the write boundary for parser code that mutates decoded
        memory state. It publishes the pending write first, then preserves
        parser-specific invariants by dropping mapper-facing screen-pointer
        writes instead of storing them as ordinary RAM bytes.

        Parameters
        ----------
        address : int
            CPU address to update inside the parser memory image.
        value : int
            Byte value to store unless the address maps to ignored mapper-side
            screen-start registers.

        Returns
        -------
        None
            Returns ``None`` explicitly when the parser ignores mapper-facing
            screen-start writes. Otherwise this forwards the list assignment
            return value.

        Notes
        -----
        The parser treats ``MEM_Screen_Start_AddressL`` and
        ``MEM_Screen_Start_AddressH`` as mapper-facing side effects rather than
        persistent RAM. Ignoring writes there preserves the decoded screen
        pointer state instead of corrupting the backing memory image.
        """
        for address_range, callback in self._write_observers.items():
            if address in address_range:
                callback(address, value)

        if address in [MEM_Screen_Start_AddressL, MEM_Screen_Start_AddressH]:
            # ignore these addresses, since they seem to access the Mapper, but actually overwrite a pointer to the
            # screen memory
            return None

        return super(NESMemory, self).__setitem__(address, value)
