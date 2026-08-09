use crate::level::ParsedLevel;
use crate::memory::{Memory, PRG_BANK_SIZE, Rom};
use crate::object::{ParsedEnemy, ParsedLevelObject};
use std::fmt::{Debug, Display, Formatter};

const MEM_PAGE_C000: MemAddress = 0x071F;
const MEM_PAGE_A000: MemAddress = 0x0720;

#[derive(Debug, Clone)]
pub struct DisAsm {
    instruction_code: String,
}

#[derive(Debug)]
pub struct Position {
    x: u8,
    y: u8,
    screen: u8,
}

#[derive(Debug)]
pub struct MPU {
    // config
    byte_mask: u8,
    addr_mask: u16,
    addr_high_mask: u16,

    /// stack pointer base address is 0x0100, since the stack lives from 0x0100 to 0x01FF
    sp_base: MemAddress,

    /// stack pointer
    sp: u8,

    // registers
    accu: Register,
    x: Register,
    y: Register,

    /// processor flags
    flags: u8,

    // vm status
    ex_cycles: u32,
    add_cycles: bool,
    processor_cycles: u32,

    memory: Memory,
    start_pc: MemAddress,
    pub pc: MemAddress,

    // instruction
    pub instruct: Vec<fn(&mut MPU)>,
    cycle_time: Vec<u8>,
    extra_cycles: Vec<u8>,
    disassemble: Vec<DisAsm>,

    step_count: u32,
    a000_bank: u8,
    c000_bank: u8,

    objects: Vec<ParsedLevelObject>,
}

pub type MemAddress = u16;
pub type RomAddress = u32;
type Register = u8;
pub type Byte = u8;
type Word = u16;

// processor flags
const NEGATIVE: u8 = 0b1000_0000;
const OVERFLOW: u8 = 0b0100_0000;
const UNUSED: u8 = 0b0010_0000;
const BREAK: u8 = 0b0001_0000;
const DECIMAL: u8 = 0b0000_1000;
const INTERRUPT: u8 = 0b0000_0100;
const ZERO: u8 = 0b0000_0010;
const CARRY: u8 = 0b0000_0001;

#[derive(Debug)]
struct FlagsPP(u8);

impl Display for FlagsPP {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        if self.0 & NEGATIVE != 0 {
            write!(f, "N")?;
        } else {
            write!(f, "0")?;
        }

        if self.0 & OVERFLOW != 0 {
            write!(f, "O")?;
        } else {
            write!(f, "0")?;
        }

        if self.0 & UNUSED != 0 {
            write!(f, "U")?;
        } else {
            write!(f, "0")?;
        }

        if self.0 & BREAK != 0 {
            write!(f, "B")?;
        } else {
            write!(f, "0")?;
        }

        if self.0 & DECIMAL != 0 {
            write!(f, "D")?;
        } else {
            write!(f, "0")?;
        }

        if self.0 & INTERRUPT != 0 {
            write!(f, "I")?;
        } else {
            write!(f, "0")?;
        }

        if self.0 & ZERO != 0 {
            write!(f, "Z")?;
        } else {
            write!(f, "0")?;
        }

        if self.0 & CARRY != 0 {
            write!(f, "C")?;
        } else {
            write!(f, "0")?;
        }

        Ok(())
    }
}

type AddressFn = fn(&mut MPU) -> MemAddress;

const SHOULD_LOG: bool = false;

impl MPU {
    // vectors
    const IRQ: u16 = 0xfffe;

    const BYTE_WIDTH: u32 = 8;

