"""Emulate SMB3's level-loader CPU path to reconstruct parsed level data.

This module runs selected SMB3 ROM entry points inside a ``py65`` 6502
emulator, watches the memory ranges that the loader mutates, and turns the
result back into :class:`~smb3parse.util.parser.level.ParsedLevel`,
:class:`~smb3parse.util.parser.object.ParsedObject`, and
:class:`~smb3parse.util.parser.object.ParsedEnemy` records. New maintainers
usually want to read :mod:`smb3parse.util.parser.level`,
:mod:`smb3parse.util.parser.object`, and
:mod:`smb3parse.util.parser.memory` next.

See Also
--------
smb3parse.util.parser.level
    Aggregates the parsed objects, enemies, and rendered screen buffer that
    this CPU produces.
smb3parse.util.parser.memory
    Supplies the bank-switching NES memory image that backs the emulation.
smb3parse.util.parser.object
    Defines the parsed object and enemy records appended during emulation.
"""

from py65.devices import mpu6502
from py65.disassembler import Disassembler

from smb3parse.constants import (
    BASE_OFFSET,
    ENEMY_ITEM_OBJECT_SET,
    PAGE_A000_OFFSET,
    Constants,
)
from smb3parse.data_points import Position
from smb3parse.util import apply
from smb3parse.util.parser.constants import (
    MEM_ADDRESS_LABELS,
    MEM_PAGE_A000,
    MEM_PAGE_C000,
    MEM_EnemiesStartA,
    MEM_EnemiesStartB,
    MEM_Enemy_Palette,
    MEM_Graphics_Set,
    MEM_Level_TileSet,
    MEM_LevelStartA,
    MEM_LevelStartB,
    MEM_Object_Palette,
    MEM_Player_Current,
    MEM_Player_Screen,
    MEM_Player_X,
    MEM_Player_Y,
    MEM_Random_Pool_Start,
    MEM_Reset_Latch,
    MEM_Screen_Memory_End,
    MEM_Screen_Memory_Start,
    MEM_World_Num,
    ROM_EndObjectParsing,
    ROM_Level_Load_Entry,
    ROM_LevelLoad_By_TileSet,
)
from smb3parse.util.parser.level import ParsedLevel
from smb3parse.util.parser.memory import NESMemory
from smb3parse.util.parser.object import ParsedEnemy, ParsedObject
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

