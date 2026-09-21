use pyo3::{pyclass, pymethods};

#[allow(dead_code)]
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct Class {
    #[pyo3(get)]
    pub a: i32,

    #[pyo3(get, set)]
    pub b: i32,
}

#[pymethods]
impl Class {
    #[new]
    fn new(a: i32, b: i32) -> Self {
        Self { a, b }
    }

    pub fn add(&mut self, a: i32) {
        self.a += a;
    }
}
