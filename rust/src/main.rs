use std::path::PathBuf;

use clap::Parser;

use csv_detective_rs::detect;

#[derive(Parser)]
#[command(name = "csv-detective-rs")]
struct Cli {
    file_path: PathBuf,

    #[arg(long, default_value_t = 500)]
    num_rows: i64,

    #[arg(long, default_value_t = false)]
    stats: bool,
}

fn main() {
    let cli = Cli::parse();
    let analysis = detect::analyze(&cli.file_path, cli.num_rows, cli.stats);
    let json = serde_json::to_string_pretty(&analysis).expect("Failed to serialize");
    println!("{json}");
}