PINK = "\033[95m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CLEAR = "\033[0m"


class NesCPU(mpu6502.MPU):
    """Emulate SMB3's loader routines and capture their parser-side outputs.

    The parser does not reimplement SMB3's object and screen-generation logic
    directly. Instead, it boots the ROM's own level-loader entry points,
    patches the memory image with either world-map state or direct level
    addresses, and records the generated objects and screen writes as the ROM
    executes.

    Parameters
    ----------
    rom : Rom
        ROM image whose PRG banks and constants back the emulated loader.
    should_log : bool, default=False
        Whether :meth:`step` should emit a colorized disassembly trace while
        the parser runs.

    Attributes
    ----------
    memory : NESMemory
        Emulated address space used by the CPU and by the parser-side screen
        and object observers.
    rom : Rom
        Source ROM used for PRG bank loads and post-parse enemy reads.
    should_log : bool
        Enables the debug-oriented disassembly path inside :meth:`step`.
    dis_asm : Disassembler
        ``py65`` disassembler used to print the traced instruction stream.
    step_count : int
        Count of executed instructions in the active load pass.
    a000_bank : int
        Active PRG bank mapped into the CPU's ``$A000`` window.
    c000_bank : int
        Active PRG bank mapped into the CPU's ``$C000`` window.
    start_pc : int
        Loader entry point that :meth:`reset` jumps to for the next parse.
    objects : list[ParsedObject]
        Parsed objects accumulated while the ROM generates the level.
    did_start_object_parsing : bool
        Legacy parser flag preserved for compatibility with older parser-side
        instrumentation.
    old_inst_0xa9 : collections.abc.Callable
        Original ``py65`` handler for opcode ``0xA9`` that
        :meth:`new_inst_0xa9` delegates back to after bank updates.

    Notes
    -----
    ``py65`` stores opcode handlers in a class-level dispatch table. This
    parser replaces the ``LDA #imm`` handler once so every CPU instance sees
    the bank-switching hook without stacking duplicate wrappers.
    """

    def __init__(self, rom: Rom, should_log=False):
        """Initialize the emulated CPU and parser-side observers.

        The constructor creates a fresh emulated RAM image, seeds the loader
        preconditions that SMB3 expects, resets parser-side tracking for the
        next level load, and patches the opcode table so later execution keeps
        PRG bank windows aligned with mapper writes.

        Parameters
        ----------
        rom : Rom
            ROM image whose PRG banks and loader entry points are executed.
        should_log : bool, default=False
            Whether instruction-by-instruction tracing should be enabled during
            later :meth:`step` calls.

        Notes
        -----
        Initialization seeds the emulated RAM with the reset-latch and random
        pool values that the loader expects, prepares the parsed-object
        accumulator for the next load pass, and installs the custom ``LDA``
        hook that keeps the ``$A000`` and ``$C000`` PRG windows synchronized
        with the ROM's bank-switching state.
        """
        super(NesCPU, self).__init__()

        self.memory = NESMemory([0x0] * 0x10000, rom)
        self.memory[MEM_Random_Pool_Start] = 0x88  # as in the ROM
        self.memory[MEM_Reset_Latch] = 0x5A  # prevents crash in LoadLevel_LittleCloudSolidRun

        self.rom = rom
        self.should_log = should_log
        self.dis_asm = Disassembler(self)

        self.step_count = 0
        self.a000_bank = 0
        self.c000_bank = 0

        self.did_start_object_parsing = False
        self.objects: list[ParsedObject] = []

        # instructions
        self.old_inst_0xa9 = NesCPU.inst_0xa9

        # self.instruct is a class attribute, so changes to it are kept between instantiations, therefore only replace
        # the load instruction once
        if self.instruct[0xA9] != NesCPU.new_inst_0xa9:
            self.instruct[0xA9] = NesCPU.new_inst_0xa9

    def load_from_world_map(self, world: int, pos: Position, max_steps=-1) -> ParsedLevel:
        """Parse the level that SMB3 would enter from a world-map tile.

        This route mirrors the world-map handoff used during normal play: it
        writes Mario's world, screen, and tile coordinates into the RAM
        locations consumed by the level-loader entry point and then lets the
        ROM choose the destination level.

        Parameters
        ----------
        world : int
            World number written into the loader's world-state RAM.
        pos : Position
            World-map tile position converted into the player screen and tile
            coordinates that the loader reads.
        max_steps : int, default=-1
            Maximum instruction count allowed before :meth:`run_until` aborts.

        Returns
        -------
        ParsedLevel
            Parsed level data generated by the ROM's world-map level-loader
            entry point.
        """
        self.start_pc = ROM_Level_Load_Entry

        self.memory[MEM_Player_Current] = 0  # Mario
        self.memory[MEM_World_Num] = world

        self.memory[MEM_Player_Screen] = pos.screen
        self.memory[MEM_Player_X] = pos.x << 4
        self.memory[MEM_Player_Y] = pos.y << 4

        return self._load_level(max_steps)

    def load_from_address(
        self, object_set_num: int, level_address: int, enemy_address: int, max_steps=-1
    ) -> ParsedLevel:
        """Parse a level by injecting its explicit loader addresses.

        This route bypasses world-map discovery and reconstructs the exact RAM
        and PRG-bank state that the tile-set loader expects when a caller
        already knows the object-set, level, and enemy stream addresses.

        Parameters
        ----------
        object_set_num : int
            Object-set index whose PRG bank mapping and loader tables should be
            used.
        level_address : int
            Absolute ROM address of the level object stream.
        enemy_address : int
            Absolute ROM address of the enemy stream header byte.
        max_steps : int, default=-1
            Maximum instruction count allowed before :meth:`run_until` aborts.

        Returns
        -------
        ParsedLevel
            Parsed level data generated by the ROM's tile-set loader path.

        Notes
        -----
        This path computes the object-stream offset that the loader expects in
        RAM, installs the matching ``$A000`` and ``$C000`` banks before reset,
        then appends enemy records by scanning the enemy stream directly after
        the ROM finishes the object-generation pass.
        """
        self.start_pc = ROM_LevelLoad_By_TileSet

        object_set_offset = (
            self.rom.int(Constants.OFFSET_BY_OBJECT_SET_A000 + object_set_num) * PRG_BANK_SIZE - PAGE_A000_OFFSET
        )
        level_offset = level_address - object_set_offset - BASE_OFFSET

        self.memory[MEM_Level_TileSet] = object_set_num
        self.memory[MEM_LevelStartA] = level_offset & 0xFF
        self.memory[MEM_LevelStartB] = level_offset >> 8
        self.memory[MEM_EnemiesStartA] = enemy_address & 0xFF
        self.memory[MEM_EnemiesStartB] = enemy_address >> 8

        self.memory[MEM_PAGE_A000] = self.a000_bank = self.rom.int(Constants.OFFSET_BY_OBJECT_SET_A000 + object_set_num)
        self.memory[MEM_PAGE_C000] = self.c000_bank = self.rom.int(Constants.OFFSET_BY_OBJECT_SET_C000 + object_set_num)

        self.memory.load_a000_page(self.a000_bank)
        self.memory.load_c000_page(self.c000_bank)

        level = self._load_level(max_steps)

        enemy_address += 1

        if enemy_address >= 0x0:
            while self.rom.int(enemy_address) != 0xFF:
                enemy_bytes = apply(int, self.rom.read(enemy_address, 3))
                level.parsed_enemies.append(ParsedEnemy(ENEMY_ITEM_OBJECT_SET, enemy_bytes, enemy_address))

                enemy_address += 3

        return level

    def _load_level(self, max_steps=-1) -> ParsedLevel:
        """Run the loader entry point and collect its parsed outputs.

        This helper installs the screen-write observer, resets CPU state to the
        selected start address, executes until SMB3 reports that object parsing
        is finished, and then snapshots both the parser-side object list and
        the generated screen buffer into one :class:`ParsedLevel`.

        Parameters
        ----------
        max_steps : int, default=-1
            Maximum instruction count allowed before parsing aborts.

        Returns
        -------
        ParsedLevel
            Aggregated parser result assembled from RAM state, screen writes,
            and parsed objects after the loader reaches its end marker.
        """
        self.memory.add_write_observer(
            range(MEM_Screen_Memory_Start, MEM_Screen_Memory_End),
            self._screen_memory_watcher,
        )

        self.reset()
        self.run_until(ROM_EndObjectParsing, max_steps)
        self._maybe_finish_parsing_last_object()

        return ParsedLevel(
            object_set_num=self.memory[MEM_Level_TileSet],
            graphics_set_num=self.memory[MEM_Graphics_Set],
            object_palette_num=self.memory[MEM_Object_Palette],
            enemy_palette_num=self.memory[MEM_Enemy_Palette],
            screen_memory=self.memory[MEM_Screen_Memory_Start:MEM_Screen_Memory_End],
            parsed_objects=self.objects,
        )

    def _screen_memory_watcher(self, address: int, value: int):
        """Attach screen-memory writes to the object currently being parsed.

        The loader writes tiles into the shared screen buffer while it handles
        one object at a time. This observer converts those writes into
        per-object tile ownership so later tooling can tell which object drew
        which tiles.

        Parameters
        ----------
        address : int
            Absolute CPU address that was written inside the screen buffer
            range.
        value : int
            Tile value stored at ``address`` by the running loader code.

        Notes
        -----
        The loader emits background bootstrap writes before any object has been
        recognized. Those writes are ignored so ``tiles_in_level`` only records
        tiles produced by a concrete parsed object.
        """
        if not self.objects:
            # probably a call for the default background graphics
            return

        assert address in range(MEM_Screen_Memory_Start, MEM_Screen_Memory_End), address

        address -= MEM_Screen_Memory_Start

        self.objects[-1].tiles_in_level.append((address, value))

    def run_until(self, target_address: int, max_steps: int = -1):
        """Execute instructions until the program counter reaches a target.

        The parser uses this as the execution boundary between setup code and
        the ROM routine that signals that object parsing has completed. The
        instruction counter protects callers from hanging forever on malformed
        addresses or corrupted loader state.

        Parameters
        ----------
        target_address : int
            Program-counter value that marks the end of this parser run.
        max_steps : int, default=-1
            Maximum instruction count allowed before execution aborts.

        Raises
        ------
        ValueError
            If execution exceeds ``max_steps`` before reaching
            ``target_address``.
        """
        while self.pc != target_address:
            self.step()

            if self.step_count > max_steps:
                raise ValueError(f"Overstepped max steps value of {max_steps}.")

    def step(self):
        """Execute one CPU instruction and update parser-side bookkeeping.

        This method is the synchronization point between emulation and parser
        state. It notices when SMB3 enters or leaves an object parse, keeps the
        trailing object bytes consistent with the ROM's loader-managed level
        pointer,
        and only then hands control back to ``py65`` for the actual CPU step
        and optional debug trace.

        Notes
        -----
        This override is where the emulator turns ROM execution back into
        parser records. It detects the instruction addresses that bracket SMB3's
        object parsing loop, starts or finalizes :class:`ParsedObject`
        instances around those boundaries, and optionally prints a colorized
        trace after symbolic address and register substitution. When tracing is
        disabled it still preserves the parser-side object lifecycle before
        delegating to ``py65`` for the actual instruction step.
        """
        self.step_count += 1

        if self.pc == 0x98EE:
            self._maybe_finish_parsing_last_object()
            parsed_object = self._start_parsing_next_object()

            if self.should_log:
                object_bytes_text = apply(hex, parsed_object.obj_bytes)

                optional_byte = hex(self.memory[parsed_object.pos_in_mem + 3])

                print(f"--> Parsing Object from {parsed_object.pos_in_mem:#x}, {object_bytes_text} ({optional_byte})")

        elif self.pc == ROM_EndObjectParsing:
            self._maybe_finish_parsing_last_object()
            breakpoint()
        elif self.pc == 0xD22B:
            # breakpoint()
            pass
        elif self.pc == 0xFF4E:
            # breakpoint()
            pass

        if not self.should_log:
            super(NesCPU, self).step()
            return

        ins_len, op = self.dis_asm.instruction_at(self.pc)

        if "ST" in op:
            color = GREEN
        elif "LD" in op:
            color = RED
        elif "J" in op or "B" in op:
            color = PINK
        else:
            color = YELLOW

        ins_bytes = apply(hex, self.memory[self.pc : self.pc + ins_len])
        op = self._replace_address_with_label(self._replace_register_values(op), color)

        print(f"{self.step_count:5} {self.pc:X}: {color}{op}{CLEAR}, {ins_bytes}")

        super(NesCPU, self).step()

        print(f"           A={self.a:X}, X={self.x:X}, Y={self.y:X}, A000={self.a000_bank}, C000={self.c000_bank}")

    def _start_parsing_next_object(self):
        """Create a parsed object from the loader's next object pointer.

        :meth:`step` calls this helper at the loader branch that begins a new
        object parse. By that point SMB3 has already advanced the level-data
        pointer and selected the active object set in RAM, so this helper can
        snapshot the raw object bytes into a :class:`ParsedObject` before the
        upcoming instruction stream starts emitting screen writes for that
        object. Appending the record to :attr:`objects` makes the new object
        the active sink that :meth:`_screen_memory_watcher` mutates during the
        same parse window.

        Returns
        -------
        ParsedObject
            Newly started parsed object appended to :attr:`objects`.
        """
        level_pointer = (self.memory[0x62] << 8) + self.memory[0x61]
        object_bytes = self.memory[level_pointer : level_pointer + 3]

        object_set_num = self.memory[MEM_Level_TileSet]

        parsed_object = ParsedObject(object_set_num, object_bytes, level_pointer)

        self.objects.append(parsed_object)

        return parsed_object

    def _maybe_finish_parsing_last_object(self):
        """Finalize or discard the object that the loader just advanced past.

        This helper reconciles the parser-side object list with the loader's
        byte-consumption result after each object boundary. It removes false
        starts, preserves standard three-byte objects, and appends the optional
        fourth byte used by the subset of object encodings that need one.

        Notes
        -----
        SMB3 advances the loader's level pointer after each object parse. The
        distance between the previous object start and the new pointer tells
        the parser whether the object was discarded, consumed three bytes, or
        consumed an optional fourth byte that must be appended retroactively.
        """
        if not self.objects:
            return

        cur_parsed_object = self.objects[-1]

        level_pointer = (self.memory[0x62] << 8) + self.memory[0x61]
        obj_len = level_pointer - cur_parsed_object.pos_in_mem

        assert obj_len in [0, 3, 4], (obj_len, cur_parsed_object)

        if obj_len == 0:
            self.objects.pop()

        if obj_len == 4:
            cur_parsed_object.obj_bytes.append(self.memory[level_pointer - 1])

    @staticmethod
    def _replace_address_with_label(op: str, cur_color):
        """Swap numeric addresses in a traced instruction for known labels.

        This keeps debug traces aligned with the parser constants module, so a
        maintainer can read loader-side RAM accesses in terms of SMB3 state
        names instead of raw hex addresses.

        Parameters
        ----------
        op : str
            Disassembled instruction text from ``py65``.
        cur_color : str
            ANSI color sequence that should be restored after a label
            substitution.

        Returns
        -------
        str
            Trace text with a symbolic RAM label inserted when one is known.
        """
        if "$" not in op or "#$" in op:
            return op

        inst, address = op.split("$")

        address = address.split(",")[0].replace("(", "").replace(")", "")

        if address.upper() in MEM_ADDRESS_LABELS:
            return op.replace(f"${address}", CYAN + MEM_ADDRESS_LABELS[address.upper()] + cur_color)

        return op

    def _replace_register_values(self, op: str):
        """Substitute live register values into indexed trace operands.

        :meth:`step` calls this helper immediately before printing each traced
        instruction. ``py65`` emits the disassembled operand text without the
        live ``X`` and ``Y`` values that the parser loop is about to use, so
        this helper resolves indexed operands against the CPU registers that
        will drive the next memory access. That keeps table lookups and
        pointer walks readable in the same trace line that produced them,
        which matters when following how loader state moves from ROM and RAM
        reads into parsed-object side effects.

        Parameters
        ----------
        op : str
            Disassembled instruction text from ``py65``.

        Returns
        -------
        str
            Instruction text with ``,X`` and ``,Y`` operands replaced by their
            live register values for easier debugging.
        """
        op = op.replace(",X", f",{self.x}").replace(",Y", f",{self.y}")

        return op

    def new_inst_0xa9(self):
        """Mirror ROM bank-switch writes before running ``LDA #imm``.

        Notes
        -----
        SMB3 uses immediate loads into the mapper control addresses that back
        the ``$A000`` and ``$C000`` PRG windows. This hook watches those loads,
        updates :attr:`a000_bank` or :attr:`c000_bank`, reloads the matching
        memory window, and then delegates to the original opcode handler so CPU
        state stays consistent with the parser's memory image.
        """
        ram_address = self.ByteAt(self.ProgramCounter())

        if ram_address == 0x46:
            self.c000_bank = self.memory[MEM_PAGE_C000]
            self.memory.load_c000_page(self.c000_bank)

        elif ram_address == 0x47:
            self.a000_bank = self.memory[MEM_PAGE_A000]
            self.memory.load_a000_page(self.a000_bank)

        self.old_inst_0xa9(self)
