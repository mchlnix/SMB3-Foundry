use crate::constants::Constants;
use crate::data_points::datapoint::HasIndex;
use crate::types::RomAddress;

struct FortressFxData {
    index: u8,

    row_address: RomAddress,
    row: u8,

    column_and_screen_address: RomAddress,
    column: u8,
    screen: u8,

    tile_indexes_address: RomAddress,
    tile_indexes: [u8; 4],

    replacement_block_address: RomAddress,
    replacement_block_index: u8,

    map_completion_data_address: RomAddress,
    map_completion_bit_index: u8,

    v_addr_high_address: RomAddress,
    v_addr_high: u8,

    v_addr_low_address: RomAddress,
    v_addr_low: u8,
}

impl HasIndex for FortressFxData {
    fn index(&self) -> u8 {
        self.index
    }

    fn set_index(&mut self, index: u8) {
        self.index = index;
    }

    fn calculate_addresses(&mut self) {
        self.row_address = Constants().FortressFX_MapLocationRow + self.index;
        self.column_and_screen_address = Constants().
    }
}