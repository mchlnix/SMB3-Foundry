use crate::mpu6502::{Byte, MemAddress, RomAddress};
use std::ops::Range;
use std::ops::{Index, IndexMut};

use crate::constants::{
    BASE_OFFSET, MEM_RANDOM_POOL_START, MEM_RESET_LATCH, MEM_SCREEN_START_ADDRESS_HI,
    MEM_SCREEN_START_ADDRESS_LO, PRG_BANK_SIZE, RAM_LEVEL_START_HI, RAM_LEVEL_START_LO,
    RAM_LEVEL_TILESET, VANILLA_PRG_COUNT,
};
use crate::object::ParsedLevelObject;

pub type RomData = Vec<Byte>;

#[derive(Debug)]
pub(crate) struct Rom {
    pub data: RomData,
    pub prg_bank_count: u8,
}

impl Rom {
    fn read(&self, address: RomAddress, length: u32) -> &[Byte] {
        let normalised_address = self.normalise_address(address);

        let start = normalised_address as usize;
        let end = (normalised_address + length) as usize;

        return self.data.get(start..end).unwrap();
    }

    fn normalise_address(&self, address: RomAddress) -> RomAddress {
        if address < (BASE_OFFSET + (30 * PRG_BANK_SIZE)) {
            return address;
        }

        let added_bytes_count = (self.prg_bank_count - VANILLA_PRG_COUNT) as u32 * PRG_BANK_SIZE;

        return address + added_bytes_count;
    }
}

#[derive(Debug)]
pub(crate) struct Memory {
    pub rom: Rom,
    pub memory: Vec<Byte>,

    current_object: Option<ParsedLevelObject>,
}

impl Memory {
    pub(crate) fn new(rom: Rom) -> Self {
        let mut memory = Self {
            rom,
            memory: vec![0; 0x10000],
            current_object: None,
        };

        memory.memory[MEM_RANDOM_POOL_START] = 0x88;
        memory.memory[MEM_RESET_LATCH] = 0x5A;

        let last_prg_index = memory.rom.prg_bank_count - 1;

        memory.load_bank(last_prg_index - 1, 0x8000 as MemAddress);
        memory.load_bank(last_prg_index, 0xE000 as MemAddress);

        return memory;
    }

    pub(crate) fn load_a000_page(&mut self, prg_index: Byte) {
        self.load_bank(prg_index, 0xA000);
    }

    pub(crate) fn load_c000_page(&mut self, prg_index: Byte) {
        self.load_bank(prg_index, 0xC000);
    }

    fn load_bank(&mut self, prg_index: Byte, address: MemAddress) {
        let prg_bank_position = BASE_OFFSET + PRG_BANK_SIZE * prg_index as u32;

        let start = address as usize;
        let end = (address as u32 + PRG_BANK_SIZE) as usize;

        self.memory[start..end].copy_from_slice(&self.rom.read(prg_bank_position, PRG_BANK_SIZE));
    }

    pub(crate) fn set_byte(&mut self, address: MemAddress, value: Byte) {
        if [MEM_SCREEN_START_ADDRESS_LO, MEM_SCREEN_START_ADDRESS_HI].contains(&address) {
            // ignore these addresses, since they seem to access the Mapper, but actually overwrite
            // a pointer to the screen memory
            return;
        }

        self.memory[address as usize] = value;
    }

    pub fn get_from_range(&self, address_range: Range<MemAddress>) -> Vec<Byte> {
        let mut return_value = vec![];

        for address in address_range {
            return_value.push(self[address]);
        }

        return return_value;
    }

    pub(crate) fn start_new_object(&mut self) {
        let level_pointer: MemAddress = ((self[RAM_LEVEL_START_HI] as MemAddress) << 8)
            + (self[RAM_LEVEL_START_LO] as MemAddress);
        let object_bytes = self.get_from_range(level_pointer..level_pointer + 3);

        let object_set_number = self[RAM_LEVEL_TILESET];

        let parsed_object = ParsedLevelObject::new(object_set_number, object_bytes, level_pointer);

        self.current_object = Some(parsed_object);
    }

    pub(crate) fn maybe_finish_object(&mut self) -> Option<ParsedLevelObject> {
        let mut object = self.current_object.clone();

        match object {
            Some(ref mut parsed_object) => {
                self.finish_object(parsed_object);
            }
            None => {}
        }

        return object;
    }

    fn finish_object(&self, object: &mut ParsedLevelObject) {
        let level_pointer: MemAddress = ((self[RAM_LEVEL_START_HI] as MemAddress) << 8)
            + (self[RAM_LEVEL_START_LO] as MemAddress);
        let object_len = level_pointer - object.pos_in_memory;

        assert!([0, 3, 4].contains(&object_len));

        if object_len == 4 {
            object.object_bytes.push(self[level_pointer - 1]);
        }
    }
}

impl Index<MemAddress> for Memory {
    type Output = Byte;
    fn index(&self, address: MemAddress) -> &Self::Output {
        let return_value: &Byte;

        if address == 0x10 {
            return_value = &(0b1000_0000 as Byte);
        } else {
            return_value = &self.memory[address as usize];
        }

        return &return_value;
    }
}

impl Index<Range<MemAddress>> for Memory {
    type Output = [Byte];
    fn index(&self, address_range: Range<MemAddress>) -> &Self::Output {
        return &self.memory[address_range.start as usize..address_range.end as usize];
    }
}

impl IndexMut<MemAddress> for Memory {
    fn index_mut(&mut self, address: MemAddress) -> &mut Self::Output {
        return &mut self.memory[address as usize];
    }
}
