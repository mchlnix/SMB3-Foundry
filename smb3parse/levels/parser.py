"""First draft of a parser, emulating the 6502 processor of the NES and letting the ROM generate the level."""

import dataclasses
import pathlib
from typing import Callable

from py65.devices import mpu6502
from py65.disassembler import Disassembler

from foundry.game.ObjectSet import ObjectSet
from smb3parse.constants import BASE_OFFSET
from smb3parse.data_points import Position
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

PINK = "\033[95m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CLEAR = "\033[0m"

# MEM are variables in RAM
MEM_Player_Y = 0x0075
MEM_Player_Screen = 0x0077
MEM_Player_X = 0x0079

MEM_PAGE_C000 = 0x071F
MEM_PAGE_A000 = 0x0720

MEM_Level_TileSet = 0x070A
MEM_Player_Current = 0x0726
MEM_World_Num = 0x0727

MEM_Object_Palette = 0x073A
MEM_Enemy_Palette = 0x073B
MEM_Random_Pool_Start = 0x0781

MEM_Screen_Memory_Start = 0x6000
MEM_Screen_Memory_End = 0x7950

MEM_Graphics_Set = 0x7EBD

MEM_Screen_Start_AddressL = 0x8000
MEM_Screen_Start_AddressH = 0x8001

MEM_ADDRESSES = {
    "00": "TempVar_01",
    "01": "TempVar_02",
    "02": "TempVar_03",
    "03": "TempVar_04",
    "04": "TempVar_05",
    "05": "TempVar_06",
    "06": "TempVar_07",
    "07": "TempVar_08",
    "08": "TempVar_09",
    "09": "TempVar_10",
    "0A": "TempVar_11",
    "0B": "TempVar_12",
    "0C": "TempVar_13",
    "0D": "TempVar_14",
    "0E": "TempVar_15",
    "0F": "TempVar_16",
    "61": "LevelStartA",  # "Level_LayPtr_AddrL",
    "62": "LevelStartB",  # "Level_LayPtr_AddrH",
    "63": "Map_Tile_AddrL (ScreenStart)",
    "64": "Map_Tile_AddrH (ScreenStart)",
    "03DE": "Level_JctCtl",
    "0700": "TileAddr_Off (InScreenOffset)",
    "0706": "LL_ShapeDef",
    "070A": "Level_TileSet",
    "0726": "Player_Current",
    "0727": "World_Num",
    "0739": "Clear_Pattern",
    "0781": "MEM_Random_Pool_Start",
    "7DFE": "JumpAddressA",
    "7DFF": "JumpAddressB",
    "7E00": "JumpEnemiesA",
    "7E01": "JumpEnemiesB",
    "97B7": "LevelLoad",
    "991E": "ObjectNotAJump",
    "992E": "JumpToFixed",
    "9934": "EndObjectParsing",
    "9935": "LoadLevel_Set_TileMemAddr",
    "9A1D": "LevelLoad By TileSet",
    "9A49": "LeveLoad_DynSizeGens",
    "9A75": "LeveLoad_FixedSizeGens",
    "B0FF": "Map PrepareLevel",
    "D2F8": "LL_RunGroundTopTiles",
    "D2FE": "LL_RunGroundMidTiles",
    "FE92": "DynJump",
    "FFBF": "PRG_Change_Both",
    "FFD1": "PRG_Change_C000",
}
# ROM is code or data in ROM banks 0x8000 - 0xFFFF

ROM_Level_Load_Entry = 0x891A
ROM_EndObjectParsing = 0x9934


class MemoryObserver(list):
    def __init__(self, backing_list: list, rom: Rom):
        super(MemoryObserver, self).__init__(backing_list)

        self.rom = rom

        self._read_observers: dict[list[int, Callable]] = {}
        self._write_observers: dict[list[int, Callable]] = {}

        # load PRG 30
        self._load_bank(30, 0x8000)

        # load PRG 31
        self._load_bank(31, 0xE000)

    def load_a000_page(self, prg_index: int):
        self._load_bank(prg_index, 0xA000)

    def load_c000_page(self, prg_index: int):
        self._load_bank(prg_index, 0xC000)

    def _load_bank(self, prg_index: int, offset: int):
        prg_bank_position = BASE_OFFSET + prg_index * PRG_BANK_SIZE

        self[offset : offset + PRG_BANK_SIZE] = self.rom.read(prg_bank_position, PRG_BANK_SIZE)

    def add_read_observer(self, address_list: list[int], callback: Callable):
        self._read_observers[address_list] = callback

    def add_write_observer(self, address_list: list[int], callback: Callable):
        self._write_observers[tuple(address_list)] = callback

    def __getitem__(self, address: int):
        if address == 0x10:
            return_value = 0b1000_0000
        else:
            return_value = super(MemoryObserver, self).__getitem__(address)

        for address_range, callback in self._read_observers.items():
            if address in address_range:
                callback(address, return_value)

        return return_value

    def __setitem__(self, address, value):
        for address_range, callback in self._write_observers.items():
            if address in address_range:
                callback(address, value)

        if address in [MEM_Screen_Start_AddressL, MEM_Screen_Start_AddressH]:
            # ignore these addresses, since they seem to access the Mapper, but actually overwrite a pointer to the
            # screen memory
            return

        return super(MemoryObserver, self).__setitem__(address, value)


@dataclasses.dataclass
class ParsedLevel:
    object_set_num: int
    graphics_set_num: int
    object_palette_num: int
    enemy_palette_num: int
    screen_memory: list[int]


class NesCPU(mpu6502.MPU):
    def __init__(self, rom: Rom, should_log=False):
        super(NesCPU, self).__init__()

        self.memory = MemoryObserver([0x0] * 0x10000, rom)
        self.memory[MEM_Random_Pool_Start] = 0x88  # as in the ROM

        self.rom = rom
        self.should_log = should_log
        self.dis_asm = Disassembler(self)

        self.step_count = 0
        self.a000_bank = 0
        self.c000_bank = 0

        self.did_start_object_parsing = False

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

        self.run_until(ROM_EndObjectParsing)

        return ParsedLevel(
            object_set_num=self.memory[MEM_Level_TileSet],
            graphics_set_num=self.memory[MEM_Graphics_Set],
            object_palette_num=self.memory[MEM_Object_Palette],
            enemy_palette_num=self.memory[MEM_Enemy_Palette],
            screen_memory=self.memory[MEM_Screen_Memory_Start:MEM_Screen_Memory_End],
        )

    def run_until(self, address: int, max_steps: int = -1):
        while self.pc != address and self.step_count != max_steps:
            self.step()

    def step(self):
        if not self.should_log:
            super(NesCPU, self).step()
            return

        ins_len, op = self.dis_asm.instruction_at(self.pc)

        if self.pc == 0x98EE:
            level_pointer = (self.memory[0x62] << 8) + self.memory[0x61]
            object_bytes = self.memory[level_pointer : level_pointer + 3]
            object_bytes_text = list(map(hex, object_bytes))

            optional_byte = hex(self.memory[level_pointer + 3])

            is_fixed = object_bytes[2] <= 0x0F

            domain_offset = (object_bytes[0] >> 5) * 0x1F

            if is_fixed:
                obj_type = object_bytes[2] + domain_offset
            else:
                obj_type = (object_bytes[2] >> 4) + domain_offset + 16 - 1

            name = ObjectSet(self.memory[MEM_Level_TileSet]).get_definition_of(obj_type).description.replace("/", "_")

            print(f"---> Parsing Object from {hex(level_pointer)}, '{name}' {object_bytes_text} ({optional_byte})")

            pathlib.Path(f"/tmp/memory_{self.step_count}_{name}.bin").write_bytes(bytes(self.memory))

        elif self.pc == ROM_EndObjectParsing:
            breakpoint()
        elif self.pc == 0xD22B:
            # breakpoint()
            pass
        elif self.pc == 0xFF4E:
            breakpoint()

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

    @staticmethod
    def _replace_address_with_label(op: str, cur_color):
        if "$" not in op or "#$" in op:
            return op

        inst, address = op.split("$")

        address = address.split(",")[0].replace("(", "").replace(")", "")

        if address.upper() in MEM_ADDRESSES:
            return op.replace(f"${address}", CYAN + MEM_ADDRESSES[address.upper()] + cur_color)

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
