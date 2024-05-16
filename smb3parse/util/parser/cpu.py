"""First draft of a parser, emulating the 6502 processor of the NES and letting the ROM generate the level."""

from py65.devices import mpu6502
from py65.disassembler import Disassembler

from smb3parse.constants import BASE_OFFSET, PAGE_A000_OFFSET, Constants
from smb3parse.data_points import Position
from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET
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
    def __init__(self, rom: Rom, should_log=False):
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
        if not self.objects:
            # probably a call for the default background graphics
            return

        assert address in range(MEM_Screen_Memory_Start, MEM_Screen_Memory_End), address

        address -= MEM_Screen_Memory_Start

        self.objects[-1].tiles_in_level.append((address, value))

    def run_until(self, address: int, max_steps: int = -1):
        while self.pc != address:
            self.step()

            if self.step_count > max_steps:
                raise ValueError(f"Overstepped max steps value of {max_steps}.")

    def step(self):
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
        level_pointer = (self.memory[0x62] << 8) + self.memory[0x61]
        object_bytes = self.memory[level_pointer : level_pointer + 3]

        object_set_num = self.memory[MEM_Level_TileSet]

        parsed_object = ParsedObject(object_set_num, object_bytes, level_pointer)

        self.objects.append(parsed_object)

        return parsed_object

    def _maybe_finish_parsing_last_object(self):
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
        if "$" not in op or "#$" in op:
            return op

        inst, address = op.split("$")

        address = address.split(",")[0].replace("(", "").replace(")", "")

        if address.upper() in MEM_ADDRESS_LABELS:
            return op.replace(f"${address}", CYAN + MEM_ADDRESS_LABELS[address.upper()] + cur_color)

        return op

    def _replace_register_values(self, op: str):
        op = op.replace(",X", f",{self.x}").replace(",Y", f",{self.y}")

        return op

    def new_inst_0xa9(self):
        ram_address = self.ByteAt(self.ProgramCounter())

        if ram_address == 0x46:
            self.c000_bank = self.memory[MEM_PAGE_C000]
            self.memory.load_c000_page(self.c000_bank)

        elif ram_address == 0x47:
            self.a000_bank = self.memory[MEM_PAGE_A000]
            self.memory.load_a000_page(self.a000_bank)

        self.old_inst_0xa9(self)
