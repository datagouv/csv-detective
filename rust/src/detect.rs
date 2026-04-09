use std::collections::{BTreeMap, HashMap};
use std::fs;
use std::path::Path;

use chardetng::EncodingDetector;

use crate::formats::{self, Detector};
use crate::{Analysis, ColumnDetection};

const SEPARATORS: &[char] = &[';', ',', '|', '\t'];
const MAX_CATEGORICAL_VALUES: usize = 25;
const CATEGORICAL_PCT: f64 = 0.05;

fn detect_encoding(raw: &[u8]) -> String {
    if std::str::from_utf8(raw).is_ok() {
        return "utf-8".to_string();
    }

    let mut detector = EncodingDetector::new();
    detector.feed(raw, true);
    let encoding = detector.guess(None, true);
    encoding.name().to_lowercase()
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

// --- Text normalization for label scoring ---

fn camel_case_split(s: &str) -> String {
    let mut result = String::with_capacity(s.len() + 4);
    let chars: Vec<char> = s.chars().collect();

    for i in 0..chars.len() {
        if i > 0 && chars[i].is_ascii_uppercase() {
            if chars[i - 1].is_ascii_lowercase() {
                result.push(' ');
            } else if i + 1 < chars.len() && chars[i + 1].is_ascii_lowercase() {
                result.push(' ');
            }
        }
        result.push(chars[i]);
    }
    result
}

fn process_text(val: &str) -> String {
    let val = camel_case_split(val);
    let mut val = val.to_lowercase();

    let replacements: &[(&str, &str)] = &[
        ("à", "a"),
        ("â", "a"),
        ("ç", "c"),
        ("é", "e"),
        ("è", "e"),
        ("ê", "e"),
        ("Ã©", "e"),
        ("î", "i"),
        ("ï", "i"),
        ("ô", "o"),
        ("ö", "o"),
        ("ù", "u"),
        ("û", "u"),
        ("ü", "u"),
        ("-", " "),
        ("_", " "),
        ("'", " "),
        (",", " "),
        ("  ", " "),
    ];

    for (from, to) in replacements {
        val = val.replace(from, to);
    }

    val.trim().to_string()
}

fn header_score(header: &str, labels: &[(&str, f64)]) -> f64 {
    if labels.is_empty() {
        return 0.0;
    }

    let processed = process_text(header);

    let exact_score = labels
        .iter()
        .map(|(label, cred)| if *label == processed { *cred } else { 0.0 })
        .fold(0.0_f64, f64::max);

    let partial_score = labels
        .iter()
        .map(|(label, cred)| {
            if label.len() > 2 && processed.contains(label) {
                0.5 * cred
            } else {
                0.0
            }
        })
        .fold(0.0_f64, f64::max);

    exact_score.max(partial_score)
}

// --- Data reading ---

struct ColumnData {
    values: Vec<String>,
}

fn read_csv_data(content: &str, sep_char: char, header_len: usize) -> Vec<ColumnData> {
    let mut columns: Vec<ColumnData> = (0..header_len)
        .map(|_| ColumnData { values: Vec::new() })
        .collect();

    for line in content.lines().skip(1) {
        if line.is_empty() {
            continue;
        }
        let fields: Vec<&str> = line.split(sep_char).collect();
        for (i, col) in columns.iter_mut().enumerate() {
            let val = fields.get(i).unwrap_or(&"").trim();
            col.values.push(val.to_string());
        }
    }

    columns
}

// --- Scoring pipeline ---

fn compute_value_counts(values: &[String]) -> HashMap<&str, usize> {
    let mut counts: HashMap<&str, usize> = HashMap::new();
    for val in values {
        *counts.entry(val.as_str()).or_insert(0) += 1;
    }
    counts
}

fn score_column_field(
    value_counts: &HashMap<&str, usize>,
    total: usize,
    detector: &dyn Detector,
) -> f64 {
    if total == 0 {
        return 1.0;
    }

    let mut matching = 0usize;
    for (&val, &count) in value_counts {
        if val.is_empty() {
            // skipna=True: NaN/empty values count as matching
            matching += count;
        } else if detector.test(val) {
            matching += count;
        }
    }

    let proportion = matching as f64 / total as f64;
    if proportion >= detector.proportion() {
        proportion
    } else {
        0.0
    }
}

struct ScoringResult {
    field_scores: BTreeMap<String, BTreeMap<String, f64>>,
    label_scores: BTreeMap<String, BTreeMap<String, f64>>,
}

fn score_all(
    header: &[String],
    columns: &[ColumnData],
    detectors: &[Box<dyn Detector>],
) -> ScoringResult {
    let mut field_scores: BTreeMap<String, BTreeMap<String, f64>> = BTreeMap::new();
    let mut label_scores: BTreeMap<String, BTreeMap<String, f64>> = BTreeMap::new();

    for (i, col_name) in header.iter().enumerate() {
        let col_data = &columns[i];
        let value_counts = compute_value_counts(&col_data.values);
        let total = col_data.values.len();

        let mut col_field_scores = BTreeMap::new();
        let mut col_label_scores = BTreeMap::new();

        for det in detectors {
            let fs = score_column_field(&value_counts, total, det.as_ref());
            col_field_scores.insert(det.name().to_string(), fs);

            let ls = header_score(col_name, det.labels());
            col_label_scores.insert(det.name().to_string(), ls);
        }

        field_scores.insert(col_name.clone(), col_field_scores);
        label_scores.insert(col_name.clone(), col_label_scores);
    }

    ScoringResult {
        field_scores,
        label_scores,
    }
}

fn handle_empty_columns(field_scores: &mut BTreeMap<String, BTreeMap<String, f64>>) {
    for (_col_name, scores) in field_scores.iter_mut() {
        let all_one = !scores.is_empty() && scores.values().all(|&s| s == 1.0);
        if all_one {
            for s in scores.values_mut() {
                *s = 0.0;
            }
        }
    }
}

struct Priorities {
    rules: Vec<(&'static str, Vec<&'static str>)>,
}

impl Priorities {
    fn new() -> Self {
        Self {
            rules: vec![
                ("int", vec!["float"]),
                (
                    "booleen",
                    vec![
                        "latitude_l93",
                        "latitude_wgs",
                        "latitude_wgs_fr_metropole",
                        "longitude_l93",
                        "longitude_wgs",
                        "longitude_wgs_fr_metropole",
                    ],
                ),
                ("geojson", vec!["json"]),
                ("latlon_wgs", vec!["json", "lonlat_wgs"]),
                ("lonlat_wgs", vec!["json"]),
                (
                    "latitude_wgs_fr_metropole",
                    vec!["latitude_l93", "latitude_wgs"],
                ),
                (
                    "longitude_wgs_fr_metropole",
                    vec!["longitude_l93", "longitude_wgs"],
                ),
                ("latitude_wgs", vec!["latitude_l93"]),
                ("longitude_wgs", vec!["longitude_l93"]),
                ("code_region", vec!["code_departement"]),
                ("datetime_rfc822", vec!["datetime_aware"]),
                ("code_epci", vec!["siren"]),
            ],
        }
    }
}

fn build_combined_output(
    header: &[String],
    scoring: &ScoringResult,
    detectors: &[Box<dyn Detector>],
    priorities: &Priorities,
) -> (
    BTreeMap<String, ColumnDetection>,
    BTreeMap<String, Vec<String>>,
) {
    let det_map: HashMap<&str, &dyn Detector> = detectors
        .iter()
        .map(|d| (d.name(), d.as_ref()))
        .collect();

    let mandatory_labels: Vec<&str> = detectors
        .iter()
        .filter(|d| d.mandatory_label())
        .map(|d| d.name())
        .collect();

    let mut columns_output: BTreeMap<String, ColumnDetection> = BTreeMap::new();
    let mut formats_index: BTreeMap<String, Vec<String>> = BTreeMap::new();

    for col_name in header {
        let fs = match scoring.field_scores.get(col_name) {
            Some(s) => s,
            None => continue,
        };
        let ls = match scoring.label_scores.get(col_name) {
            Some(s) => s,
            None => continue,
        };

        // combined = field * (1 + label / 2)
        let mut combined: BTreeMap<String, f64> = BTreeMap::new();
        for (fmt_name, &field_score) in fs {
            let label_score = ls.get(fmt_name).copied().unwrap_or(0.0);
            let mut score = field_score * (1.0 + label_score / 2.0);

            // mandatory label: zero out if label doesn't match
            if mandatory_labels.contains(&fmt_name.as_str()) && label_score == 0.0 {
                score = 0.0;
            }

            if score > 0.0 {
                combined.insert(fmt_name.clone(), score);
            }
        }

        // deprioritize int/float if other formats detected
        let non_numeric: Vec<&String> = combined
            .keys()
            .filter(|k| *k != "float" && *k != "int")
            .collect();
        let mut formats_to_remove: Vec<String> = Vec::new();
        if !non_numeric.is_empty() {
            formats_to_remove.push("float".to_string());
            formats_to_remove.push("int".to_string());
        }

        // apply priority rules
        for (prio, secondaries) in &priorities.rules {
            if let Some(&prio_score) = combined.get(*prio) {
                for sec in secondaries {
                    if let Some(&sec_score) = combined.get(*sec) {
                        if prio_score >= sec_score || prio_score >= 1.0 {
                            formats_to_remove.push(sec.to_string());
                        }
                    }
                }
            }
        }

        for fmt in &formats_to_remove {
            combined.remove(fmt);
        }

        // pick the best or fallback to string
        let best = combined
            .iter()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal));

        let detection = match best {
            Some((fmt_name, &score)) => {
                let python_type = det_map
                    .get(fmt_name.as_str())
                    .map(|d| d.python_type())
                    .unwrap_or("string");
                ColumnDetection {
                    python_type: python_type.to_string(),
                    format: fmt_name.clone(),
                    score,
                }
            }
            None => ColumnDetection {
                python_type: "string".to_string(),
                format: "string".to_string(),
                score: 1.0,
            },
        };

        formats_index
            .entry(detection.format.clone())
            .or_default()
            .push(col_name.clone());
        columns_output.insert(col_name.clone(), detection);
    }

    (columns_output, formats_index)
}

