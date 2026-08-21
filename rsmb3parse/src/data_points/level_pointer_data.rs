use pyo3::{pyclass, pymethods};
use crate::data_points::world_map_data::WorldMapData;
use crate::position::Position;
use crate::types::{Index, Offset, RawAddress};
use crate::util::rom::Rom;

#[pyclass(from_py_object)]
#[derive(Clone, Default, PartialEq, Eq, PartialOrd, Ord)]
pub struct LevelPointerData {
    index: Index,

    pos: Position,

    object_set_number_address: RawAddress,
    object_set_number: u8,

    level_offset_address: RawAddress,
    level_offset: Offset,

    enemy_offset_address: RawAddress,
    enemy_offset: Offset,
}

#[pymethods]
impl LevelPointerData {
    #[new]
    pub fn new(world: &WorldMapData, index: Index) -> Self {
        let mut level_pointer_data = Self {
            index,
            ..Default::default()
        };

        level_pointer_data.calculate_addresses(world);

        level_pointer_data
    }

    pub fn calculate_addresses(&mut self, world_map_data: &WorldMapData) {

    }
    
    pub fn change_index(&mut self, world_map_data: &mut WorldMapData, index: Index) {
        self.index = index;
        
        self.calculate_addresses(world_map_data);
    }
    
    pub fn read_values(&mut self, rom : &Rom) {
        
    }
    
    pub fn write_to_rom(&mut self, world_map_data: &WorldMapData, rom: &mut Rom) {
        
    }
    
    #[getter]
    pub fn get_screen(&self) -> u8 {
        self.pos.screen
    }
    
    
}