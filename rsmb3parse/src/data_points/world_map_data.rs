use crate::data_points::datapoint::Datapoint;
use crate::data_points::fortress_fx_data::FortressFxData;
use crate::data_points::level_pointer_data::LevelPointerData;
use crate::position::Position;
use crate::types::{Byte, Index, Offset, RawAddress};
use crate::util::rom::{
    AIRSHIP_TRAVEL_SET_COUNT, AIRSHIP_TRAVEL_SET_SIZE, BASE_OFFSET, OFFSET_SIZE, Rom,
};
use pyo3::{pyclass, pymethods};
use std::collections::HashMap;

const WORLD_MAP_LAYOUT_DELIMITER: Byte = 0xff;
const MAX_SCREEN_COUNT: u8 = 4;
const WORLD_MAP_BASE_OFFSET: Offset = Offset(0xE000);

#[pyclass(from_py_object)]
#[derive(Clone, Default, PartialEq, Eq, PartialOrd, Ord)]
pub struct WorldMapData {
    index: Index,

    tile_data_offset_address: RawAddress,
    tile_data_offset: Offset,

    tile_data: Vec<Byte>,

    bottom_border_tile_address: RawAddress,
    bottom_border_tile: Byte,

    palette_index_address: RawAddress,
    palette_index: Byte,

    object_color_palette_index_address: RawAddress,
    object_color_palette_index: Byte,

    frame_tick_count_address: RawAddress,
    frame_tick_count: Byte,

    structure_data_offset_address: RawAddress,
    structure_data_offset: Offset,

    map_start_y_address: RawAddress,
    map_start_y: Byte,

    map_scroll_address: RawAddress,
    map_scroll: Byte,

    airship_travel_base_index_address: RawAddress,
    airship_travel_base_index: Byte,

    airship_travel_x_set_address: RawAddress,
    airship_travel_y_set_address: RawAddress,

    airship_travel_sets: [Vec<Position>; 3],

    fortress_fx_base_index_address: RawAddress,
    fortress_fx_base_index: Byte,

    fortress_fx_indexes: Vec<Byte>,
    fortress_fx_count: Byte,
    fortress_fx_data_objects: Vec<FortressFxData>,

    pos_offsets_for_screen: Vec<Byte>,

    y_pos_list_start_address: RawAddress,
    y_pos_list_start: RawAddress,

    x_pos_list_start_address: RawAddress,
    x_pos_list_start: RawAddress,

    enemy_offset_list_offset_address: RawAddress,
    enemy_offset_list_offset: Offset,

    level_offset_list_offset_address: RawAddress,
    level_offset_list_offset: Offset,

    level_pointers: Vec<LevelPointerData>,

    airship_enemy_offset_address: RawAddress,
    airship_enemy_offset: Offset,
    airship_level_offset_address: RawAddress,
    airship_level_offset: Offset,

    coin_ship_enemy_offset_address: RawAddress,
    coin_ship_enemy_offset: Offset,
    coin_ship_level_offset_address: RawAddress,
    coin_ship_level_offset: Offset,

    generic_exit_object_set_address: RawAddress,
    generic_exit_object_set: Byte,
    generic_exit_enemy_offset_address: RawAddress,
    generic_exit_enemy_offset: Offset,
    generic_exit_level_offset_address: RawAddress,
    generic_exit_level_offset: Offset,

    big_q_block_object_set_address: RawAddress,
    big_q_block_object_set: Byte,
    big_q_block_enemy_offset_address: RawAddress,
    big_q_block_enemy_offset: Offset,
    big_q_block_level_offset_address: RawAddress,
    big_q_block_level_offset: Offset,

    toad_warp_level_offset_address: RawAddress,
    toad_warp_level_offset: Offset,

    toad_warp_item_address: RawAddress,
    toad_warp_item: u16,

    music_index_address: RawAddress,
    music_index: Byte,

    music_arrival_index_address: RawAddress,
    music_arrival_index: Byte,
}

#[pymethods]
impl WorldMapData {
    #[getter]
    fn get_layout_address(&self) -> RawAddress {
        RawAddress::from(WORLD_MAP_BASE_OFFSET + self.tile_data_offset)
    }

    #[setter]
    fn set_layout_address(&mut self, address: RawAddress) {
        self.tile_data_offset = Offset::from(address - WORLD_MAP_BASE_OFFSET)
    }

