use crate::constants::{LEVEL_HEADER_LENGTH, OBJECT_ID_RANGES};
use crate::devices::mpu6502::Byte;
use crate::object::{CanBeJump, ParsedEnemy, ParsedLevelObject};
use pyo3::{pyclass, pymethods};
use std::ops::RangeInclusive;

#[pyclass]
pub struct ParsedLevel {
    #[pyo3(get)]
    pub object_set_num: u8,
    #[pyo3(get)]
    pub graphics_set_num: u8,
    #[pyo3(get)]
    pub object_palette_num: u8,
    #[pyo3(get)]
    pub enemy_palette_num: u8,
    #[pyo3(get)]
    pub screen_memory: Vec<Byte>,
    #[pyo3(get)]
    pub parsed_objects: Vec<ParsedLevelObject>,
    #[pyo3(get)]
    pub parsed_enemies: Vec<ParsedEnemy>,
}

fn obj_range(object_set_number: u8, start_value: u8) -> RangeInclusive<u8> {
    if start_value < 0x10 || [0x0, 0x10].contains(&object_set_number) {
        return start_value..=start_value;
    }

    start_value..=(start_value.saturating_add(0x10))
}

fn goes_to_next_level(object: Box<&dyn CanBeJump>) -> bool {
    let (object_set_number, domain, object_id) = object.get_info();

    let object_id_ranges: &[(u8, &[u8])] = OBJECT_ID_RANGES[object_set_number as usize];

    let object_ids: Option<&(u8, &[u8])> = object_id_ranges
        .iter()
        .find(|(_domain, _)| *_domain == domain);

    // current object is not in a domain, where jump objects reside
    if object_ids.is_none() {
        return false;
    }

    let object_ids = object_ids.unwrap().1;

    object_ids
        .iter()
        .any(|jump_id| obj_range(object_set_number, *jump_id).contains(&object_id))
}

#[pymethods]
impl ParsedLevel {
    #[getter(object_data_length)]
    fn get_object_data_length(&self) -> u32 {
        LEVEL_HEADER_LENGTH + self.parsed_objects.iter().map(|obj| obj.len()).sum::<u32>()
    }

    #[getter(enemy_data_length)]
    fn get_enemy_data_length(&self) -> u32 {
        self.parsed_enemies.iter().map(|en| en.len()).sum::<u32>()
    }

    fn has_jump(&self) -> bool {
        let object_iter = self.parsed_objects.iter().map(|obj| obj as &dyn CanBeJump);
        let enemy_iter = self.parsed_enemies.iter().map(|obj| obj as &dyn CanBeJump);

        object_iter
            .chain(enemy_iter)
            .any(|obj| goes_to_next_level(Box::new(obj)))
    }

    fn has_generic_exit(&self) -> bool {
        let domain: u8;
        let id_range: RangeInclusive<u8>;

        if [0x03, 0x0E].contains(&self.object_set_num) {
            domain = 4;
            id_range = 0xE0..=0xEF;
        } else if self.object_set_num == 0x0D {
            domain = 3;
            id_range = 0x60..=0x6F;
        } else if [0x05, 0x0B].contains(&self.object_set_num) {
            domain = 3;
            id_range = 0x50..=0x6F;
        } else {
            return false;
        }

        self.parsed_objects
            .iter()
            .any(|obj| obj.domain() == domain && id_range.contains(&obj.object_id()))
    }

    fn has_big_q_level(&self) -> bool {
        let domain;
        let id_range;

        if (0x01..0x10).contains(&self.object_set_num) {
            domain = 1;
            id_range = 0xB0..=0xBF;
        } else {
            return false;
        }

        self.parsed_objects
            .iter()
            .any(|obj| obj.domain() == domain && id_range.contains(&obj.object_id()))
    }
}
