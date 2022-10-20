"""First draft of a parser, emulating the 6502 processor of the NES and letting the ROM generate the level."""

import pathlib

from py65.devices import mpu6502
from py65.disassembler import Disassembler

# FIXME remove the foundry import
from foundry.game.ObjectSet import ObjectSet
from smb3parse.data_points import Position
from smb3parse.util.parser import (
    MEM_ADDRESS_LABELS,
    MEM_Enemy_Palette,
    MEM_Graphics_Set,
    MEM_Level_TileSet,
    MEM_Object_Palette,
    MEM_PAGE_A000,
    MEM_PAGE_C000,
    MEM_Player_Current,
    MEM_Player_Screen,
    MEM_Player_X,
    MEM_Player_Y,
    MEM_Random_Pool_Start,
    MEM_Screen_Memory_End,
    MEM_Screen_Memory_Start,
    MEM_World_Num,
    ROM_EndObjectParsing,
    ROM_Level_Load_Entry,
)
from smb3parse.util.parser.level import ParsedLevel
from smb3parse.util.parser.memory import NESMemory
from smb3parse.util.parser.object import ParsedObject
from smb3parse.util.rom import Rom

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

        self.rom = rom
        self.should_log = should_log
        self.dis_asm = Disassembler(self)

        self.step_count = 0
        self.a000_bank = 0
        self.c000_bank = 0

        self.did_start_object_parsing = False
        self.objects: list[ParsedObject] = []

        # instructions
        self.old_inst_0xa9 = self.instruct[0xA9]
        self.instruct[0xA9] = NesCPU.new_inst_0xa9

    def load_from_world_map(self, world: int, pos: Position) -> ParsedLevel:
        self.start_pc = ROM_Level_Load_Entry
        self.reset()

        self.memory[MEM_Player_Current] = 0  # Mario
        self.memory[MEM_World_Num] = world

        self.memory[MEM_Player_Screen] = pos.screen
        self.memory[MEM_Player_X] = pos.x << 4
        self.memory[MEM_Player_Y] = pos.y << 4

        self.memory.add_write_observer(
            list(range(MEM_Screen_Memory_Start, MEM_Screen_Memory_End)), self._screen_memory_watcher
        )

        self.run_until(ROM_EndObjectParsing)

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
        while self.pc != address and self.step_count != max_steps:
            self.step()

    def step(self):
        if self.pc == 0x98EE:
            self._maybe_finish_parsing_last_object()
            parsed_object = self._start_parsing_next_object()

            object_bytes_text = list(map(hex, parsed_object.obj_bytes))

            optional_byte = hex(self.memory[parsed_object.pos_in_mem + 3])

            domain_offset = parsed_object.domain * 0x1F

            if parsed_object.is_fixed:
                obj_type = parsed_object.obj_id + domain_offset
            else:
                obj_type = (parsed_object.obj_id >> 4) + domain_offset + 16 - 1

            object_set_num = self.memory[MEM_Level_TileSet]

            name = ObjectSet(object_set_num).get_definition_of(obj_type).description.replace("/", "_")

            print(
                f"---> Parsing Object from {hex(parsed_object.pos_in_mem)}, "
                f"'{name}' {object_bytes_text} ({optional_byte})"
            )

            pathlib.Path(f"/tmp/memory_{self.step_count}_{name}.bin").write_bytes(bytes(self.memory))

        elif self.pc == ROM_EndObjectParsing:
            self._maybe_finish_parsing_last_object()
            breakpoint()
        elif self.pc == 0xD22B:
            # breakpoint()
            pass
        elif self.pc == 0xFF4E:
            breakpoint()

        if not self.should_log:
            return super(NesCPU, self).step()

        ins_len, op = self.dis_asm.instruction_at(self.pc)

        if "ST" in op:
            color = GREEN
        elif "LD" in op:
            color = RED
        elif "J" in op or "B" in op:
            color = PINK
        else:
            color = YELLOW

        self.step_count += 1

        ins_bytes = list(map(hex, self.memory[self.pc : self.pc + ins_len]))
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

        assert obj_len in [3, 4]

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
