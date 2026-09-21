use std::cmp::min;
use pyo3::{pyclass, pymethods};
use crate::data_points::util::FIRST_VALID_ROW;
use crate::position::Position;
use crate::types::{Byte, Index, RawAddress};
use crate::util::rom::Rom;

#[pyclass(from_py_object)]
#[derive(Default, Clone, Hash, PartialOrd, Ord)]
pub struct FortressFxData {
    pub index: Index,

    row_address: RawAddress,
    column_and_screen_address: RawAddress,

    pub pos: Position,

    tile_indexes_address: RawAddress,
    tile_indexes: Vec<Byte>,

    replacement_block_address: RawAddress,
    replacement_block_index: u8,

    map_completion_data_address: RawAddress,
    map_completion_bit_index: u8,

    v_addr_high_address: RawAddress,
    v_addr_high: u8,

    v_addr_low_address: RawAddress,
    v_addr_low: u8,
}

impl FortressFxData {
    pub fn new(rom: &Rom, index: Index) -> FortressFxData {
        let mut data = FortressFxData {
            index,
            ..Default::default()
        };

        data.calculate_addresses(rom);
        data.read_values(rom);

        data
    }
}

#[pymethods]
impl FortressFxData {
    fn calculate_addresses(&mut self, rom: &Rom) {
        self.row_address = rom.labels.FortressFx_MapLocationRow + self.index;
        self.column_and_screen_address = rom.labels.FortressFX_MapLocation + self.index;

        self.tile_indexes_address = rom.labels.FortressFX_Patterns + self.index * 4;  // tiles per block
        self.replacement_block_address = rom.labels.FortressFX_MapTileReplace + self.index;

        // ignore the column value of the map completion data, because it is the same as the screen and column position
        self.map_completion_data_address = rom.labels.FortressFX_MapCompIdx + self.index * 2;

        self.v_addr_high_address = rom.labels.FortressFX_VAddrH + self.index;
        self.v_addr_low_address = rom.labels.FortressFX_VAddrL + self.index;
    }

    fn read_values(&mut self, rom: &Rom) {
        let (row, _) = rom.nibbles(&RawAddress::from(self.row_address));
        let (column, screen) = rom.nibbles(&self.column_and_screen_address);

        self.pos = Position::new(row, column, screen);

        self.tile_indexes = rom.read(&self.tile_indexes_address, 4);
        self.replacement_block_index = rom.byte(&self.replacement_block_address);

        // ignore the column value of the map completion data, because it is the same as the screen and column position
        self.map_completion_bit_index = rom.byte(&(self.map_completion_data_address + 1));

        self.v_addr_high = rom.byte(&self.v_addr_high_address);
        self.v_addr_low = rom.byte(&self.v_addr_low_address);
    }

    pub fn write_to_rom(&self, rom: &mut Rom) {
        rom.write_nibbles(&self.row_address, self.pos.get_row(), 0);
        rom.write_nibbles(&self.column_and_screen_address, self.pos.get_column(), self.pos.screen);

        rom.write(&self.tile_indexes_address, self.tile_indexes.as_slice());
        rom.write_byte(&self.replacement_block_address, self.replacement_block_index);

        rom.write_nibbles(&self.map_completion_data_address, self.pos.screen, self.pos.get_column());

        // 8 is not a valid row for any level pointer, row 9 has its value
        let adjusted_row = self.pos.get_row() - FIRST_VALID_ROW;
        let minimum_shift = min(adjusted_row, 0x08);

        // last minute sanitization
        let map_completion_bit_index = 0x80 >> minimum_shift;

        rom.write_byte(&(self.map_completion_data_address + 1), map_completion_bit_index);

        // TODO find reasons for numbers; 32 * 4 screens * 8?
        let v_addr_offset: u16 = 0x2800 + ((self.pos.get_row() * 32 + self.pos.get_column()) * 2) as u16;

        rom.write_byte(&self.v_addr_high_address, (v_addr_offset >> 8) as Byte);
        rom.write_byte(&self.v_addr_low_address, (v_addr_offset & 0x00FF) as Byte);
    }

    #[getter]
    pub fn get_pos(&self) -> Position {
        self.pos.clone()
    }
}

impl PartialEq for FortressFxData {
    fn eq(&self, other: &Self) -> bool {
        if self.index != other.index {
            return false;
        }
        if self.get_pos() != other.get_pos() {
            return false;
        }

        if self.replacement_block_index != other.replacement_block_index {
            return false;
        }

        true
    }
}

impl Eq for FortressFxData {}