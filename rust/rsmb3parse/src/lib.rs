mod data_points;
mod labels;
mod position;
mod types;
mod util;

use pyo3::prelude::*;
use pyo3::py_run;
use crate::util::rect::{Point, Rect};
use crate::util::rom::{INESHeader, Rom};

macro_rules! add_submodule {
    ($parent_module:ident ,$module_path:literal) => {
        {
            let module = PyModule::new($parent_module.py(), $module_path)?;
            py_run!($parent_module.py(), module, &format!("import sys; sys.modules['{}'] = module", $module_path));
            $parent_module.add_submodule(&module)?;

            module
        }
    };
}

#[pymodule]
fn rsmb3parse (_py: Python, root: &Bound<PyModule>) -> PyResult<()> {
    let util: Bound<PyModule> = add_submodule!(root, "rsmb3parse.util");

    util.add_function(wrap_pyfunction!(util::funcs::clamp, &util)?)?;
    util.add_function(wrap_pyfunction!(util::funcs::hex_int, &util)?)?;

    util.add_class::<Point>()?;
    util.add_class::<Rect>()?;

    util.add_class::<INESHeader>()?;
    util.add_class::<Rom>()?;

    Ok(())
}