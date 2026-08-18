use crate::data_points::util::{FIRST_VALID_ROW, WORLD_MAP_SCREEN_SIZE, WORLD_MAP_SCREEN_WIDTH};
use pyo3::{pyclass, pymethods};
use std::ops::{Add, Sub};

#[pyclass(from_py_object)]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Position {
    pub x: u8,
    pub y: u8,
    pub screen: u8,
}

#[pymethods]
impl Position {
    #[new]
    pub fn new(x: u8, y: u8, screen: u8) -> Self {
        Self { x, y, screen }
    }

    #[getter]
    pub fn get_row(&self) -> u8 {
        self.y
    }

    #[setter]
    pub fn set_row(&mut self, value: u8) {
        self.y = value;
    }

    #[getter]
    pub fn get_column(&self) -> u8 {
        self.x
    }

    #[setter]
    pub fn set_column(&mut self, value: u8) {
        self.x = value;
    }

    #[getter]
    pub fn tile_data_index(&self) -> u8 {
        self.screen * WORLD_MAP_SCREEN_SIZE
            + (self.get_row() - FIRST_VALID_ROW) * WORLD_MAP_SCREEN_WIDTH
            + self.get_column()
    }
}

impl Add for Position {
    type Output = Self;

    fn add(self, rhs: Self) -> Self::Output {
        let (x, y): (u8, u8) = self.into();
        let (o_x, o_y): (u8, u8) = rhs.into();

        Position::from((x + o_x, y + o_y))
    }
}

impl Sub for Position {
    type Output = Self;

    fn sub(self, rhs: Self) -> Self::Output {
        let (x, y): (u8, u8) = self.into();
        let (o_x, o_y): (u8, u8) = rhs.into();

        Position::from((x - o_x, y - o_y))
    }
}

impl From<Position> for (u8, u8) {
    fn from(position: Position) -> Self {
        (position.screen * WORLD_MAP_SCREEN_WIDTH + position.x, position.y)
    }
}

impl From<u8> for Position {
    fn from(index: u8) -> Self {
        let screen = index / WORLD_MAP_SCREEN_SIZE;
        let index = index % WORLD_MAP_SCREEN_SIZE;

        let row = index / WORLD_MAP_SCREEN_WIDTH;
        let index = index % WORLD_MAP_SCREEN_WIDTH;

        let column = index;

        Self { x: column, y: row + FIRST_VALID_ROW, screen }
    }
}

impl From<(u8, u8)> for Position {
    fn from((x, y): (u8, u8)) -> Self {
        let screen = x / WORLD_MAP_SCREEN_WIDTH;
        let x = x % WORLD_MAP_SCREEN_WIDTH;

        Self { x, y, screen }
    }
}

impl From<(u8, u8, u8)> for Position {
    fn from((x, y, screen): (u8, u8, u8)) -> Self {
        Self { x, y, screen }
    }
}