    #[getter]
    fn get_structure_block_address(&self) -> RawAddress {
        RawAddress::from(WORLD_MAP_BASE_OFFSET + self.structure_data_offset)
    }

    #[setter]
    fn set_structure_block_address(&mut self, address: RawAddress) {
        self.structure_data_offset = Offset::from(address - WORLD_MAP_BASE_OFFSET);

        let level_count = self.get_level_count();

        self.y_pos_list_start = self.get_structure_block_address() + Offset::from(MAX_SCREEN_COUNT);
        self.x_pos_list_start = self.y_pos_list_start + Offset::from(level_count);

        self.enemy_offset_list_offset =
            self.x_pos_list_start - WORLD_MAP_BASE_OFFSET + Offset::from(self.get_level_count());
        self.level_offset_list_offset =
            self.enemy_offset_list_offset + Offset::from(self.get_level_count()) * OFFSET_SIZE;
    }

    #[getter]
    fn get_fortress_fx_indexes_start_address(&self) -> RawAddress {
        RawAddress::from(
            WORLD_MAP_BASE_OFFSET + Offset::from(self.fortress_fx_indexes.len() * OFFSET_SIZE),
        )
    }

    #[getter]
    fn get_level_count(&self) -> u8 {
        (self.x_pos_list_start.0 - self.y_pos_list_start.0) as u8
    }

    #[getter]
    fn get_level_count_screen_1(&self) -> u8 {
        self.pos_offsets_for_screen[1] - self.pos_offsets_for_screen[0]
    }

    #[setter]
    fn set_level_count_screen_1(&mut self, value: u8) {
        let diff = value - self.get_level_count_screen_1();

        self._update_level_counts(1, diff)
    }

    #[getter]
    fn get_level_count_screen_2(&self) -> u8 {
        self.pos_offsets_for_screen[1] - self.pos_offsets_for_screen[0]
    }

    #[setter]
    fn set_level_count_screen_2(&mut self, value: u8) {
        let diff = value - self.get_level_count_screen_1();

        self._update_level_counts(1, diff)
    }

    #[getter]
    fn get_level_count_screen_3(&self) -> u8 {
        self.pos_offsets_for_screen[1] - self.pos_offsets_for_screen[0]
    }

    #[setter]
    fn set_level_count_screen_3(&mut self, value: u8) {
        let diff = value - self.get_level_count_screen_1();

        self._update_level_counts(1, diff)
    }

    #[getter]
    fn get_level_count_screen_4(&self) -> u8 {
        self.pos_offsets_for_screen[1] - self.pos_offsets_for_screen[0]
    }

    #[setter]
    fn set_level_count_screen_4(&mut self, value: u8) {
        let diff = value - self.get_level_count_screen_1();

        self._update_level_counts(1, diff)
    }

    fn _update_level_counts(&mut self, screen_number: u8, diff: u8) {
        for i in 0..MAX_SCREEN_COUNT {
            if i >= screen_number {
                self.pos_offsets_for_screen[i as usize] += diff;
            }
        }

        self.x_pos_list_start = self.x_pos_list_start + Offset(diff as u16);

        self.set_structure_block_address(self.get_structure_block_address());
    }