    pub fn new(rom: Rom) -> MPU {
        let byte_mask = Byte::MAX;
        let addr_mask = MemAddress::MAX;

        // The stack position in memory is 0x0100 - 0x01FF
        let sp_base = 0x0100;

        // The stack grows downwards, so it starts at 0xFF
        let sp = u8::MAX;

        let mut mpu = MPU {
            byte_mask,
            addr_mask,
            addr_high_mask: 0xFF00,
            sp_base,
            sp,

            accu: 0,
            x: 0,
            y: 0,

            flags: BREAK | UNUSED,

            ex_cycles: 0,
            add_cycles: false,
            processor_cycles: 0,

            memory: Memory::new(rom),
            start_pc: 0,
            pc: 0,

            instruct: Vec::new(),
            cycle_time: vec![0; 256],
            extra_cycles: vec![0; 256],
            disassemble: vec![
                DisAsm {
                    instruction_code: String::from("???"),
                };
                256
            ],
            step_count: 0,
            a000_bank: 0,
            c000_bank: 0,

            objects: vec![],
        };

        mpu.instruct = vec![MPU::inst_not_implemented; 256];

        {
            mpu._log_op_code(MPU::inst_0x00, 0x00, "BRK", 7, 0);
            mpu._log_op_code(MPU::inst_0x01, 0x01, "ORA", 6, 0);
            mpu._log_op_code(MPU::inst_0x05, 0x05, "ORA", 3, 0);
            mpu._log_op_code(MPU::inst_0x06, 0x06, "ASL", 5, 0);
            mpu._log_op_code(MPU::inst_0x08, 0x08, "PHP", 3, 0);
            mpu._log_op_code(MPU::inst_0x09, 0x09, "ORA", 2, 0);
            mpu._log_op_code(MPU::inst_0x0a, 0x0a, "ASL", 2, 0);
            mpu._log_op_code(MPU::inst_0x0d, 0x0d, "ORA", 4, 0);
            mpu._log_op_code(MPU::inst_0x0e, 0x0e, "ASL", 6, 0);
            mpu._log_op_code(MPU::inst_0x10, 0x10, "BPL", 2, 2);
            mpu._log_op_code(MPU::inst_0x11, 0x11, "ORA", 5, 1);
            mpu._log_op_code(MPU::inst_0x15, 0x15, "ORA", 4, 0);
            mpu._log_op_code(MPU::inst_0x16, 0x16, "ASL", 6, 0);
            mpu._log_op_code(MPU::inst_0x18, 0x18, "CLC", 2, 0);
            mpu._log_op_code(MPU::inst_0x19, 0x19, "ORA", 4, 1);
            mpu._log_op_code(MPU::inst_0x1d, 0x1d, "ORA", 4, 1);
            mpu._log_op_code(MPU::inst_0x1e, 0x1e, "ASL", 7, 0);
            mpu._log_op_code(MPU::inst_0x20, 0x20, "JSR", 6, 0);
            mpu._log_op_code(MPU::inst_0x21, 0x21, "AND", 6, 0);
            mpu._log_op_code(MPU::inst_0x24, 0x24, "BIT", 3, 0);
            mpu._log_op_code(MPU::inst_0x25, 0x25, "AND", 3, 0);
            mpu._log_op_code(MPU::inst_0x26, 0x26, "ROL", 5, 0);
            mpu._log_op_code(MPU::inst_0x28, 0x28, "PLP", 4, 0);
            mpu._log_op_code(MPU::inst_0x29, 0x29, "AND", 2, 0);
            mpu._log_op_code(MPU::inst_0x2a, 0x2a, "ROL", 2, 0);
            mpu._log_op_code(MPU::inst_0x2c, 0x2c, "BIT", 4, 0);
            mpu._log_op_code(MPU::inst_0x2d, 0x2d, "AND", 4, 0);
            mpu._log_op_code(MPU::inst_0x2e, 0x2e, "ROL", 6, 0);
            mpu._log_op_code(MPU::inst_0x30, 0x30, "BMI", 2, 2);
            mpu._log_op_code(MPU::inst_0x31, 0x31, "AND", 5, 1);
            mpu._log_op_code(MPU::inst_0x35, 0x35, "AND", 4, 0);
            mpu._log_op_code(MPU::inst_0x36, 0x36, "ROL", 6, 0);
            mpu._log_op_code(MPU::inst_0x38, 0x38, "SEC", 2, 0);
            mpu._log_op_code(MPU::inst_0x39, 0x39, "AND", 4, 1);
            mpu._log_op_code(MPU::inst_0x3d, 0x3d, "AND", 4, 1);
            mpu._log_op_code(MPU::inst_0x3e, 0x3e, "ROL", 7, 0);
            mpu._log_op_code(MPU::inst_0x40, 0x40, "RTI", 6, 0);
            mpu._log_op_code(MPU::inst_0x41, 0x41, "EOR", 6, 0);
            mpu._log_op_code(MPU::inst_0x45, 0x45, "EOR", 3, 0);
            mpu._log_op_code(MPU::inst_0x46, 0x46, "LSR", 5, 0);
            mpu._log_op_code(MPU::inst_0x48, 0x48, "PHA", 3, 0);
            mpu._log_op_code(MPU::inst_0x49, 0x49, "EOR", 2, 0);
            mpu._log_op_code(MPU::inst_0x4a, 0x4a, "LSR", 2, 0);
            mpu._log_op_code(MPU::inst_0x4c, 0x4c, "JMP", 3, 0);
            mpu._log_op_code(MPU::inst_0x4d, 0x4d, "EOR", 4, 0);
            mpu._log_op_code(MPU::inst_0x4e, 0x4e, "LSR", 6, 0);
            mpu._log_op_code(MPU::inst_0x50, 0x50, "BVC", 2, 2);
            mpu._log_op_code(MPU::inst_0x51, 0x51, "EOR", 5, 1);
            mpu._log_op_code(MPU::inst_0x55, 0x55, "EOR", 4, 0);
            mpu._log_op_code(MPU::inst_0x56, 0x56, "LSR", 6, 0);
            mpu._log_op_code(MPU::inst_0x58, 0x58, "CLI", 2, 0);
            mpu._log_op_code(MPU::inst_0x59, 0x59, "EOR", 4, 1);
            mpu._log_op_code(MPU::inst_0x5d, 0x5d, "EOR", 4, 1);
            mpu._log_op_code(MPU::inst_0x5e, 0x5e, "LSR", 7, 0);
            mpu._log_op_code(MPU::inst_0x60, 0x60, "RTS", 6, 0);
            mpu._log_op_code(MPU::inst_0x61, 0x61, "ADC", 6, 0);
            mpu._log_op_code(MPU::inst_0x65, 0x65, "ADC", 3, 0);
            mpu._log_op_code(MPU::inst_0x66, 0x66, "ROR", 5, 0);
            mpu._log_op_code(MPU::inst_0x68, 0x68, "PLA", 4, 0);
            mpu._log_op_code(MPU::inst_0x69, 0x69, "ADC", 2, 0);
            mpu._log_op_code(MPU::inst_0x6a, 0x6a, "ROR", 2, 0);
            mpu._log_op_code(MPU::inst_0x6c, 0x6c, "JMP", 5, 0);
            mpu._log_op_code(MPU::inst_0x6d, 0x6d, "ADC", 4, 0);
            mpu._log_op_code(MPU::inst_0x6e, 0x6e, "ROR", 6, 0);
            mpu._log_op_code(MPU::inst_0x70, 0x70, "BVS", 2, 2);
            mpu._log_op_code(MPU::inst_0x71, 0x71, "ADC", 5, 1);
            mpu._log_op_code(MPU::inst_0x75, 0x75, "ADC", 4, 0);
            mpu._log_op_code(MPU::inst_0x76, 0x76, "ROR", 6, 0);
            mpu._log_op_code(MPU::inst_0x78, 0x78, "SEI", 2, 0);
            mpu._log_op_code(MPU::inst_0x79, 0x79, "ADC", 4, 1);
            mpu._log_op_code(MPU::inst_0x7d, 0x7d, "ADC", 4, 1);
            mpu._log_op_code(MPU::inst_0x7e, 0x7e, "ROR", 7, 0);
            mpu._log_op_code(MPU::inst_0x81, 0x81, "STA", 6, 0);
            mpu._log_op_code(MPU::inst_0x84, 0x84, "STY", 3, 0);
            mpu._log_op_code(MPU::inst_0x85, 0x85, "STA", 3, 0);
            mpu._log_op_code(MPU::inst_0x86, 0x86, "STX", 3, 0);
            mpu._log_op_code(MPU::inst_0x88, 0x88, "DEY", 2, 0);
            mpu._log_op_code(MPU::inst_0x8a, 0x8a, "TXA", 2, 0);
            mpu._log_op_code(MPU::inst_0x8c, 0x8c, "STY", 4, 0);
            mpu._log_op_code(MPU::inst_0x8d, 0x8d, "STA", 4, 0);
            mpu._log_op_code(MPU::inst_0x8e, 0x8e, "STX", 4, 0);
            mpu._log_op_code(MPU::inst_0x90, 0x90, "BCC", 2, 2);
            mpu._log_op_code(MPU::inst_0x91, 0x91, "STA", 6, 0);
            mpu._log_op_code(MPU::inst_0x94, 0x94, "STY", 4, 0);
            mpu._log_op_code(MPU::inst_0x95, 0x95, "STA", 4, 0);
            mpu._log_op_code(MPU::inst_0x96, 0x96, "STX", 4, 0);
            mpu._log_op_code(MPU::inst_0x98, 0x98, "TYA", 2, 0);
            mpu._log_op_code(MPU::inst_0x99, 0x99, "STA", 5, 0);
            mpu._log_op_code(MPU::inst_0x9a, 0x9a, "TXS", 2, 0);
            mpu._log_op_code(MPU::inst_0x9d, 0x9d, "STA", 5, 0);
            mpu._log_op_code(MPU::inst_0xa0, 0xa0, "LDY", 2, 0);
            mpu._log_op_code(MPU::inst_0xa1, 0xa1, "LDA", 6, 0);
            mpu._log_op_code(MPU::inst_0xa2, 0xa2, "LDX", 2, 0);
            mpu._log_op_code(MPU::inst_0xa4, 0xa4, "LDY", 3, 0);
            mpu._log_op_code(MPU::inst_0xa5, 0xa5, "LDA", 3, 0);
            mpu._log_op_code(MPU::inst_0xa6, 0xa6, "LDX", 3, 0);
            mpu._log_op_code(MPU::inst_0xa8, 0xa8, "TAY", 2, 0);
            mpu._log_op_code(MPU::inst_0xa9, 0xa9, "LDA", 2, 0);
            mpu._log_op_code(MPU::inst_0xaa, 0xaa, "TAX", 2, 0);
            mpu._log_op_code(MPU::inst_0xac, 0xac, "LDY", 4, 0);
            mpu._log_op_code(MPU::inst_0xad, 0xad, "LDA", 4, 0);
            mpu._log_op_code(MPU::inst_0xae, 0xae, "LDX", 4, 0);
            mpu._log_op_code(MPU::inst_0xb0, 0xb0, "BCS", 2, 2);
            mpu._log_op_code(MPU::inst_0xb1, 0xb1, "LDA", 5, 1);
            mpu._log_op_code(MPU::inst_0xb4, 0xb4, "LDY", 4, 0);
            mpu._log_op_code(MPU::inst_0xb5, 0xb5, "LDA", 4, 0);
            mpu._log_op_code(MPU::inst_0xb6, 0xb6, "LDX", 4, 0);
            mpu._log_op_code(MPU::inst_0xb8, 0xb8, "CLV", 2, 0);
            mpu._log_op_code(MPU::inst_0xb9, 0xb9, "LDA", 4, 1);
            mpu._log_op_code(MPU::inst_0xba, 0xba, "TSX", 2, 0);
            mpu._log_op_code(MPU::inst_0xbc, 0xbc, "LDY", 4, 1);
            mpu._log_op_code(MPU::inst_0xbd, 0xbd, "LDA", 4, 1);
            mpu._log_op_code(MPU::inst_0xbe, 0xbe, "LDX", 4, 1);
            mpu._log_op_code(MPU::inst_0xc0, 0xc0, "CPY", 2, 0);
            mpu._log_op_code(MPU::inst_0xc1, 0xc1, "CMP", 6, 0);
            mpu._log_op_code(MPU::inst_0xc4, 0xc4, "CPY", 3, 0);
            mpu._log_op_code(MPU::inst_0xc5, 0xc5, "CMP", 3, 0);
            mpu._log_op_code(MPU::inst_0xc6, 0xc6, "DEC", 5, 0);
            mpu._log_op_code(MPU::inst_0xc8, 0xc8, "INY", 2, 0);
            mpu._log_op_code(MPU::inst_0xc9, 0xc9, "CMP", 2, 0);
            mpu._log_op_code(MPU::inst_0xca, 0xca, "DEX", 2, 0);
            mpu._log_op_code(MPU::inst_0xcc, 0xcc, "CPY", 4, 0);
            mpu._log_op_code(MPU::inst_0xcd, 0xcd, "CMP", 4, 0);
            mpu._log_op_code(MPU::inst_0xce, 0xce, "DEC", 3, 0);
            mpu._log_op_code(MPU::inst_0xd0, 0xd0, "BNE", 2, 2);
            mpu._log_op_code(MPU::inst_0xd1, 0xd1, "CMP", 5, 1);
            mpu._log_op_code(MPU::inst_0xd5, 0xd5, "CMP", 4, 0);
            mpu._log_op_code(MPU::inst_0xd6, 0xd6, "DEC", 6, 0);
            mpu._log_op_code(MPU::inst_0xd8, 0xd8, "CLD", 2, 0);
            mpu._log_op_code(MPU::inst_0xd9, 0xd9, "CMP", 4, 1);
            mpu._log_op_code(MPU::inst_0xdd, 0xdd, "CMP", 4, 1);
            mpu._log_op_code(MPU::inst_0xde, 0xde, "DEC", 7, 0);
            mpu._log_op_code(MPU::inst_0xe0, 0xe0, "CPX", 2, 0);
            mpu._log_op_code(MPU::inst_0xe1, 0xe1, "SBC", 6, 0);
            mpu._log_op_code(MPU::inst_0xe4, 0xe4, "CPX", 3, 0);
            mpu._log_op_code(MPU::inst_0xe5, 0xe5, "SBC", 3, 0);
            mpu._log_op_code(MPU::inst_0xe6, 0xe6, "INC", 5, 0);
            mpu._log_op_code(MPU::inst_0xe8, 0xe8, "INX", 2, 0);
            mpu._log_op_code(MPU::inst_0xe9, 0xe9, "SBC", 2, 0);
            mpu._log_op_code(MPU::inst_0xea, 0xea, "NOP", 2, 0);
            mpu._log_op_code(MPU::inst_0xec, 0xec, "CPX", 4, 0);
            mpu._log_op_code(MPU::inst_0xed, 0xed, "SBC", 4, 0);
            mpu._log_op_code(MPU::inst_0xee, 0xee, "INC", 6, 0);
            mpu._log_op_code(MPU::inst_0xf0, 0xf0, "BEQ", 2, 2);
            mpu._log_op_code(MPU::inst_0xf1, 0xf1, "SBC", 5, 1);
            mpu._log_op_code(MPU::inst_0xf5, 0xf5, "SBC", 4, 0);
            mpu._log_op_code(MPU::inst_0xf6, 0xf6, "INC", 6, 0);
            mpu._log_op_code(MPU::inst_0xf8, 0xf8, "SED", 2, 0);
            mpu._log_op_code(MPU::inst_0xf9, 0xf9, "SBC", 4, 1);
            mpu._log_op_code(MPU::inst_0xfd, 0xfd, "SBC", 4, 1);
            mpu._log_op_code(MPU::inst_0xfe, 0xfe, "INC", 7, 0);
        }

        mpu.reset();

        mpu
    }

