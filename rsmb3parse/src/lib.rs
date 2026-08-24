mod data_points;
mod labels;
mod position;
mod types;
mod util;

use pyo3::prelude::*;

#[pymodule]
mod rsmb3parse {
    use pyo3::prelude::*;

    #[pymodule]
    mod util {
        #[pymodule_export]
        use crate::util::rom::Rom;

        #[pymodule_export]
        use crate::util::rom::INESHeader;

        #[pymodule_export]
        use crate::util::funcs::clamp;

        #[pymodule_export]
        use crate::util::funcs::hex_int;

        #[pymodule_export]
        use crate::util::rect::Rect;

        #[pymodule_export]
        use crate::util::rect::Point;
    }
}