// --- Categorical detection ---

fn detect_categorical(columns: &[ColumnData], header: &[String]) -> Vec<String> {
    let mut result = Vec::new();
    for (i, col) in columns.iter().enumerate() {
        let total = col.values.len();
        if total == 0 {
            continue;
        }
        let unique: std::collections::HashSet<&str> =
            col.values.iter().map(|s| s.as_str()).collect();
        let n_unique = unique.len();
        if n_unique <= MAX_CATEGORICAL_VALUES
            || (n_unique as f64 / total as f64) <= CATEGORICAL_PCT
        {
            result.push(header[i].clone());
        }
    }
    result
}

// --- Duplicates ---

fn count_duplicates(content: &str) -> usize {
    let mut row_counts: HashMap<&str, usize> = HashMap::new();
    for line in content.lines().skip(1) {
        if line.is_empty() {
            continue;
        }
        *row_counts.entry(line).or_insert(0) += 1;
    }
    row_counts.values().filter(|&&c| c > 1).count()
}

// --- Main analysis ---

pub fn analyze(file_path: &Path, _num_rows: i64) -> Analysis {
    let raw = fs::read(file_path).unwrap_or_default();
    let encoding = detect_encoding(&raw);

    let content = if encoding == "utf-8" {
        String::from_utf8(raw).unwrap_or_default()
    } else {
        let enc =
            encoding_rs::Encoding::for_label(encoding.as_bytes()).unwrap_or(encoding_rs::UTF_8);
        let (decoded, _, _) = enc.decode(&raw);
        decoded.into_owned()
    };

    let lines: Vec<&str> = content.lines().collect();
    if lines.is_empty() {
        return empty_analysis();
    }

    let separator = detect_separator(lines[0]);
    let sep_char = match separator.as_str() {
        "\\t" => '\t',
        s => s.chars().next().unwrap_or(','),
    };

    let sample_lines: Vec<&str> = lines.iter().take(10).copied().collect();
    let (heading_columns, trailing_columns) = count_edge_columns(&sample_lines[1..], sep_char);

    let header: Vec<String> = lines[0]
        .split(sep_char)
        .map(|s| s.trim().to_string())
        .collect();

    let total_lines = if lines.len() > 1 { lines.len() - 1 } else { 0 };
    let nb_duplicates = count_duplicates(&content);

    let columns_data = read_csv_data(&content, sep_char, header.len());
    let categorical = detect_categorical(&columns_data, &header);

    let detectors = formats::all_detectors();
    let mut scoring = score_all(&header, &columns_data, &detectors);
    handle_empty_columns(&mut scoring.field_scores);

    let priorities = Priorities::new();
    let (columns, formats) =
        build_combined_output(&header, &scoring, &detectors, &priorities);

    Analysis {
        encoding,
        separator,
        heading_columns,
        trailing_columns,
        header_row_idx: 0,
        header,
        total_lines,
        nb_duplicates,
        categorical,
        columns_fields: BTreeMap::new(),
        columns_labels: BTreeMap::new(),
        columns,
        formats,
    }
}

fn empty_analysis() -> Analysis {
    Analysis {
        encoding: String::new(),
        separator: String::new(),
        heading_columns: 0,
        trailing_columns: 0,
        header_row_idx: 0,
        header: Vec::new(),
        total_lines: 0,
        nb_duplicates: 0,
        categorical: Vec::new(),
        columns_fields: BTreeMap::new(),
        columns_labels: BTreeMap::new(),
        columns: BTreeMap::new(),
        formats: BTreeMap::new(),
    }
}
