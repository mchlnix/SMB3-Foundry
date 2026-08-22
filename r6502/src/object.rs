use crate::mpu6502::{Byte, MemAddress};
use pyo3::{pyclass, pymethods};


#[pyclass(from_py_object)]
#[derive(Clone, Debug)]
pub struct ParsedLevelObject {
    pub object_set_number: u8,
    pub object_bytes: Vec<Byte>,

    pub pos_in_memory: MemAddress,

    pub tiles_in_level: Vec<(MemAddress, Byte)>,
}

pub trait CanBeJump {
    fn get_info(&self) -> (u8, u8, u8);
}

#[pymethods]
impl ParsedLevelObject {
    #[new]
    pub fn new(object_set_number: u8, object_bytes: Vec<Byte>, pos_in_memory: MemAddress) -> ParsedLevelObject {
        let new_object = ParsedLevelObject {
            object_set_number,
            object_bytes,
            pos_in_memory,
            tiles_in_level: vec![],
        };

        new_object
    }

    #[getter]
    pub fn get_object_set_num(&self) -> u8 {
        self.object_set_number
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
    pub fn is_fixed(&self) -> bool {
        self.object_id() < 0x10
    }

    #[getter]
    pub fn x(&self) -> u8 {
        self.object_bytes[1]
    }

    #[getter]
    pub fn y(&self) -> u8 {
        self.object_bytes[0] & 0b0001_1111
    }

    pub(crate) fn len(&self) -> u32 {
        self.object_bytes.len() as u32
    }
}

impl CanBeJump for ParsedLevelObject {
    fn get_info(&self) -> (u8, u8, u8) {
        (self.object_set_number, self.domain(), self.object_id())
    }
}

#[pyclass(from_py_object)]
#[derive(Clone, Debug)]
pub struct ParsedEnemy {
    pub object_set_number: u8,
    pub object_bytes: Vec<Byte>,

    pub pos_in_memory: u32,
}

#[pymethods]
impl ParsedEnemy {
    #[new]
    pub fn new(object_set_number: u8, object_bytes: Vec<Byte>, pos_in_memory: u32) -> ParsedEnemy {
        ParsedEnemy {
            object_set_number,
            object_bytes,
            pos_in_memory,
        }
    }

    #[getter]
    pub fn get_object_set_num(&self) -> u8 {
        self.object_set_number
    }

    #[getter]
    pub fn domain(&self) -> u8 {
        0
    }

    #[getter]
    pub fn object_id(&self) -> u8 {
        self.object_bytes[0]
    }

    #[getter]
    pub fn is_fixed(&self) -> bool {
        true
    }

    #[getter]
    pub fn x(&self) -> u8 {
        self.object_bytes[1]
    }

    #[getter]
    pub fn y(&self) -> u8 {
        self.object_bytes[2]
    }

    pub(crate) fn len(&self) -> u32 {
        3
    }
}

impl CanBeJump for ParsedEnemy {
    fn get_info(&self) -> (u8, u8, u8) {
        (self.object_set_number, self.domain(), self.object_id())
    }
}