    fn step(&mut self) -> &mut Self {
        let instruct_code = self.memory[self.pc];

        let inst_name = &self.disassemble[instruct_code as usize].instruction_code;

        if SHOULD_LOG {
            println!(
                "{:5} {:x}: {}({:x})",
                self.step_count,
                self.pc,
                inst_name,
                { instruct_code }
            );
        }

        self.pc = self.pc.wrapping_add(1);

        self.ex_cycles = 0;
        self.add_cycles = self.extra_cycles[instruct_code as usize] != 0;
        self.instruct[instruct_code as usize](self);

        if SHOULD_LOG {
            println!(
                "   A: {:02x} X: {:02x} Y: {:02x} P: {}, M:{}",
                self.accu,
                self.x,
                self.y,
                FlagsPP(self.flags),
                self.memory.memory[0]
            );
        }
        self.processor_cycles += self.cycle_time[instruct_code as usize] as u32 + self.ex_cycles;

        self
    }

    fn reset(&mut self) {
        self.pc = self.start_pc;
        self.sp = self.byte_mask;

        self.accu = 0;
        self.x = 0;
        self.y = 0;

        self.processor_cycles = 0;
    }

    fn _set_flags(&mut self, flags: Byte) {
        self.flags |= flags;
    }

    fn _clear_flags(&mut self, flags: Byte) {
        self.flags &= !flags;
    }

    // helpers for addressing modes

    pub fn byte_at(&self, address: MemAddress) -> Byte {
        self.memory[address]
    }

    fn word_at(&self, address: MemAddress) -> Word {
        if address == MemAddress::MAX {
            panic!("Invalid word address: {}", address);
        } else {
            self._bytes_to_word(address, address + 1)
        }
    }

    /// This function reads a word from the given `address`.
    /// However, contrary to `word_at`, the high byte of `address` is not changed, even if the lower
    /// byte overflows it.
    ///
    /// This is primarily used, when working with the Zero Page, since it only comprises 0xFF bytes
    /// of memory and wraps around to the beginning, when read at the edge.
    ///
    /// For example the address 0x00FF would read the word from 0x00FF and 0x0000.
    fn wrap_at(&self, address: MemAddress) -> Word {
        let high_part = address & self.addr_high_mask;
        let low_part = (address + 1) & self.byte_mask as u16;

        let wrapped_address = high_part + low_part;

        self._bytes_to_word(address, wrapped_address)
    }

    fn _address_offset_by_register(
        &self,
        base_address: MemAddress,
        register: Register,
    ) -> MemAddress {
        let offset = register as MemAddress;
        let offset_address = (base_address + offset) & self.addr_mask;

        offset_address
    }

    fn _bytes_to_word(&self, lo_address: MemAddress, hi_address: MemAddress) -> u16 {
        let lo_byte = self.byte_at(lo_address) as u16;
        let hi_byte = self.byte_at(hi_address) as u16;

        let word = (hi_byte << MPU::BYTE_WIDTH) + lo_byte;

        word
    }

    fn program_counter(&mut self) -> MemAddress {
        self.pc
    }

    // addressing modes

    fn immediate_byte(&mut self) -> Byte {
        self.byte_at(self.pc)
    }

