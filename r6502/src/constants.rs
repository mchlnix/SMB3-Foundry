use crate::devices::mpu6502::MemAddress;
use crate::devices::mpu6502::RomAddress;

pub const BASE_OFFSET: RomAddress = 0x10;

pub const BYTE_WIDTH: u32 = 8;

pub const OBJECT_ID_RANGES: [&[(u8, &[u8])]; 17] = [
    &[],                                                           // 0
    &[(0, &[0x04]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 1
    &[
        (0, &[0x00, 0x06]),
        (1, &[0x90, 0xC0, 0xE0]),
        (2, &[0x07, 0x10]),
    ], // 2
    &[(0, &[0x0F]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 3
    &[(0, &[0x05]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 4
    &[(1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])],               // 5
    &[(0, &[0x0A]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 6
    &[(0, &[0x04]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 7
    &[(0, &[0x0A]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 8
    &[(0, &[0x0B]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 9
    &[(1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])],               // 10
    &[(1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])],               // 11
    &[(0, &[0x05]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 12
    &[(1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])],               // 13
    &[(0, &[0x0F]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 14
    &[(0, &[0x04]), (1, &[0x90, 0xC0, 0xE0]), (2, &[0x07, 0x10])], // 15
    &[
        (0, &[0x08, 0xD5]),
        (1, &[0x90, 0xC0, 0xE0]),
        (2, &[0x07, 0x10]),
    ], // 16
];
pub const LEVEL_HEADER_LENGTH: u32 = 9; // bytes
pub const PRG_BANK_SIZE: u32 = 0x2000;
pub const VANILLA_PRG_COUNT: u8 = 32;
pub const MEM_SCREEN_START_ADDRESS_LO: MemAddress = 0x8000;
pub const MEM_SCREEN_START_ADDRESS_HI: MemAddress = 0x8001;
pub const MEM_RANDOM_POOL_START: usize = 0x0781;
pub const MEM_RESET_LATCH: usize = 0x7964;
pub const MEM_PAGE_C000: MemAddress = 0x071F;
pub const MEM_PAGE_A000: MemAddress = 0x0720;

pub const RAM_SCREEN_MEMORY_START: MemAddress = 0x6000;
pub const RAM_SCREEN_MEMORY_END: MemAddress = 0x7950;
pub const RAM_LEVEL_TILESET: MemAddress = 0x070A;
pub const ROM_LEVELLOAD_BY_TILESET: MemAddress = 0x9A1D;
pub const RAM_LEVEL_START_LO: MemAddress = 0x61;
pub const RAM_LEVEL_START_HI: MemAddress = 0x62;
pub const RAM_ENEMY_START_LO: MemAddress = 0x67;
pub const RAM_ENEMY_START_HI: MemAddress = 0x68;

// processor flags
pub const NEGATIVE: u8 = 0b1000_0000;
pub const OVERFLOW: u8 = 0b0100_0000;
pub const UNUSED: u8 = 0b0010_0000;
pub const BREAK: u8 = 0b0001_0000;
pub const DECIMAL: u8 = 0b0000_1000;
pub const INTERRUPT: u8 = 0b0000_0100;
pub const ZERO: u8 = 0b0000_0010;
pub const CARRY: u8 = 0b0000_0001;

pub const ROM_LEVEL_LOAD_ENTRY: MemAddress = 0x891A;
pub const RAM_PLAYER_CURRENT: MemAddress = 0x0726;
pub const RAM_WORLD_NUMBER: MemAddress = 0x0727;
pub const RAM_PLAYER_SCREEN: MemAddress = 0x0077;
pub const RAM_PLAYER_X: MemAddress = 0x0079;
pub const RAM_PLAYER_Y: MemAddress = 0x0075;
pub const ROM_END_OBJECT_PARSING: MemAddress = 0x9934;
pub const RAM_GRAPHICS_SET: MemAddress = 0x7EBD;
pub const RAM_OBJECT_PALETTE: MemAddress = 0x073A;
pub const RAM_ENEMY_PALETTE: MemAddress = 0x073B;
pub const OFFSET_BY_OBJECT_SET_A000: RomAddress = 0x3C3F9;
pub const OFFSET_BY_OBJECT_SET_C000: RomAddress = 0x3C3E6;
pub const PAGE_A000_OFFSET: u32 = 0xA000;
pub const RAM_PAGE_A000_INDEX: MemAddress = 0x0720;
pub const RAM_PAGE_C000_INDEX: MemAddress = 0x071F;
