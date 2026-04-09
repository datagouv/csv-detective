use std::collections::BTreeMap;
use std::path::PathBuf;

use clap::Parser;
use serde::Serialize;

mod detect;
mod formats;
pub mod value;

#[derive(Parser)]
#[command(name = "csv-detective-rs")]
struct Cli {
    file_path: PathBuf,

    #[arg(long, default_value_t = 500)]
    num_rows: i64,

    #[arg(long, default_value_t = false)]
    stats: bool,

}

#[derive(Serialize)]
struct ColumnDetection {
    python_type: String,
    format: String,
    score: f64,
}

#[derive(Serialize)]
struct Analysis {
    encoding: String,
    separator: String,
    heading_columns: usize,
    trailing_columns: usize,
    header_row_idx: usize,
    header: Vec<String>,
    total_lines: usize,
    nb_duplicates: usize,
    categorical: Vec<String>,
    columns_fields: BTreeMap<String, ColumnDetection>,
    columns_labels: BTreeMap<String, ColumnDetection>,
    columns: BTreeMap<String, ColumnDetection>,
    formats: BTreeMap<String, Vec<String>>,
}

fn main() {
    let cli = Cli::parse();
    let analysis = detect::analyze(&cli.file_path, cli.num_rows, cli.stats);
    let json = serde_json::to_string_pretty(&analysis).expect("Failed to serialize");
    println!("{json}");
}
