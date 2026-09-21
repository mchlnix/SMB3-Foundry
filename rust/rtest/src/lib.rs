use pyo3::prelude::*;
use pyo3::py_run;
use crate::level_1::level_2::level_3::clazz::Class;

mod level_1;

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
fn rtest (_py: Python, rtest: &Bound<PyModule>) -> PyResult<()> {
    let level_1 = add_submodule!(rtest, "rtest.level_1");
    let level_2 = add_submodule!(level_1, "rtest.level_1.level_2");
    let level_3 = add_submodule!(level_2, "rtest.level_1.level_2.level_3");
    let clazz = add_submodule!(level_3, "rtest.level_1.level_2.level_3.clazz");
    
    clazz.add_class::<Class>()?;

    Ok(())
}
