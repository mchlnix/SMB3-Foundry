use crate::types::{Byte, Index, NormalizedAddress, Offset, RawAddress};
use pyo3::{pyclass, pymethods};
use crate::labels::_Labels;

/// A ROM that wasn't extended fits 32 PRG Banks.
pub const VANILLA_PRG_COUNT: usize = 32;

/// A PRG Bank takes up 0x2000 bytes.
pub const PRG_BANK_SIZE: usize = 0x2000;

/// The size of all PRG Banks in a non-extended ROM is 0x40000 bytes.
pub const VANILLA_PRG_SIZE: usize = PRG_BANK_SIZE * VANILLA_PRG_COUNT;

/// A PRG Unit, as encoded in the ROM header, fits two PRG Banks.
const PRG_BANKS_PER_UNIT: usize = 2;
pub const PRG_UNIT_SIZE: usize = PRG_BANK_SIZE * PRG_BANKS_PER_UNIT;

pub const CHR_UNIT_SIZE: usize = 0x2000;
pub const ROM_HEADER_LENGTH: usize = 0x10;

pub const TSA_OS_LIST: RawAddress = RawAddress(0x3C3F9); // Label, Constant

pub const WORLD_MAP_OBJECT_SET_INDEX: Index = Index(0);
pub const WORLD_MAP_TSA_INDEX: u8 = 12;
pub const BASE_OFFSET: Offset = Offset(ROM_HEADER_LENGTH as u16);
pub const OFFSET_SIZE: usize = 2;
pub const AIRSHIP_TRAVEL_SET_COUNT: usize = 3;
pub const AIRSHIP_TRAVEL_SET_SIZE: usize = 6;

const TSA_TABLE_SIZE: usize = 0x400;

#[pyclass]
pub struct INESHeader {
    magic_bytes: [Byte; 4],
    prg_units: Byte,
    chr_units: Byte,
    flags: Byte,
    unused_flags: [Byte; 4],
    unused_pad: [Byte; 5],
}

#[pymethods]
impl INESHeader {
    #[getter]
    fn get_prg_size(&self) -> usize {
        self.prg_units as usize * PRG_UNIT_SIZE
    }

    #[getter]
    fn get_chr_size(&self) -> usize {
        self.chr_units as usize * CHR_UNIT_SIZE
    }
}

impl From<[Byte; ROM_HEADER_LENGTH]> for INESHeader {
    fn from(header: [Byte; ROM_HEADER_LENGTH]) -> Self {
        Self {
            magic_bytes: header[0..4].try_into().unwrap(),
            prg_units: header[4],
            chr_units: header[5],
            flags: header[6],
            unused_flags: header[7..11].try_into().unwrap(),
            unused_pad: header[11..].try_into().unwrap(),
        }
    }
}

#[pyclass]
pub struct Rom {
    data: Vec<Byte>,
    header: INESHeader,
    pub labels: _Labels,
}

#[pymethods]
impl Rom {
    #[new]
    pub fn new(data: Vec<u8>) -> Self {
        let header_data: [u8; ROM_HEADER_LENGTH] = data[0..ROM_HEADER_LENGTH].try_into().unwrap();

        let header = INESHeader::from(header_data);
        
        let labels = _Labels::from_default();

        Self { data, header, labels }
    }
    
    #[staticmethod]
    fn from_file(path: &str) -> Self {
        let data = std::fs::read(path).unwrap();
        Self::new(data)
    }
    
    fn save_to(&self, path: &str) {
        std::fs::write(path, &self.data).unwrap();
    }

    #[getter]
    fn get_prg_units(&self) -> usize {
        self.header.prg_units as usize
    }

    #[getter]
    fn get_prg_banks(&self) -> usize {
        self.get_prg_units() * PRG_BANKS_PER_UNIT
    }

    pub fn prg_normalize(&self, address: &RawAddress) -> NormalizedAddress {
        if (address) < &(RawAddress(30_usize * PRG_BANK_SIZE) + BASE_OFFSET) {
            return NormalizedAddress(address.0);
        }

        let additional_byte_count = self.header.get_prg_size() - VANILLA_PRG_SIZE;

        NormalizedAddress(address.0 + additional_byte_count)
    }

    fn tsa_data_for_object_set(&self, object_set_index: Index) -> Vec<Byte> {
        let tsa_index;
        if object_set_index == WORLD_MAP_OBJECT_SET_INDEX {
            tsa_index = WORLD_MAP_TSA_INDEX;
        } else {
            tsa_index = self.data[(TSA_OS_LIST + object_set_index).0];
        }

        let tsa_start = RawAddress(tsa_index as usize * PRG_BANK_SIZE) + BASE_OFFSET;

        self.read(&tsa_start, TSA_TABLE_SIZE as u32)
    }

    fn find_byte(
        &self,
        byte: Byte,
        start: Option<&NormalizedAddress>,
        end: Option<&NormalizedAddress>,
    ) -> Option<NormalizedAddress> {
        let start = match start {
            Some(start) => start.0,
            None => 0,
        };

        let end = match end {
            Some(end) => end.0,
            None => self.data.len(),
        };

        let found = self.data[start..end].iter().position(|&b| b == byte);

        match found {
            Some(found) => Some(NormalizedAddress(found)),
            None => None,
        }
    }

    pub fn read(&self, address: &RawAddress, count: u32) -> Vec<Byte> {
        let normalized_address = self.prg_normalize(address);

        let start = normalized_address.0;
        let end = start + count as usize;

        self.data[start..end].try_into().unwrap()
    }

    pub fn read_until_byte(&self, address: &RawAddress, byte: Byte) -> Option<Vec<Byte>> {
        let normalized_address = self.prg_normalize(address);

        let end = self.find_byte(byte, Some(&normalized_address), None);

        if end.is_none() {
            return None;
        }

        let start = normalized_address.0;
        let end = end.unwrap().0;

        Some(self.data[start..end].try_into().unwrap())
    }

    pub fn byte(&self, address: &RawAddress) -> Byte {
        self.read(address, 1)[0]
    }

    pub fn little_endian(&self, address: &RawAddress) -> u16 {
        u16::from_le_bytes(self.read(address, 2).try_into().unwrap())
    }
    
    pub fn offset(&self, address: &RawAddress) -> Offset {
        Offset(self.little_endian(address))
    }

    pub fn nibbles(&self, address: &RawAddress) -> (Byte, Byte) {
        let byte = self.byte(address);

        let high_nibble = byte >> 4;
        let low_nibble = byte & 0x0F;

        (high_nibble, low_nibble as Byte)
    }

    pub fn write(&mut self, address: &RawAddress, data: &[Byte]) {
        let normalized_address = self.prg_normalize(address);

        let range = normalized_address.0..normalized_address.0 + data.len();
        
        self.data[range].copy_from_slice(data);
    }

    pub fn write_byte(&mut self, address: &RawAddress, byte: Byte) {
        self.write(address, &[byte]);
    }

    pub fn write_offset(&mut self, address: &RawAddress, offset: Offset) {
        self.write_little_endian(address, offset.0);
    }
    
    pub fn write_little_endian(&mut self, address: &RawAddress, integer: u16) {
        self.write(address, &integer.to_le_bytes());
    }

    pub fn write_nibbles(&mut self, address: &RawAddress, high_nibble: Byte, low_nibble: Byte) {
        let byte = (high_nibble << 4) | low_nibble;

        self.write(address, &[byte]);
    }
}
