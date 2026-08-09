use crate::mpu6502::{Byte, MemAddress};
use pyo3::{pyclass, pymethods};


#[derive(Debug)]
#[pyclass(from_py_object)]
pub struct ParsedLevelObject {
    object_set_number: u8,
    pub(crate) object_bytes: Vec<Byte>,

    pub(crate) pos_in_memory: MemAddress,

    pub tiles_in_level: Vec<(MemAddress, Byte)>,
}

pub trait CanBeJump {
    fn get_info(&self) -> (u8, u8, u8);
}

#[pymethods]
impl ParsedLevelObject {
    #[new]
    pub(crate) fn new(object_set_number: u8, object_bytes: Vec<Byte>, pos_in_memory: MemAddress) -> ParsedLevelObject {
        let new_object = ParsedLevelObject {
            object_set_number,
            object_bytes,
            pos_in_memory,
            tiles_in_level: vec![],
        };

        new_object
    }

    #[getter(object_set_number)]
    fn get_object_set_number(&self) -> u8 {
        self.object_set_number
    }

    #[getter]
    pub fn len(&self) -> u32 {
        self.object_bytes.len() as u32
    }

    #[getter]
    pub fn domain(&self) -> u8 {
        self.object_bytes[0] >> 5
    }

    #[getter]
    pub fn object_id(&self) -> u8 {
        self.object_bytes[2]
    }

    #[getter]
    fn is_fixed(&self) -> bool {
        self.object_id() < 0x10
    }

    #[getter]
    fn x(&self) -> u8 {
        self.object_bytes[1]
    }

    #[getter]
    fn y(&self) -> u8 {
        self.object_bytes[0] & 0b0001_1111
    }
}

impl CanBeJump for ParsedLevelObject {
    fn get_info(&self) -> (u8, u8, u8) {
        (self.object_set_number, self.domain(), self.object_id())
    }
}

impl Clone for ParsedLevelObject {
    fn clone(&self) -> Self {
        ParsedLevelObject {
            object_set_number: self.object_set_number,
            object_bytes: self.object_bytes.clone(),
            pos_in_memory: self.pos_in_memory,
            tiles_in_level: self.tiles_in_level.clone(),
        }
    }
}

#[pyclass(from_py_object)]
pub struct ParsedEnemy {
    object_set_number: u8,
    object_bytes: Vec<Byte>,

    pos_in_memory: u32,
}

#[pymethods]
impl ParsedEnemy {
    #[new]
    pub(crate) fn new(object_set_number: u8, object_bytes: Vec<Byte>, pos_in_memory: u32) -> ParsedEnemy {
        ParsedEnemy {
            object_set_number,
            object_bytes,
            pos_in_memory,
        }
    }

    fn get_object_set_number(&self) -> u8 {
        self.object_set_number
    }

    pub fn len(&self) -> u32 {
        3
    }

    fn domain(&self) -> u8 {
        0
    }

    fn object_id(&self) -> u8 {
        self.object_bytes[0]
    }

    fn is_fixed(&self) -> bool {
        true
    }

    fn x(&self) -> u8 {
        self.object_bytes[1]
    }

    fn y(&self) -> u8 {
        self.object_bytes[2]
    }
}

impl CanBeJump for ParsedEnemy {
    fn get_info(&self) -> (u8, u8, u8) {
        (self.object_set_number, self.domain(), self.object_id())
    }
}

impl Clone for ParsedEnemy {
    fn clone(&self) -> Self {
        ParsedEnemy {
            object_set_number: self.object_set_number,
            object_bytes: self.object_bytes.clone(),
            pos_in_memory: self.pos_in_memory,
        }
    }
}