    fn zero_page_addr(&mut self) -> MemAddress {
        self.immediate_byte() as MemAddress
    }

    fn zero_page_x_addr(&mut self) -> MemAddress {
        (self.x + self.zero_page_addr() as Byte & self.byte_mask) as MemAddress
    }

    fn zero_page_y_addr(&mut self) -> MemAddress {
        (self.y + self.zero_page_addr() as Byte & self.byte_mask) as MemAddress
    }

    fn indirect_x_addr(&mut self) -> MemAddress {
        let zero_page_address = self.zero_page_x_addr();

        self.wrap_at(zero_page_address) as MemAddress
    }

    fn indirect_y_addr(&mut self) -> MemAddress {
        let zero_page_address = self.zero_page_addr();
        let base_address = self.wrap_at(zero_page_address) as MemAddress;
        let address_with_offset = self._address_offset_by_register(base_address, self.y);

        if self.add_cycles {
            // if the high byte of the addresses is different, add an extra cycle
            if !self._have_same_high_byte(base_address, address_with_offset) {
                self.ex_cycles += 1;
            }
        }

        address_with_offset
    }

    fn absolute_addr(&mut self) -> MemAddress {
        self.word_at(self.pc)
    }

    fn absolute_x_addr(&mut self) -> MemAddress {
        let base_address = self.absolute_addr();
        let address_with_offset = self._address_offset_by_register(base_address, self.x);

        if self.add_cycles {
            if !self._have_same_high_byte(base_address, address_with_offset) {
                self.ex_cycles += 1;
            }
        }

        address_with_offset
    }

    fn absolute_y_addr(&mut self) -> MemAddress {
        let base_address = self.absolute_addr();
        let address_with_offset = self._address_offset_by_register(base_address, self.y);

        if self.add_cycles {
            if !self._have_same_high_byte(base_address, address_with_offset) {
                self.ex_cycles += 1;
            }
        }

        address_with_offset
    }

    fn _have_same_high_byte(
        &self,
        base_address: MemAddress,
        address_with_offset: MemAddress,
    ) -> bool {
        ((base_address ^ address_with_offset) & self.addr_high_mask) == 0x0
    }

    fn branch_rel_addr(&mut self) {
        self.ex_cycles += 1;

        let addr_at_pc = self.immediate_byte();
        self.pc = self.pc.wrapping_add(1);

        let address: MemAddress;

        if (addr_at_pc & NEGATIVE) == NEGATIVE {
            address = self
                .pc
                .wrapping_sub(((addr_at_pc ^ self.byte_mask) as MemAddress) + 1);
        } else {
            address = self.pc.wrapping_add(addr_at_pc as MemAddress);
        }

        // if the address is not in the same upper address range as the program counter
        // add an extra cycle
        if (address & self.addr_high_mask) != (self.pc & self.addr_high_mask) {
            self.ex_cycles += 1;
        }

        self.pc = address & self.addr_mask;
    }

    // stack

    fn st_push(&mut self, byte: Byte) {
        self.memory
            .set_byte(self.sp_base + self.sp as MemAddress, byte);

        if SHOULD_LOG {
            println!(
                "Pushing {} to stack at {}",
                byte,
                self.sp_base + self.sp as MemAddress
            );
        }
        self.sp -= 1;
    }

    fn st_pop(&mut self) -> Byte {
        self.sp += 1;

        let byte = self.byte_at(self.sp_base + self.sp as MemAddress);

        if SHOULD_LOG {
            println!(
                "Popping {} from stack at {}",
                byte,
                self.sp_base + self.sp as MemAddress
            );
        }
        byte
    }

    fn st_push_word(&mut self, word: Word) {
        let left = (word >> MPU::BYTE_WIDTH) as Byte;
        let right = word as Byte;

        self.st_push(left);
        self.st_push(right);
    }

    fn st_pop_word(&mut self) -> Word {
        let right = self.st_pop() as Word;
        let left = (self.st_pop() as Word) << MPU::BYTE_WIDTH;

        let combined = left | right;

        combined
    }

    /// sets NEGATIVE or ZERO flag, depending on the given value
    fn flags_nz(&mut self, value: Byte) {
        // clear the flags
        self._clear_flags(ZERO | NEGATIVE);

        // set flags if necessary
        // self._set_flags(value);

        if value == 0 {
            self._set_flags(ZERO);
        } else if value & NEGATIVE == NEGATIVE {
            self._set_flags(NEGATIVE);
        }
    }

    // operations helpers

    fn _address_from_fn(&mut self, address_fn: Option<AddressFn>) -> Option<MemAddress> {
        let address: Option<MemAddress>;

        if address_fn.is_none() {
            address = None;
        } else {
            address = Some(address_fn.unwrap()(self))
        }
        address
    }

    fn _to_address_or_accumulator(&mut self, address: Option<MemAddress>, t_byte: Byte) {
        if address.is_none() {
            self.accu = t_byte;
        } else {
            self.memory.set_byte(address.unwrap(), t_byte);
        }
    }

    fn _from_address_or_accumulator(&mut self, address: Option<MemAddress>) -> Byte {
        if address.is_none() {
            self.accu
        } else {
            self.byte_at(address.unwrap())
        }
    }

    // operations

    fn op_ora(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        self.accu |= self.byte_at(address);
        self.flags_nz(self.accu)
    }

    fn op_asl(&mut self, address_fn: Option<AddressFn>) {
        let address = self._address_from_fn(address_fn);

        let mut t_byte = self._from_address_or_accumulator(address);

        self._clear_flags(CARRY | NEGATIVE | ZERO);

        if (t_byte & NEGATIVE) == NEGATIVE {
            self._set_flags(CARRY);
        }

        t_byte = (t_byte << 1) & self.byte_mask;

        if t_byte == 0 {
            self._set_flags(ZERO);
        } else {
            self._set_flags(t_byte & NEGATIVE);
        }

        if address.is_none() {
            self.accu = t_byte;
        } else {
            self.memory.set_byte(address.unwrap(), t_byte);
        }
    }

    fn op_lsr(&mut self, address_fn: Option<AddressFn>) {
        let address = self._address_from_fn(address_fn);

        let mut t_byte = self._from_address_or_accumulator(address);

        self._clear_flags(CARRY | NEGATIVE | ZERO);
        self._set_flags(CARRY);

        t_byte = t_byte >> 1;

        if t_byte == 0 {
            self._set_flags(ZERO);
        }

        self._to_address_or_accumulator(address, t_byte);
    }

    /// generic implementation for branching when flag is not set
    fn op_bcl(&mut self, flag: Byte) {
        MPU::_validate_flag_argument(&flag);

        if !self._is_flag_set(flag) {
            // flag not set, so set the program counter to the address the program-counter points to
            self.branch_rel_addr();
        } else {
            // flag is set, so skip the instruction and set the program-counter forward
            self.pc = self.pc.wrapping_add(1);
        }
    }

    fn _is_flag_set(&mut self, flag: Byte) -> bool {
        self.flags & flag == flag
    }

    fn _validate_flag_argument(flag: &Byte) {
        if ![NEGATIVE, OVERFLOW, ZERO, CARRY].contains(&flag) {
            panic!("Relative Branch Jump called with unknown flag.")
        }
    }

    /// generic implementation for branching when flag is set, see also `op_bcl`
    fn op_bst(&mut self, flag: Byte) {
        MPU::_validate_flag_argument(&flag);

        if self._is_flag_set(flag) {
            self.branch_rel_addr()
        } else {
            self.pc = self.pc.wrapping_add(1);
        }
    }

