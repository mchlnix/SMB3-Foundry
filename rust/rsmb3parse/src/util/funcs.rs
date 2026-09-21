use pyo3::pyfunction;

#[pyfunction]
pub fn clamp(min: i32, value: i32, max: i32) -> i32 {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}

#[pyfunction]
pub fn hex_int(number: String) -> i64 {
    i64::from_str_radix(&number.trim_start_matches("0x"), 16).unwrap()
}
