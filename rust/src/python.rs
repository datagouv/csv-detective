use std::path::Path;

use pyo3::prelude::*;
use crate::detect;

#[pyfunction]
#[pyo3(signature = (file_path, num_rows=500))]
fn routine(py: Python<'_>, file_path: &str, num_rows: i64) -> PyResult<PyObject> {
    let analysis = detect::analyze(Path::new(file_path), num_rows, false);
    let json_str =
        serde_json::to_string(&analysis).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    let json_module = py.import("json")?;
    let result = json_module.call_method1("loads", (json_str,))?;
    Ok(result.into())
}

#[pymodule]
fn csv_detective_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(routine, m)?)?;
    Ok(())
}