    /// generic implementation to clear flag(s)
    fn op_clr(&mut self, flag: Byte) {
        self._clear_flags(flag);
    }

    /// generic implementation to set flag(s)
    fn op_set(&mut self, flag: Byte) {
        self._set_flags(flag);
    }

    fn op_and(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        self.accu &= self.byte_at(address);

        self.flags_nz(self.accu);
    }

    fn op_bit(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        let t_byte = self.byte_at(address);

        self._clear_flags(NEGATIVE | OVERFLOW | ZERO);

        if self.accu & t_byte == 0 {
            self._set_flags(ZERO);
        }

        self._set_flags(t_byte & (NEGATIVE | OVERFLOW));
    }

    fn op_rol(&mut self, address_fn: Option<AddressFn>) {
        let address = self._address_from_fn(address_fn);
        let mut t_byte = self._from_address_or_accumulator(address);

        if self._is_flag_set(CARRY) {
            if t_byte & NEGATIVE != NEGATIVE {
                self._clear_flags(CARRY);
            }
        } else {
            if t_byte & NEGATIVE == NEGATIVE {
                self._set_flags(CARRY);
            }

            t_byte = t_byte << 1;
        }

        t_byte &= self.byte_mask;

        self.flags_nz(t_byte);

        self._to_address_or_accumulator(address, t_byte);
    }

    fn op_eor(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        self.accu ^= self.byte_at(address);

        self.flags_nz(self.accu);
    }

    fn op_adc(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        let data = self.byte_at(address);

        if self._is_flag_set(DECIMAL) {
            self._add_bcd_mode(data);
        } else {
            self._add_bin_mode(data);
        }
    }

    fn _add_bcd_mode(&mut self, to_add: Byte) {
        let mut half_carry = 0;
        let mut decimal_carry = 0;

        let mut adjust_0 = 0;
        let mut adjust_1 = 0;

        let mut nibble_0 = (to_add & 0b0000_1111) + (self.accu & 0b0000_1111);

        if self._is_flag_set(CARRY) {
            nibble_0 += CARRY;
        }

        // if the higher nibble is larger than 9 (i.e. 10)
        if nibble_0 > 9 {
            debug_assert!(
                nibble_0 == 10,
                "nibble cannot be larger than 10 in BCD mode"
            );

            // set adjust to 6 to get the decimal 10 to hexadecimal 0x10
            adjust_0 = 6;

            // set carry flag for the overflow
            half_carry = 1;
        }

        let mut nibble_1 = ((to_add >> 4) & 0b0000_1111) + ((self.accu >> 4) & 0b0000_1111);
        nibble_1 += half_carry;

        // if the higher nibble is larger than 9 (i.e. 10)
        if nibble_1 > 9 {
            debug_assert!(
                nibble_1 == 10,
                "nibble cannot be larger than 10 in BCD mode"
            );

            // set adjust to 6 to get the decimal 10 to hexadecimal 0x10
            adjust_1 = 6;

            // set carry flag for the overflow
            decimal_carry = 1;
        }

        // add together the bcd nibbles
        nibble_0 &= 0b0000_1111;
        nibble_1 &= 0b0000_1111;

        let sum_in_bcd = (nibble_1 << 4) + nibble_0;

        // adjust further before adding to accumulator
        nibble_0 = (nibble_0 + adjust_0) & 0b0000_1111;
        nibble_1 = (nibble_1 + adjust_1) & 0b0000_1111;

        self._clear_flags(CARRY | NEGATIVE | OVERFLOW | ZERO);

        if sum_in_bcd == 0 {
            self._set_flags(ZERO);
        } else {
            // set negative flag, if the bcd sum has the negative flag set
            self._set_flags(sum_in_bcd & NEGATIVE);
        }

        if decimal_carry == 1 {
            self._set_flags(CARRY);
        }

        if (!(self.accu ^ to_add) & (self.accu ^ sum_in_bcd)) & NEGATIVE == NEGATIVE {
            self._set_flags(OVERFLOW)
        }

        self.accu = (nibble_1 << 4) + nibble_0;
    }

    fn _add_bin_mode(&mut self, data: Byte) {
        // to check for overflow, we need to have result be a 16 bit integer, until we cast it
        // down to a byte
        let mut result = data as u16 + self.accu as u16;

        if self._is_flag_set(CARRY) {
            result += 1;
        }

        self._clear_flags(CARRY | NEGATIVE | OVERFLOW | ZERO);

        if (!(self.accu ^ data) & (self.accu ^ result as Byte)) & NEGATIVE == NEGATIVE {
            self._set_flags(OVERFLOW);
        }

        if result > u8::MAX as u16 {
            self._set_flags(CARRY);

            result &= self.byte_mask as u16;
        }

        // cast it down to byte
        let result = result as Byte;

        self.flags_nz(result);

        self.accu = result;
    }

    fn op_ror(&mut self, address_fn: Option<AddressFn>) {
        let address = self._address_from_fn(address_fn);
        let mut t_byte = self._from_address_or_accumulator(address);

        let old_carry_flag = self.flags & CARRY;
        let lsb = t_byte & 0b0000_0001;

        let new_msb = old_carry_flag << 7;
        let new_carry_flag = lsb;

        t_byte = (t_byte >> 1) | new_msb;

        if new_carry_flag == 1 {
            self._set_flags(CARRY);
        } else {
            self._clear_flags(CARRY);
        }

        self.flags_nz(t_byte);

        self._to_address_or_accumulator(address, t_byte)
    }