    fn calculate_addresses(&mut self, rom: &Rom) {
        self.tile_data_offset_address = rom.labels.Map_Tile_Layouts + self.index * OFFSET_SIZE;

        self.palette_index_address = rom.labels.Map_Tile_ColorSets + self.index;
        self.object_color_palette_index_address = rom.labels.Map_Object_ColorSets + self.index;

        self.bottom_border_tile_address = rom.labels.Map_Bottom_Tiles + self.index;
        // TODO you can define a separate tick count for each anim frame, not used in game though
        self.frame_tick_count_address = rom.labels.Map_AnimSpeeds + self.index * 4; // 4 animation frames

        self.structure_data_offset_address =
            rom.labels.Map_ByXHi_InitIndex + self.index * OFFSET_SIZE;

        self.y_pos_list_start_address = rom.labels.Map_ByRowType + self.index * OFFSET_SIZE;
        self.x_pos_list_start_address = rom.labels.Map_ByScrCol + self.index * OFFSET_SIZE;

        self.enemy_offset_list_offset_address = rom.labels.Map_ObjSets + self.index * OFFSET_SIZE;
        self.level_offset_list_offset_address =
            rom.labels.Map_LevelLayouts + self.index * OFFSET_SIZE;

        self.map_start_y_address = rom.labels.Map_Y_Starts + self.index;
        self.map_scroll_address = rom.labels.World_Map_Max_PanR + self.index;

        // unused, because the value is always 0x03 * world_index
        self.airship_travel_base_index_address = rom.labels.Map_Airship_Travel_BaseIdx + self.index;

        self.airship_travel_x_set_address =
            rom.labels.Map_Airship_Dest_XSets + self.index * AIRSHIP_TRAVEL_SET_COUNT * OFFSET_SIZE;
        self.airship_travel_y_set_address =
            rom.labels.Map_Airship_Dest_YSets + self.index * AIRSHIP_TRAVEL_SET_COUNT * OFFSET_SIZE;

        self.fortress_fx_base_index_address = rom.labels.FortressFXBase_ByWorld + self.index;

        self.airship_level_offset_address = rom.labels.Airship_Layouts + self.index * OFFSET_SIZE;
        self.airship_enemy_offset_address = rom.labels.Airship_Objects + self.index * OFFSET_SIZE;

        self.coin_ship_level_offset_address =
            rom.labels.CoinShip_Layouts + self.index * OFFSET_SIZE;
        self.coin_ship_enemy_offset_address =
            rom.labels.CoinShip_Objects + self.index * OFFSET_SIZE;

        self.generic_exit_level_offset_address =
            rom.labels.LevelJctGE_Layout + self.index * OFFSET_SIZE;
        self.generic_exit_enemy_offset_address =
            rom.labels.LevelJctGE_Objects + self.index * OFFSET_SIZE;
        self.generic_exit_object_set_address = rom.labels.LevelJctGE_Tileset + self.index;

        self.big_q_block_level_offset_address =
            rom.labels.LevelJctBQ_Layout + self.index * OFFSET_SIZE;
        self.big_q_block_enemy_offset_address =
            rom.labels.LevelJctBQ_Objects + self.index * OFFSET_SIZE;
        self.big_q_block_object_set_address = rom.labels.LevelJctBQ_Tileset + self.index;

        self.toad_warp_level_offset_address =
            rom.labels.ToadShop_Layouts + self.index * OFFSET_SIZE;
        self.toad_warp_item_address = rom.labels.ToadShop_Objects + self.index * OFFSET_SIZE;

        self.music_index_address = rom.labels.World_BGM + self.index;
        self.music_arrival_index_address = rom.labels.World_BGM_Arrival + self.index;
    }

