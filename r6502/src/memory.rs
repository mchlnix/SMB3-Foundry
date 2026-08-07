use crate::devices::mpu6502::{
    Byte, MemAddress, RAM_LEVEL_START_HI, RAM_LEVEL_START_LO, RAM_LEVEL_TILESET,
    RAM_SCREEN_MEMORY_END, RAM_SCREEN_MEMORY_START, RomAddress,
};
use std::collections::HashMap;
use std::ops::Range;
use std::ops::{Index, IndexMut};

const BASE_OFFSET: RomAddress = 0x0010;
pub const PRG_BANK_SIZE: u32 = 0x2000;

const VANILLA_PRG_COUNT: u8 = 32;
const VANILLA_ROM_SIZE: u32 = VANILLA_PRG_COUNT as u32 * PRG_BANK_SIZE;

const MEM_Screen_Start_AddressL: MemAddress = 0x8000;
const MEM_Screen_Start_AddressH: MemAddress = 0x8001;

const MEM_RANDOM_POOL_START: usize = 0x0781;
const MEM_RESET_LATCH: usize = 0x7964;

use crate::object::ParsedLevelObject;
use std::fmt;

pub struct ReadObserver(Box<dyn Fn(MemAddress, Byte)>);
pub struct WriteObserver(pub(crate) Box<dyn Fn(MemAddress, Byte)>);

impl fmt::Debug for ReadObserver {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("ReadObserver")
    }
}

impl fmt::Debug for WriteObserver {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("WriteObserver")
    }
}
pub type RomData = Vec<Byte>;

#[derive(Debug)]
pub struct Rom {
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
pub struct Memory {
    pub rom: Rom,
    pub memory: Vec<Byte>,
    read_observers: HashMap<Range<MemAddress>, ReadObserver>,
    write_observers: HashMap<Range<MemAddress>, WriteObserver>,

    current_object: Option<ParsedLevelObject>,
}

impl Memory {
    pub fn new(rom: Rom) -> Self {
        let mut memory = Self {
            rom,
            memory: vec![0; 0x10000],
            read_observers: HashMap::new(),
            write_observers: HashMap::new(),
            current_object: None,
        };

        memory.memory[MEM_RANDOM_POOL_START] = 0x88;
        memory.memory[MEM_RESET_LATCH] = 0x5A;

        let last_prg_index = memory.rom.prg_bank_count - 1;

        memory._load_bank(last_prg_index - 1, 0x8000 as MemAddress);
        memory._load_bank(last_prg_index, 0xE000 as MemAddress);

        return memory;
    }

    pub fn load_a000_page(&mut self, prg_index: Byte) {
        self._load_bank(prg_index, 0xA000);
    }

    pub fn load_c000_page(&mut self, prg_index: Byte) {
        self._load_bank(prg_index, 0xC000);
    }

    fn _load_bank(&mut self, prg_index: Byte, address: MemAddress) {
        let prg_bank_position = BASE_OFFSET + PRG_BANK_SIZE * prg_index as u32;

        let start = address as usize;
        let end = (address as u32 + PRG_BANK_SIZE) as usize;

        self.memory[start..end].copy_from_slice(&self.rom.read(prg_bank_position, PRG_BANK_SIZE));
    }

    pub fn add_read_observer(&mut self, range: Range<MemAddress>, observer: ReadObserver) {
        self.read_observers.insert(range, observer);
    }

    pub fn add_write_observer(&mut self, range: Range<MemAddress>, observer: WriteObserver) {
        self.write_observers.insert(range, observer);
    }

    pub fn remove_write_observer(&mut self, range: Range<MemAddress>) {
        self.write_observers.remove(&range);
    }

    pub fn set_byte(&mut self, address: MemAddress, value: Byte) {
        for (range, observer) in &self.write_observers {
            if range.contains(&address) {
                observer.0(address, value);
            }
        }

        if [MEM_Screen_Start_AddressL, MEM_Screen_Start_AddressH].contains(&address) {
            // ignore these addresses, since they seem to access the Mapper, but actually overwrite
            // a pointer to the screen memory
            return;
        }

        self.memory[address as usize] = value;
    }

    pub(crate) fn get_from_range(&self, address_range: Range<MemAddress>) -> Vec<Byte> {
        let mut return_value = vec![];

        for address in address_range {
            return_value.push(self[address]);
        }

        return return_value;
    }

    pub fn start_new_object(&mut self) {
        let level_pointer: MemAddress = ((self[RAM_LEVEL_START_HI] as MemAddress) << 8)
            + (self[RAM_LEVEL_START_LO] as MemAddress);
        let object_bytes = self.get_from_range(level_pointer..level_pointer + 3);

        let object_set_number = self[RAM_LEVEL_TILESET];

        let parsed_object = ParsedLevelObject::new(object_set_number, object_bytes, level_pointer);

        self.current_object = Some(parsed_object);
    }

    pub fn maybe_finish_object(&mut self) -> Option<ParsedLevelObject> {
        let mut object = self.current_object.clone();

        match object {
            Some(ref mut parsed_object) => {
                self._finish_object(parsed_object);
            }
            None => {}
        }

        return object;
    }

    fn _finish_object(&self, object: &mut ParsedLevelObject) {
        let level_pointer: MemAddress = ((self[RAM_LEVEL_START_HI] as MemAddress) << 8)
            + (self[RAM_LEVEL_START_LO] as MemAddress);
        let object_len = level_pointer - object.pos_in_memory;

        assert!([0, 3, 4].contains(&object_len));

        if object_len == 4 {
            object.object_bytes.push(self[level_pointer - 1]);
        }
    }

    fn _screen_memory_watcher(&mut self, address: MemAddress, value: Byte) {
        match self.current_object {
            Some(ref mut object) => {
                assert!((RAM_SCREEN_MEMORY_START..RAM_SCREEN_MEMORY_END).contains(&address));

                let tile_address = address - RAM_SCREEN_MEMORY_START;

                object.tiles_in_level.push((tile_address, value));
            }
            None => {} // Probably a call for the default background graphics
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

        for (range, observer) in &self.read_observers {
            if range.contains(&address) {
                observer.0(address, *return_value);
            }
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