    fn op_sta(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);
        self.memory.set_byte(address, self.accu);
    }

    fn op_sty(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);
        self.memory.set_byte(address, self.y);
    }

    fn op_stx(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);
        self.memory.set_byte(address, self.x);
    }

    fn op_cmpr(&mut self, address_fn: AddressFn, register: Register) {
        let address = address_fn(self);

        let t_byte = self.byte_at(address);

        self._clear_flags(CARRY | NEGATIVE | ZERO);

        if register >= t_byte {
            self._set_flags(CARRY);
        }
        if register == t_byte {
            self._set_flags(ZERO);
        }
        if (register.wrapping_sub(t_byte) & NEGATIVE) == NEGATIVE {
            self.flags |= NEGATIVE;
        }
    }

    fn op_sbc(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        let data = self.byte_at(address);

        if self._is_flag_set(DECIMAL) {
            self._sub_bcd_mode(data);
        } else {
            self._sub_bin_mode(data);
        }
    }

    fn _sub_bcd_mode(&mut self, data: Byte) {
        let mut half_carry = 1;
        let mut decimal_carry = 0;
        let mut adjust_0 = 0;
        let mut adjust_1 = 0;

        let mut nibble_0 = (self.accu & 0b0000_1111) + (!data & 0b0000_1111);

        if self._is_flag_set(CARRY) {
            nibble_0 += 1;
        }

        if nibble_0 <= 0b0000_1111 {
            half_carry = 0;
            adjust_0 = 10;
        }

        let mut nibble_1 =
            ((self.accu >> 4) & 0b0000_1111) + ((!data >> 4) & 0b0000_1111) + half_carry;

        if nibble_1 <= 0b0000_1111 {
            adjust_1 = 10 << 4;
        }

        let mut sum_in_bcd = self.accu as u16 + (!data & self.byte_mask) as u16;

        if self._is_flag_set(CARRY) {
            sum_in_bcd += 1;
        }

        if sum_in_bcd > self.byte_mask as u16 {
            decimal_carry = 1;
        }

        let sum_in_bcd = sum_in_bcd as Byte;

        nibble_0 = (sum_in_bcd + adjust_0) & 0b0000_1111;
        nibble_1 = ((sum_in_bcd + adjust_1) >> 4) & 0b0000_1111;

        self._clear_flags(CARRY | NEGATIVE | OVERFLOW | ZERO);

        if sum_in_bcd == 0 {
            self._set_flags(ZERO);
        } else {
            self._set_flags(sum_in_bcd & NEGATIVE)
        }

        if decimal_carry == 1 {
            self._set_flags(CARRY);
        }

        if ((self.accu ^ data) & (self.accu ^ sum_in_bcd)) & NEGATIVE == NEGATIVE {
            self._set_flags(OVERFLOW);
        }

        self.accu = (nibble_1 << 4) + nibble_0;
    }

    fn _sub_bin_mode(&mut self, data: Byte) {
        let mut result: Byte;
        let carry_first: bool;
        let carry_second: bool;

        (result, carry_first) = self.accu.carrying_add(!data, false);

        if self._is_flag_set(CARRY) {
            (result, carry_second) = result.carrying_add(1, false);
        } else {
            carry_second = false;
        }

        self._clear_flags(CARRY | NEGATIVE | OVERFLOW | ZERO);

        if (((self.accu ^ data) & (self.accu ^ result)) & NEGATIVE) == NEGATIVE {
            self._set_flags(OVERFLOW);
        }

        let data = result;
        if data == 0 {
            self._set_flags(ZERO);
        }

        if carry_first || carry_second {
            self._set_flags(CARRY);
        }

        self._set_flags(data & NEGATIVE);
        self.accu = data;
    }

    fn op_decr(&mut self, address_fn: Option<AddressFn>) {
        let address = self._address_from_fn(address_fn);
        let mut t_byte = self._from_address_or_accumulator(address);

        self._clear_flags(ZERO | NEGATIVE);

        t_byte = t_byte.wrapping_sub(1);

        self.flags_nz(t_byte);

        self._to_address_or_accumulator(address, t_byte);
    }

    fn op_incr(&mut self, address_fn: Option<AddressFn>) {
        let address = self._address_from_fn(address_fn);
        let mut t_byte = self._from_address_or_accumulator(address);

        self._clear_flags(ZERO | NEGATIVE);

        t_byte = t_byte.wrapping_add(1);

        self.flags_nz(t_byte);

        self._to_address_or_accumulator(address, t_byte);
    }

    fn op_lda(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        self.accu = self.byte_at(address);

        self.flags_nz(self.accu);
    }

    fn op_ldy(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        self.y = self.byte_at(address);
        self.flags_nz(self.y);
    }

    fn op_ldx(&mut self, address_fn: AddressFn) {
        let address = address_fn(self);

        self.x = self.byte_at(address);
        self.flags_nz(self.x);
    }

    // instructions

    fn inst_not_implemented(&mut self) {
        self.pc = self.pc.wrapping_add(1);
    }

    fn _log_op_code(
        &mut self,
        op_fn: fn(&mut MPU),
        op_code: u8,
        name: &str,
        cycles: u8,
        extra_cycles: u8,
    ) {
        let dis_asm = DisAsm {
            instruction_code: String::from(name),
        };

        self.disassemble[op_code as usize] = dis_asm;

        self.instruct[op_code as usize] = op_fn;
        self.cycle_time[op_code as usize] = cycles;

        self.extra_cycles[op_code as usize] = extra_cycles;
    }

    fn inst_0x00(&mut self) {
        // program counter has already been increased by one
        let pc = self.pc.wrapping_add(1);

        self.st_push_word(pc);

        self._set_flags(BREAK);
        self.st_push(self.flags | BREAK | UNUSED);

        self._set_flags(INTERRUPT);
        self.pc = self.word_at(MPU::IRQ)
    }

    fn inst_0x01(&mut self) {
        self.op_ora(MPU::indirect_x_addr);
        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x05(&mut self) {
        self.op_ora(MPU::zero_page_addr);
        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x06(&mut self) {
        self.op_asl(Some(MPU::zero_page_addr));
        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x08(&mut self) {
        self.st_push(self.pc as Byte | BREAK | UNUSED)
    }

    fn inst_0x09(&mut self) {
        self.op_ora(MPU::program_counter);
        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x0a(&mut self) {
        self.op_asl(None);
    }

    fn inst_0x0d(&mut self) {
        self.op_ora(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x0e(&mut self) {
        self.op_asl(Some(MPU::absolute_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x10(&mut self) {
        self.op_bcl(NEGATIVE);
    }

    fn inst_0x11(&mut self) {
        self.op_ora(MPU::indirect_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x15(&mut self) {
        self.op_ora(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x16(&mut self) {
        self.op_asl(Some(MPU::zero_page_x_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x18(&mut self) {
        self.op_clr(CARRY);
    }

    fn inst_0x19(&mut self) {
        self.op_ora(MPU::absolute_y_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x1d(&mut self) {
        self.op_ora(MPU::absolute_x_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x1e(&mut self) {
        self.op_asl(Some(MPU::absolute_x_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x20(&mut self) {
        self.st_push_word(self.pc.wrapping_add(1));
        self.pc = self.word_at(self.pc)
    }

    fn inst_0x21(&mut self) {
        self.op_and(MPU::indirect_x_addr);
        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x24(&mut self) {
        self.op_bit(MPU::zero_page_addr);
        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x25(&mut self) {
        self.op_and(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x26(&mut self) {
        self.op_rol(Some(MPU::zero_page_addr));
        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x28(&mut self) {
        self.flags = self.st_pop() | BREAK | UNUSED;
    }

    fn inst_0x29(&mut self) {
        self.op_and(MPU::program_counter);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x2a(&mut self) {
        self.op_rol(None);
    }

    fn inst_0x2c(&mut self) {
        self.op_bit(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x2d(&mut self) {
        self.op_and(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x2e(&mut self) {
        self.op_rol(Some(MPU::absolute_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x30(&mut self) {
        self.op_bst(NEGATIVE);
    }

    fn inst_0x31(&mut self) {
        self.op_and(MPU::indirect_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x35(&mut self) {
        self.op_and(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x36(&mut self) {
        self.op_rol(Some(MPU::zero_page_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x38(&mut self) {
        self.op_set(CARRY);
    }

    fn inst_0x39(&mut self) {
        self.op_and(MPU::absolute_y_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x3d(&mut self) {
        self.op_and(MPU::absolute_x_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x3e(&mut self) {
        self.op_rol(Some(MPU::absolute_x_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x40(&mut self) {
        self.flags = self.st_pop() | BREAK | UNUSED;

        self.pc = self.st_pop_word();
    }

    fn inst_0x41(&mut self) {
        self.op_eor(MPU::indirect_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x45(&mut self) {
        self.op_eor(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x46(&mut self) {
        self.op_lsr(Some(MPU::zero_page_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x48(&mut self) {
        self.st_push(self.accu);
    }

    fn inst_0x49(&mut self) {
        self.op_eor(MPU::program_counter);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x4a(&mut self) {
        self.op_lsr(None);
    }

    fn inst_0x4c(&mut self) {
        self.pc = self.word_at(self.pc);
    }

    fn inst_0x4d(&mut self) {
        self.op_eor(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x4e(&mut self) {
        self.op_lsr(Some(MPU::absolute_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x50(&mut self) {
        self.op_bcl(OVERFLOW);
    }

    fn inst_0x51(&mut self) {
        self.op_eor(MPU::indirect_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x55(&mut self) {
        self.op_eor(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x56(&mut self) {
        self.op_lsr(Some(MPU::zero_page_x_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x58(&mut self) {
        self.op_clr(INTERRUPT);
    }

    fn inst_0x59(&mut self) {
        self.op_eor(MPU::absolute_y_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x5d(&mut self) {
        self.op_eor(MPU::absolute_x_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x5e(&mut self) {
        self.op_lsr(Some(MPU::absolute_x_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x60(&mut self) {
        self.pc = self.st_pop_word();

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x61(&mut self) {
        self.op_adc(MPU::indirect_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x65(&mut self) {
        self.op_adc(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x66(&mut self) {
        self.op_ror(Some(MPU::zero_page_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x68(&mut self) {
        self.accu = self.st_pop();

        self.flags_nz(self.accu);
    }

    fn inst_0x69(&mut self) {
        self.op_adc(MPU::program_counter);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x6a(&mut self) {
        self.op_ror(None);
    }

    fn inst_0x6c(&mut self) {
        let new_pc = self.word_at(self.pc);
        self.pc = self.wrap_at(new_pc);
    }

    fn inst_0x6d(&mut self) {
        self.op_adc(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x6e(&mut self) {
        self.op_ror(Some(MPU::absolute_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x70(&mut self) {
        self.op_bst(OVERFLOW);
    }

    fn inst_0x71(&mut self) {
        self.op_adc(MPU::indirect_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x75(&mut self) {
        self.op_adc(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x76(&mut self) {
        self.op_ror(Some(MPU::zero_page_x_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x78(&mut self) {
        self.op_set(INTERRUPT);
    }

    fn inst_0x79(&mut self) {
        self.op_adc(MPU::absolute_y_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x7d(&mut self) {
        self.op_adc(MPU::absolute_x_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x7e(&mut self) {
        self.op_ror(Some(MPU::absolute_x_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x81(&mut self) {
        self.op_sta(MPU::indirect_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x84(&mut self) {
        self.op_sty(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x85(&mut self) {
        self.op_sta(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x86(&mut self) {
        self.op_stx(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x88(&mut self) {
        self.y = self.y.wrapping_sub(1) & self.byte_mask;

        self.flags_nz(self.y);
    }

    fn inst_0x8a(&mut self) {
        self.accu = self.x;

        self.flags_nz(self.accu);
    }

    fn inst_0x8c(&mut self) {
        self.op_sty(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x8d(&mut self) {
        self.op_sta(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x8e(&mut self) {
        self.op_stx(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x90(&mut self) {
        self.op_bcl(CARRY);
    }

    fn inst_0x91(&mut self) {
        self.op_sta(MPU::indirect_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x94(&mut self) {
        self.op_sty(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x95(&mut self) {
        self.op_sta(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x96(&mut self) {
        self.op_stx(MPU::zero_page_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0x98(&mut self) {
        self.accu = self.y;

        self.flags_nz(self.accu);
    }

    fn inst_0x99(&mut self) {
        self.op_sta(MPU::absolute_y_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0x9a(&mut self) {
        let ram_address = self.byte_at(self.pc);

        if ram_address == 0x46 {
            self.c000_bank = self.memory[MEM_PAGE_C000];
            self.memory.load_c000_page(self.c000_bank)
        } else if ram_address == 0x47 {
            self.a000_bank = self.memory[MEM_PAGE_A000];
            self.memory.load_a000_page(self.a000_bank)
        }

        // original 0x9a
        self.sp = self.x;
    }

    fn inst_0x9d(&mut self) {
        self.op_sta(MPU::absolute_x_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xa0(&mut self) {
        self.op_ldy(MPU::program_counter);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xa1(&mut self) {
        self.op_lda(MPU::indirect_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xa2(&mut self) {
        self.op_ldx(MPU::program_counter);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xa4(&mut self) {
        self.op_ldy(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xa5(&mut self) {
        self.op_lda(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xa6(&mut self) {
        self.op_ldx(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xa8(&mut self) {
        self.y = self.accu;

        self.flags_nz(self.y);
    }

    fn inst_0xa9(&mut self) {
        self.op_lda(MPU::program_counter);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xaa(&mut self) {
        self.x = self.accu;

        self.flags_nz(self.x);
    }

    fn inst_0xac(&mut self) {
        self.op_ldy(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xad(&mut self) {
        self.op_lda(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xae(&mut self) {
        self.op_ldx(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xb0(&mut self) {
        self.op_bst(CARRY);
    }

    fn inst_0xb1(&mut self) {
        self.op_lda(MPU::indirect_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xb4(&mut self) {
        self.op_ldy(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xb5(&mut self) {
        self.op_lda(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xb6(&mut self) {
        self.op_ldx(MPU::zero_page_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xb8(&mut self) {
        self.op_clr(OVERFLOW);
    }

    fn inst_0xb9(&mut self) {
        self.op_lda(MPU::absolute_y_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xba(&mut self) {
        self.x = self.sp;

        self.flags_nz(self.x);
    }

    fn inst_0xbc(&mut self) {
        self.op_ldy(MPU::absolute_x_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xbd(&mut self) {
        self.op_lda(MPU::absolute_x_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xbe(&mut self) {
        self.op_ldx(MPU::absolute_y_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xc0(&mut self) {
        self.op_cmpr(MPU::program_counter, self.y);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xc1(&mut self) {
        self.op_cmpr(MPU::indirect_x_addr, self.accu);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xc4(&mut self) {
        self.op_cmpr(MPU::zero_page_addr, self.y);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xc5(&mut self) {
        self.op_cmpr(MPU::zero_page_addr, self.accu);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xc6(&mut self) {
        self.op_decr(Some(MPU::zero_page_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xc8(&mut self) {
        self.y = self.y.wrapping_add(1) & self.byte_mask;

        self.flags_nz(self.y);
    }

    fn inst_0xc9(&mut self) {
        self.op_cmpr(MPU::program_counter, self.accu);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xca(&mut self) {
        self.x = self.x.wrapping_sub(1) & self.byte_mask;

        self.flags_nz(self.x);
    }

    fn inst_0xcc(&mut self) {
        self.op_cmpr(MPU::absolute_addr, self.y);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xcd(&mut self) {
        self.op_cmpr(MPU::absolute_addr, self.accu);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xce(&mut self) {
        self.op_decr(Some(MPU::absolute_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xd0(&mut self) {
        self.op_bcl(ZERO);
    }

    fn inst_0xd1(&mut self) {
        self.op_cmpr(MPU::indirect_y_addr, self.accu);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xd5(&mut self) {
        self.op_cmpr(MPU::zero_page_x_addr, self.accu);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xd6(&mut self) {
        self.op_decr(Some(MPU::zero_page_x_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xd8(&mut self) {
        self.op_clr(DECIMAL);
    }

    fn inst_0xd9(&mut self) {
        self.op_cmpr(MPU::absolute_y_addr, self.accu);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xdd(&mut self) {
        self.op_cmpr(MPU::absolute_x_addr, self.accu);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xde(&mut self) {
        self.op_decr(Some(MPU::absolute_x_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xe0(&mut self) {
        self.op_cmpr(MPU::program_counter, self.x);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xe1(&mut self) {
        self.op_sbc(MPU::indirect_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xe4(&mut self) {
        self.op_cmpr(MPU::zero_page_addr, self.x);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xe5(&mut self) {
        self.op_sbc(MPU::zero_page_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xe6(&mut self) {
        self.op_incr(Some(MPU::zero_page_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xe8(&mut self) {
        self.x = self.x.wrapping_add(1) & self.byte_mask;

        self.flags_nz(self.x);
    }

    fn inst_0xe9(&mut self) {
        self.op_sbc(MPU::program_counter);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xea(&mut self) {}

    fn inst_0xec(&mut self) {
        self.op_cmpr(MPU::absolute_addr, self.x);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xed(&mut self) {
        self.op_sbc(MPU::absolute_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xee(&mut self) {
        self.op_incr(Some(MPU::absolute_addr));

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xf0(&mut self) {
        self.op_bst(ZERO);
    }

    fn inst_0xf1(&mut self) {
        self.op_sbc(MPU::indirect_y_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xf5(&mut self) {
        self.op_sbc(MPU::zero_page_x_addr);

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xf6(&mut self) {
        self.op_incr(Some(MPU::zero_page_x_addr));

        self.pc = self.pc.wrapping_add(1);
    }

    fn inst_0xf8(&mut self) {
        self.op_set(DECIMAL);
    }

    fn inst_0xf9(&mut self) {
        self.op_sbc(MPU::absolute_y_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xfd(&mut self) {
        self.op_sbc(MPU::absolute_x_addr);

        self.pc = self.pc.wrapping_add(2);
    }

    fn inst_0xfe(&mut self) {
        self.op_incr(Some(MPU::absolute_x_addr));

        self.pc = self.pc.wrapping_add(2);
    }
}

const ROM_LEVEL_LOAD_ENTRY: MemAddress = 0x891A;
const RAM_PLAYER_CURRENT: MemAddress = 0x0726;
const RAM_WORLD_NUMBER: MemAddress = 0x0727;

const RAM_PLAYER_SCREEN: MemAddress = 0x0077;
const RAM_PLAYER_X: MemAddress = 0x0079;
const RAM_PLAYER_Y: MemAddress = 0x0075;

pub const RAM_SCREEN_MEMORY_START: MemAddress = 0x6000;
pub const RAM_SCREEN_MEMORY_END: MemAddress = 0x7950;
const ROM_END_OBJECT_PARSING: MemAddress = 0x9934;
pub const RAM_LEVEL_TILESET: MemAddress = 0x070A;
const RAM_GRAPHICS_SET: MemAddress = 0x7EBD;
const RAM_OBJECT_PALETTE: MemAddress = 0x073A;
const RAM_ENEMY_PALETTE: MemAddress = 0x073B;
const ROM_LEVELLOAD_BY_TILESET: MemAddress = 0x9A1D;
const OFFSET_BY_OBJECT_SET_A000: u32 = 0x3C3F9;
const OFFSET_BY_OBJECT_SET_C000: u32 = 0x3C3E6;
const PAGE_A000_OFFSET: u32 = 0xA000;
const BASE_OFFSET: u32 = 0x10;
pub const RAM_LEVEL_START_LO: MemAddress = 0x61;
pub const RAM_LEVEL_START_HI: MemAddress = 0x62;
pub const RAM_ENEMY_START_LO: MemAddress = 0x67;
pub const RAM_ENEMY_START_HI: MemAddress = 0x68;
const RAM_PAGE_A000_INDEX: MemAddress = 0x0720;
const RAM_PAGE_C000_INDEX: MemAddress = 0x071F;

impl MPU {
    #[allow(dead_code)]
    fn load_from_world_map(&mut self, world: u8, pos: Position, max_steps: u32) -> ParsedLevel {
        self.start_pc = ROM_LEVEL_LOAD_ENTRY;

        self.memory.set_byte(RAM_PLAYER_CURRENT, 0); // Mario
        self.memory.set_byte(RAM_WORLD_NUMBER, world);

        self.memory.set_byte(RAM_PLAYER_SCREEN, pos.screen);
        self.memory.set_byte(RAM_PLAYER_X, pos.x << 4);
        self.memory.set_byte(RAM_PLAYER_Y, pos.y << 4);

        return self._load_level(max_steps);
    }

    pub fn load_from_address(
        &mut self,
        object_set_number: u8,
        level_position: u32,
        enemy_position: u32,
        max_steps: u32,
    ) -> ParsedLevel {
        self.start_pc = ROM_LEVELLOAD_BY_TILESET;

        let a000_bank_index_position =
            (OFFSET_BY_OBJECT_SET_A000 + object_set_number as u32) as usize;
        let c000_bank_index_position =
            (OFFSET_BY_OBJECT_SET_C000 + object_set_number as u32) as usize;

        let bank_index_for_object_set = self.memory.rom.data[a000_bank_index_position];
        let object_set_offset =
            (bank_index_for_object_set as u32) * PRG_BANK_SIZE - PAGE_A000_OFFSET;

        let level_offset = (level_position - object_set_offset - BASE_OFFSET) as MemAddress;

        self.memory[RAM_LEVEL_TILESET] = object_set_number;
        self.memory[RAM_LEVEL_START_LO] = (level_offset & 0xFF) as Byte;
        self.memory[RAM_LEVEL_START_HI] = (level_offset >> 8) as Byte;
        self.memory[RAM_ENEMY_START_LO] = (enemy_position & 0xFF) as Byte;
        self.memory[RAM_ENEMY_START_HI] = (enemy_position >> 8) as Byte;

        self.a000_bank = bank_index_for_object_set;
        self.memory[RAM_PAGE_A000_INDEX] = self.a000_bank;

        self.c000_bank = self.memory.rom.data[c000_bank_index_position];
        self.memory[RAM_PAGE_C000_INDEX] = self.c000_bank;

        self.memory.load_a000_page(self.a000_bank);
        self.memory.load_c000_page(self.c000_bank);

        let mut level = self._load_level(max_steps);

        let mut enemy_position = (enemy_position + 1) as usize;

        while self.memory.rom.data[enemy_position] != 0xFF {
            let enemy_bytes = self.memory.rom.data[enemy_position..enemy_position + 3].to_vec();

            level
                .parsed_enemies
                .push(ParsedEnemy::new(0x10, enemy_bytes, enemy_position as u32));

            enemy_position += 3;
        }

        return level;
    }

    fn _load_level(&mut self, max_steps: u32) -> ParsedLevel {
        self.reset();
        self.run_until(ROM_END_OBJECT_PARSING, max_steps);
        self._maybe_finish_parsing_last_object();

        return ParsedLevel {
            object_set_num: self.memory[RAM_LEVEL_TILESET],
            graphics_set_num: self.memory[RAM_GRAPHICS_SET],
            object_palette_num: self.memory[RAM_OBJECT_PALETTE],
            enemy_palette_num: self.memory[RAM_ENEMY_PALETTE],
            screen_memory: self.memory[RAM_SCREEN_MEMORY_START..RAM_SCREEN_MEMORY_END].to_vec(),
            parsed_objects: self.objects.to_owned(),
            parsed_enemies: vec![],
        };
    }

    fn run_until(&mut self, target_address: MemAddress, max_steps: u32) {
        let mut max_steps = max_steps;

        if max_steps == 0 {
            max_steps = u32::MAX;
        }

        while self.pc != target_address {
            self.do_step();

            if self.step_count > max_steps {
                panic!("Max steps reached");
            }
        }
    }

    fn do_step(&mut self) {
        self.step_count += 1;

        if self.pc == 0x98EE {
            self._maybe_finish_parsing_last_object();
            self._start_parsing_next_object();

            // if self.should_log
        } else if self.pc == ROM_END_OBJECT_PARSING {
            self._maybe_finish_parsing_last_object();
        }

        self.step();
    }

    fn _start_parsing_next_object(&mut self) {
        self.memory.start_new_object();
    }

    fn _maybe_finish_parsing_last_object(&mut self) {
        match self.memory.maybe_finish_object() {
            Some(object) => self.objects.push(object),
            None => (),
        }
    }
}