    fn read_values(&mut self, rom: &Rom) {
        self.tile_data_offset = rom.offset(&self.tile_data_offset_address);
        self.tile_data = rom
            .read_until_byte(&self.get_layout_address(), WORLD_MAP_LAYOUT_DELIMITER)
            .unwrap();

        self.palette_index = rom.byte(&self.palette_index_address);
        self.object_color_palette_index = rom.byte(&self.object_color_palette_index_address);

        self.bottom_border_tile = rom.byte(&self.bottom_border_tile_address);
        self.frame_tick_count = rom.byte(&self.frame_tick_count_address);

        self.structure_data_offset = rom.offset(&self.structure_data_offset_address);

        self.pos_offsets_for_screen =
            rom.read(&self.get_structure_block_address(), MAX_SCREEN_COUNT as u32);

        self.y_pos_list_start =
            RawAddress::from(WORLD_MAP_BASE_OFFSET) + rom.offset(&self.y_pos_list_start_address);
        self.x_pos_list_start =
            RawAddress::from(WORLD_MAP_BASE_OFFSET) + rom.offset(&self.x_pos_list_start_address);

        self.level_pointers = (0..self.get_level_count())
            .map(|index| LevelPointerData::new(self, Index(index)))
            .collect();

        self.enemy_offset_list_offset = rom.offset(&self.enemy_offset_list_offset_address);
        self.level_offset_list_offset = rom.offset(&self.level_offset_list_offset_address);

        self.map_start_y = rom.byte(&self.map_start_y_address);
        self.map_scroll = rom.byte(&self.map_scroll_address);

        self.airship_travel_base_index = rom.byte(&self.airship_travel_base_index_address);

        for set_number in 0..AIRSHIP_TRAVEL_SET_COUNT {
            self.airship_travel_sets[set_number].clear();

            let offset_x = rom.offset(
                &(self.airship_travel_x_set_address + Index(set_number as u8) * OFFSET_SIZE),
            );
            let offset_y = rom.offset(
                &(self.airship_travel_y_set_address + Index(set_number as u8) * OFFSET_SIZE),
            );

            for index in 0..AIRSHIP_TRAVEL_SET_SIZE {
                let (x, screen) =
                    rom.nibbles(&(RawAddress::from(BASE_OFFSET) + 0xC000 + offset_x + index));
                let (y, _) =
                    rom.nibbles(&(RawAddress::from(BASE_OFFSET) + 0xC000 + offset_y + index));

                self.airship_travel_sets[set_number].push(Position::new(x, y, screen));
            }
        }
        self.fortress_fx_base_index = rom.byte(&self.fortress_fx_base_index_address);
        self.fortress_fx_count = rom.byte(&(self.fortress_fx_base_index_address + Offset(1)))
            - self.fortress_fx_base_index;

        self.fortress_fx_data_objects.clear();
        self.fortress_fx_indexes.clear();

        for offset in (0..self.fortress_fx_count).map(|index| Offset(index as u16)) {
            let index = rom.byte(&(self.get_fortress_fx_indexes_start_address() + offset));

            self.fortress_fx_data_objects
                .push(FortressFxData::new(rom, Index(index)));
            self.fortress_fx_indexes.push(index);
        }

        self.airship_level_offset = rom.offset(&self.airship_level_offset_address);
        self.airship_enemy_offset = rom.offset(&self.airship_enemy_offset_address);

        self.coin_ship_level_offset = rom.offset(&self.coin_ship_level_offset_address);
        self.coin_ship_enemy_offset = rom.offset(&self.coin_ship_enemy_offset_address);

        self.generic_exit_level_offset = rom.offset(&self.generic_exit_level_offset_address);
        self.generic_exit_enemy_offset = rom.offset(&self.generic_exit_enemy_offset_address);
        self.generic_exit_object_set = rom.byte(&self.generic_exit_object_set_address);

        self.big_q_block_level_offset = rom.offset(&self.big_q_block_level_offset_address);
        self.big_q_block_enemy_offset = rom.offset(&self.big_q_block_enemy_offset_address);
        self.big_q_block_object_set = rom.byte(&self.big_q_block_object_set_address);

        self.toad_warp_level_offset = rom.offset(&self.toad_warp_level_offset_address);
        self.toad_warp_item = rom.little_endian(&self.toad_warp_item_address);

        self.music_index = rom.byte(&self.music_index_address);
        self.music_arrival_index = rom.byte(&self.music_arrival_index_address);
    }

