use crate::level::ParsedLevel;
use crate::memory::Rom;
use mpu6502::MPU;
use pyo3::prelude::*;

mod object;
mod memory;
mod level;
mod constants;
mod mpu6502;

#[pyfunction]
fn load_from_address(_py: Python, rom_data: Vec<u8>, prg_bank_count: u8, object_set_number: u8, level_position: u32, enemy_position: u32, max_steps: u32) -> PyResult<ParsedLevel> {
    let rom: Rom = Rom {
        data: rom_data,
        prg_bank_count,
    };

    let mut cpu = MPU::new(rom);

    let level = cpu.load_from_address(object_set_number, level_position, enemy_position, max_steps);

    Ok(level)
}

#[pymodule]
mod r6502 {
    #[pymodule_export]
    use super::load_from_address;

    #[pymodule_export]
    use crate::level::ParsedLevel;
}

