use pyo3::pyclass;

#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct RawAddress(pub usize);

#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct NormalizedAddress(pub usize);

impl From<RawAddress> for u16 {
    fn from(address: RawAddress) -> Self {
        address.0 as u16
    }
}

impl From<NormalizedAddress> for u16 {
    fn from(address: NormalizedAddress) -> Self {
        address.0 as u16
    }
}

pub type RomAddress = u32;


pub type Byte = u8;