    fn write_to_rom(&mut self, rom: &mut Rom) {
        // tile_data_offset
        rom.write_offset(&self.tile_data_offset_address, self.tile_data_offset);
        // tile_data
        let mut world_tile_data = self.tile_data.clone();
        world_tile_data.push(WORLD_MAP_LAYOUT_DELIMITER);

        rom.write(&self.get_layout_address(), world_tile_data.as_slice());
        rom.write_byte(&self.palette_index_address, self.palette_index);
        rom.write_byte(
            &self.object_color_palette_index_address,
            self.object_color_palette_index,
        );
        rom.write_byte(&self.bottom_border_tile_address, self.bottom_border_tile);
        rom.write(&self.frame_tick_count_address, &[self.frame_tick_count; 4]);
        // structure_data_offset
        rom.write_offset(
            &self.structure_data_offset_address,
            self.structure_data_offset,
        );

        // values depending on amount of level pointers per screen
        self.level_pointers.sort();

        let mut level_pointer_per_screen: HashMap<u8, u8> = HashMap::new();

        for level_pointer in self.level_pointers.iter() {
            *level_pointer_per_screen.entry(level_pointer.get_screen()).or_insert(0) += 1;
        }

        self.set_level_count_screen_1(level_pointer_per_screen[&0]);
        self.set_level_count_screen_2(level_pointer_per_screen[&1]);
        self.set_level_count_screen_3(level_pointer_per_screen[&2]);
        self.set_level_count_screen_4(level_pointer_per_screen[&3]);

        // pos_offsets_for_screen
        rom.write(&self.get_structure_block_address(), self.pos_offsets_for_screen.as_slice());

        // y_pos_list_start
        rom.write_offset(
            &(rom.labels.Map_ByRowType + self.index * OFFSET_SIZE),
            self.y_pos_list_start - WORLD_MAP_BASE_OFFSET,
        );

        // x_pos_list_start
        rom.write_offset(
            &(rom.labels.Map_ByScrCol + self.index * OFFSET_SIZE),
            self.x_pos_list_start - WORLD_MAP_BASE_OFFSET,
        );

        rom.write_offset(
            &self.enemy_offset_list_offset_address,
            self.enemy_offset_list_offset,
        );
        rom.write_offset(
            &self.level_offset_list_offset_address,
            self.enemy_offset_list_offset + (Index(self.get_level_count()) * OFFSET_SIZE),
        );

        let mut mutable_clone = self.clone();

        for (index, level_pointer) in self.level_pointers.iter_mut().enumerate() {
            level_pointer.change_index(& mut mutable_clone, Index(index as u8));
            level_pointer.write_to_rom(& mut mutable_clone, rom);
        }

        rom.write_byte(&self.map_start_y_address, self.map_start_y);
        rom.write_byte(&self.map_scroll_address, self.map_scroll);

        rom.write_byte(
            &self.airship_travel_base_index_address,
            self.airship_travel_base_index,
        );

        for set_number in (0..AIRSHIP_TRAVEL_SET_COUNT).map(|index| Index(index as u8)) {
            let offset_x =
                rom.offset(&(self.airship_travel_x_set_address + set_number * OFFSET_SIZE));
            let offset_y =
                rom.offset(&(self.airship_travel_y_set_address + set_number * OFFSET_SIZE));

            for index in 0..AIRSHIP_TRAVEL_SET_SIZE {
                let pos: Position = self.airship_travel_sets[set_number.0 as usize][index];

                rom.write_nibbles(
                    &(RawAddress::from(BASE_OFFSET) + 0xC000 + offset_x + index),
                    pos.x,
                    pos.screen,
                );
                rom.write_nibbles(
                    &(RawAddress::from(BASE_OFFSET) + 0xC000 + offset_y + index),
                    pos.y,
                    0,
                );
            }
        }
        rom.write_byte(
            &self.fortress_fx_base_index_address,
            self.fortress_fx_base_index,
        );

        for (offset, fortress_fx_data) in self.fortress_fx_data_objects.iter().enumerate() {
            rom.write_byte(
                &(self.get_fortress_fx_indexes_start_address() + offset),
                fortress_fx_data.index.into(),
            );

            fortress_fx_data.write_to_rom(rom)
        }

        rom.write_offset(
            &self.airship_level_offset_address,
            self.airship_level_offset,
        );
        rom.write_offset(
            &self.airship_enemy_offset_address,
            self.airship_enemy_offset,
        );

        rom.write_offset(
            &self.coin_ship_level_offset_address,
            self.coin_ship_level_offset,
        );
        rom.write_offset(
            &self.coin_ship_enemy_offset_address,
            self.coin_ship_enemy_offset,
        );

        rom.write_offset(
            &self.generic_exit_level_offset_address,
            self.generic_exit_level_offset,
        );
        rom.write_offset(
            &self.generic_exit_enemy_offset_address,
            self.generic_exit_enemy_offset,
        );
        rom.write_byte(
            &self.generic_exit_object_set_address,
            self.generic_exit_object_set,
        );

        rom.write_offset(
            &self.big_q_block_level_offset_address,
            self.big_q_block_level_offset,
        );
        rom.write_offset(
            &self.big_q_block_enemy_offset_address,
            self.big_q_block_enemy_offset,
        );
        rom.write_byte(
            &self.big_q_block_object_set_address,
            self.big_q_block_object_set,
        );

        rom.write_offset(
            &self.toad_warp_level_offset_address,
            self.toad_warp_level_offset,
        );
        rom.write_little_endian(&self.toad_warp_item_address, self.toad_warp_item);

        rom.write_byte(&self.music_index_address, self.music_index);
        rom.write_byte(&self.music_arrival_index_address, self.music_arrival_index);
    }
}