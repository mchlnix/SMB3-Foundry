mod data_points;
pub mod types;
mod position;
pub mod util;
pub mod constants;

use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
mod rsmb3parse {
    use pyo3::prelude::*;

    /// Formats the sum of two numbers as string.
    #[pyfunction]
    fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
        Ok((a + b).to_string())
    }
}
