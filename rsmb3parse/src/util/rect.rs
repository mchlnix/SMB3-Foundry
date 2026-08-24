use pyo3::{pyclass, pymethods, PyRef, PyRefMut, PyResult, Py};

#[pyclass(from_py_object)]
#[derive(Clone, PartialEq, Eq)]
pub struct Rect {
    #[pyo3(get, set)]
    pub x: i32,
    #[pyo3(get, set)]
    pub y: i32,
    #[pyo3(get, set)]
    pub width: i32,
    #[pyo3(get, set)]
    pub height: i32,
}

#[pymethods]
impl Rect {

    #[new]
    #[pyo3(signature=(x=0, y=0, width=0, height=0))]
    pub fn new(x: i32, y: i32, width: i32, height: i32) -> Self {
        let mut x = x;
        let mut y = y;
        let mut width = width;
        let mut height = height;

        if width < 0 {
            width = width * -1;
            x = x -width;
        }

        if height < 0 {
            height = height * -1;
            y = y -height;
        }

        Self { x, y, width, height }
    }

    pub fn size(&self) -> (i32, i32) {
        (self.width, self.height)
    }

    pub fn top(&self) -> i32 {
        self.y
    }

    pub fn bottom(&self) -> i32 {
        self.y + self.height
    }

    pub fn left(&self) -> i32 {
        self.x
    }

    pub fn right(&self) -> i32 {
        self.x + self.width
    }

    pub fn top_left(&self) -> Point {
        Point::new(self.left(), self.top())
    }

    pub fn top_right(&self) -> Point {
        Point::new(self.right(), self.top())
    }

    pub fn bottom_left(&self) -> Point {
        Point::new(self.left(), self.bottom())
    }

    pub fn bottom_right(&self) -> Point {
        Point::new(self.right(), self.bottom())
    }

    #[pyo3(signature=(x, y, include_borders=true))]
    pub fn point_in(&self, x: i32, y: i32, include_borders: bool) -> bool {
        if include_borders {
            self.x <= x && x <= self.right() && self.y <= y && y <= self.bottom()
        }
        else {
            self.x <= x && x < self.right() && self.y <= y && y < self.bottom()
        }
    }

    pub fn intersects(&self, other: &Rect) -> bool {
        if self.left() >= other.right() {
            return false;
        }

        if other.left() >= self.right() {
            return false;
        }

        if self.top() >= other.bottom() {
            return false;
        }

        if other.top() >= self.bottom() {
            return false;
        }

        true
    }

    pub fn contains(&self, other: &Rect) -> bool {
        self.point_in(other.left(), other.top(), true) && self.point_in(other.right(), other.bottom(), true)
    }

    pub fn __mul__(&self, other: i32) -> Rect {
        Rect::new(self.x * other, self.y * other, self.width * other, self.height * other)
    }

    pub fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<Iter>> {
        let iter = Iter {
            inner: vec![slf.left(), slf.top(), slf.width, slf.height].into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    pub fn __eq__(&self, other: &Self) -> bool {
        self == other
    }
}

#[pyclass(from_py_object)]
#[derive(Clone, PartialEq, Eq)]
pub struct Point {
    #[pyo3(get, set)]
    pub x: i32,
    #[pyo3(get, set)]
    pub y: i32,
}

#[pymethods]
impl Point {
    #[new]
    pub fn new(x: i32, y: i32) -> Self {
        Self { x, y }
    }

    pub fn copy(&self) -> Self {
        Self { x: self.x, y: self.y }
    }

    pub fn __add__(&self, other: &Point) -> Point {
        Point::new(self.x + other.x, self.y + other.y)
    }

    pub fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<Iter>> {
        let iter = Iter {
            inner: vec![slf.x, slf.y].into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    pub fn __eq__(&self, other: &Self) -> bool {
        self == other
    }
}

#[pyclass]
pub struct Iter {
    inner: std::vec::IntoIter<i32>,
}

#[pymethods]
impl Iter {
    pub fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    pub fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<i32> {
        slf.inner.next()
    }
}


