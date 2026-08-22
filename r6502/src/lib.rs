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

/// A Python module implemented in Rust.
#[pymodule]
fn r6502(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(load_from_address, m)?)?;
    m.add_class::<ParsedLevel>()?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_load_from_address() {
        let rom_data = fs::read("/home/michael/Gits/SMB3Foundry/roms/smb3.nes");

        let rom: Rom = Rom {
            data: rom_data.unwrap(),
            prg_bank_count: 32,
        };

        let mut cpu = MPU::new(rom);

        cpu.load_from_address(1, 0x1FB92, 0xC537, 60000);
    }
}


