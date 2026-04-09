use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

use chardetng::EncodingDetector;

use crate::Analysis;

const SEPARATORS: &[char] = &[';', ',', '|', '\t'];

fn detect_encoding(raw: &[u8]) -> String {
    match std::str::from_utf8(raw) {
        Ok(_) => return "utf-8".to_string(),
        Err(_) => {}
    }

    let mut detector = EncodingDetector::new();
    detector.feed(raw, true);
    let encoding = detector.guess(None, true);
    encoding.name().to_lowercase().to_string()
}

fn detect_separator(first_line: &str) -> String {
    let mut best_sep = ',';
    let mut best_count = 0;

    for &sep in SEPARATORS {
        let count = first_line.chars().filter(|&c| c == sep).count();
        if count > best_count {
            best_count = count;
            best_sep = sep;
        }
    }

    match best_sep {
        '\t' => "\\t".to_string(),
        c => c.to_string(),
    }
}

fn count_edge_columns(lines: &[&str], separator: char) -> (usize, usize) {
    if lines.is_empty() {
        return (0, 0);
    }

    let mut min_heading = usize::MAX;
    let mut min_trailing = usize::MAX;

    for line in lines {
        let fields: Vec<&str> = line.split(separator).collect();

        let heading = fields.iter().take_while(|f| f.is_empty()).count();
        let trailing = fields.iter().rev().take_while(|f| f.is_empty()).count();

        min_heading = min_heading.min(heading);
        min_trailing = min_trailing.min(trailing);
    }

    (
        if min_heading == usize::MAX { 0 } else { min_heading },
        if min_trailing == usize::MAX { 0 } else { min_trailing },
    )
}

pub fn analyze(file_path: &Path, _num_rows: i64) -> Analysis {
    let raw = fs::read(file_path).expect("Failed to read file");
    let encoding = detect_encoding(&raw);

    let content = if encoding == "utf-8" {
        String::from_utf8(raw).unwrap()
    } else {
        let enc = encoding_rs::Encoding::for_label(encoding.as_bytes())
            .unwrap_or(encoding_rs::UTF_8);
        let (decoded, _, _) = enc.decode(&raw);
        decoded.into_owned()
    };

    let lines: Vec<&str> = content.lines().collect();
    if lines.is_empty() {
        panic!("File is empty");
    }

    let separator = detect_separator(lines[0]);
    let sep_char = match separator.as_str() {
        "\\t" => '\t',
        s => s.chars().next().unwrap(),
    };

    let sample_lines: Vec<&str> = lines.iter().take(10).copied().collect();
    let (heading_columns, trailing_columns) = count_edge_columns(&sample_lines[1..], sep_char);

    let header: Vec<String> = lines[0]
        .split(sep_char)
        .map(|s| s.trim().to_string())
        .collect();

    let total_lines = if lines.len() > 1 { lines.len() - 1 } else { 0 };

    let columns_fields = BTreeMap::new();
    let columns_labels = BTreeMap::new();
    let columns = BTreeMap::new();
    let formats = BTreeMap::new();

    Analysis {
        encoding,
        separator,
        heading_columns,
        trailing_columns,
        header_row_idx: 0,
        header,
        total_lines,
        nb_duplicates: 0,
        categorical: vec![],
        columns_fields,
        columns_labels,
        columns,
        formats,
    }
}
