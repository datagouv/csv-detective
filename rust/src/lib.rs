use std::collections::BTreeMap;

use serde::Serialize;

pub mod detect;
pub mod formats;
pub mod value;

#[cfg(feature = "python")]
mod python;

#[derive(Serialize)]
pub struct ColumnDetection {
    pub python_type: String,
    pub format: String,
    pub score: f64,
}

#[derive(Serialize)]
pub struct Analysis {
    pub encoding: String,
    pub separator: String,
    pub heading_columns: usize,
    pub trailing_columns: usize,
    pub header_row_idx: usize,
    pub header: Vec<String>,
    pub total_lines: usize,
    pub nb_duplicates: usize,
    pub categorical: Vec<String>,
    pub columns_fields: BTreeMap<String, ColumnDetection>,
    pub columns_labels: BTreeMap<String, ColumnDetection>,
    pub columns: BTreeMap<String, ColumnDetection>,
    pub formats: BTreeMap<String, Vec<String>>,
}
