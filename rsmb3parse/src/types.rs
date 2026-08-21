use pyo3::pyclass;
use std::ops::{Add, Mul, Sub};

pub type Byte = u8;

// Offset //

#[pyclass(from_py_object)]
#[derive(Clone, Copy, Default, Hash, PartialEq, Eq, PartialOrd, Ord)]
pub struct Offset(pub u16);

impl Add<Offset> for Offset {
    type Output = Offset;
    fn add(self, rhs: Offset) -> Self::Output {
        Offset(self.0 + rhs.0)
    }
}

impl Add<Index> for Offset {
    type Output = Offset;
    fn add(self, rhs: Index) -> Self::Output {
        Offset(self.0 + rhs.0 as u16)
    }
}

impl Mul<usize> for Offset {
    type Output = Offset;
    fn mul(self, rhs: usize) -> Self::Output {
        Offset(self.0 * rhs as u16)
    }
}

impl From<RawAddress> for Offset {
    fn from(raw_address: RawAddress) -> Self {
        Offset(raw_address.0 as u16)
    }
}

impl From<u8> for Offset {
    fn from(byte: u8) -> Self {
        Offset(byte as u16)
    }
}

impl From<usize> for Offset {
    fn from(byte: usize) -> Self {
        Offset(byte as u16)
    }
}

// RawAddress //

#[pyclass(from_py_object)]
#[derive(Clone, Copy, Default, Hash, PartialEq, Eq, PartialOrd, Ord)]
pub struct RawAddress(pub usize);

impl Add<Index> for RawAddress {
    type Output = RawAddress;
    fn add(self, rhs: Index) -> Self::Output {
        RawAddress(self.0 + rhs.0 as usize)
    }
}

impl Add<usize> for RawAddress {
    type Output = RawAddress;
    fn add(self, rhs: usize) -> Self::Output {
        RawAddress(self.0 + rhs)
    }
}

impl Add<Offset> for RawAddress {
    type Output = RawAddress;
    fn add(self, rhs: Offset) -> Self::Output {
        RawAddress(self.0 + rhs.0 as usize)
    }
}

impl Sub<Offset> for RawAddress {
    type Output = Offset;
    fn sub(self, rhs: Offset) -> Self::Output {
        Offset(self.0 as u16 - rhs.0)
    }
}

impl From<u32> for RawAddress {
    fn from(address: u32) -> Self {
        RawAddress(address as usize)
    }
}

impl From<i32> for RawAddress {
    fn from(address: i32) -> Self {
        RawAddress(address as usize)
    }
}

impl From<Offset> for RawAddress {
    fn from(offset: Offset) -> Self {
        RawAddress(offset.0 as usize)
    }
}

// NormalizedAddress //

#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct NormalizedAddress(pub usize);

// Index //

#[pyclass(from_py_object)]
#[derive(Clone, Copy, PartialEq, Eq, Default, Hash, PartialOrd, Ord)]
pub struct Index(pub u8);

impl From<Index> for u8 {
    fn from(index: Index) -> Self {
        index.0
    }
}

impl Mul<usize> for Index {
    type Output = Index;
    fn mul(self, rhs: usize) -> Self::Output {
        Index(self.0 * rhs as u8)
    }
}