use std::collections::BTreeMap;

use ahash::AHashMap as HashMap;
use std::fs;
use std::path::Path;

use chardetng::EncodingDetector;

use crate::formats::{self, Format};
use crate::value::Value;
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

pub fn process_text(val: &str) -> String {
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

// --- Data reading (streaming) ---

struct ColumnStats {
    value_counts: HashMap<String, usize>,
}

struct StreamedData {
    columns: Vec<ColumnStats>,
    total_lines: usize,
    nb_duplicates: usize,
}

fn stream_csv(reader: impl std::io::Read, sep_char: char, header_len: usize) -> StreamedData {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut columns: Vec<ColumnStats> = (0..header_len)
        .map(|_| ColumnStats { value_counts: HashMap::new() })
        .collect();
    let mut row_hashes: HashMap<u64, usize> = HashMap::new();
    let mut total_lines = 0usize;

    let mut rdr = csv::ReaderBuilder::new()
        .delimiter(sep_char as u8)
        .has_headers(true)
        .flexible(true)
        .from_reader(reader);

    for result in rdr.records() {
        let record = match result {
            Ok(r) => r,
            Err(_) => continue,
        };
        total_lines += 1;

        let mut hasher = DefaultHasher::new();
        for (i, col) in columns.iter_mut().enumerate() {
            let val = record.get(i).unwrap_or("");
            val.hash(&mut hasher);
            if let Some(count) = col.value_counts.get_mut(val) {
                *count += 1;
            } else {
                col.value_counts.insert(val.to_string(), 1);
            }
        }
        *row_hashes.entry(hasher.finish()).or_insert(0) += 1;
    }

    let nb_duplicates = row_hashes.values().filter(|&&c| c > 1).map(|&c| c - 1).sum();

    StreamedData {
        columns,
        total_lines,
        nb_duplicates,
    }
}

fn score_column_field(
    values: &[(Value, usize)],
    non_empty_total: usize,
    detector: &Format,
) -> f64 {
    if non_empty_total == 0 {
        return 1.0;
    }

    let max_failures = ((1.0 - detector.proportion()) * non_empty_total as f64) as usize;

    let mut matching = 0usize;
    let mut failing = 0usize;
    for (val, count) in values {
        if detector.test(val) {
            matching += count;
        } else {
            failing += count;
            if failing > max_failures {
                return 0.0;
            }
        }
    }

    let proportion = matching as f64 / non_empty_total as f64;
    if proportion >= detector.proportion() {
        proportion
    } else {
        0.0
    }
}

struct ScoringResult {
    field_scores: BTreeMap<String, BTreeMap<&'static str, f64>>,
    label_scores: BTreeMap<String, BTreeMap<&'static str, f64>>,
}

fn score_all(
    header: &[String],
    columns: &[ColumnStats],
    detectors: &[Format],
    total_lines: usize,
    stats: bool,
) -> ScoringResult {
    use std::time::Instant;

    let label_scores_per_det: Vec<Vec<f64>> = detectors
        .iter()
        .map(|det| {
            header
                .iter()
                .map(|col_name| header_score(col_name, det.labels()))
                .collect()
        })
        .collect();

    let mut format_times: Vec<(String, f64)> = if stats {
        detectors.iter().map(|d| (d.name().to_string(), 0.0)).collect()
    } else {
        Vec::new()
    };

    let mut field_scores: BTreeMap<String, BTreeMap<&'static str, f64>> = BTreeMap::new();
    let mut label_scores: BTreeMap<String, BTreeMap<&'static str, f64>> = BTreeMap::new();

    for (i, col_name) in header.iter().enumerate() {
        let col = &columns[i];
        let empty_count = col.value_counts.get("").copied().unwrap_or(0);
        let non_empty_total = total_lines - empty_count;

        let values: Vec<(Value, usize)> = col
            .value_counts
            .iter()
            .filter(|(v, _)| !v.is_empty())
            .map(|(v, &c)| (Value::new(v), c))
            .collect();

        if values.is_empty() {
            let mut col_field_scores = BTreeMap::new();
            let mut col_label_scores = BTreeMap::new();
            for det in detectors {
                col_field_scores.insert(det.name(), 1.0);
                col_label_scores.insert(det.name(), header_score(col_name, det.labels()));
            }
            field_scores.insert(col_name.clone(), col_field_scores);
            label_scores.insert(col_name.clone(), col_label_scores);
            continue;
        }

        let mut col_field_scores = BTreeMap::new();
        let mut col_label_scores = BTreeMap::new();

        for (det_idx, det) in detectors.iter().enumerate() {
            let ls = label_scores_per_det[det_idx][i];
            col_label_scores.insert(det.name(), ls);

            if det.mandatory_label() && ls == 0.0 {
                col_field_scores.insert(det.name(), 0.0);
                continue;
            }

            let t_det = Instant::now();
            let fs = score_column_field(&values, non_empty_total, det);
            if stats { format_times[det_idx].1 += t_det.elapsed().as_secs_f64(); }
            col_field_scores.insert(det.name(), fs);
        }

        field_scores.insert(col_name.clone(), col_field_scores);
        label_scores.insert(col_name.clone(), col_label_scores);
    }

    if stats {
        let total_uniques: usize = columns.iter().map(|c| c.value_counts.keys().filter(|v| !v.is_empty()).count()).sum();
        eprintln!("[stats] total unique values across cols: {total_uniques}");
        format_times.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        for (name, time) in &format_times {
            if *time > 0.001 {
                eprintln!("[stats]   {name:<35} {time:.3}s");
            }
        }
    }

    ScoringResult {
        field_scores,
        label_scores,
    }
}

fn handle_empty_columns(field_scores: &mut BTreeMap<String, BTreeMap<&'static str, f64>>) {
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
    detectors: &[Format],
    priorities: &Priorities,
) -> (
    BTreeMap<String, ColumnDetection>,
    BTreeMap<String, Vec<String>>,
) {
    let det_map: HashMap<&str, &Format> = detectors
        .iter()
        .map(|d| (d.name(), d))
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
        let mut combined: BTreeMap<&'static str, f64> = BTreeMap::new();
        for (&fmt_name, &field_score) in fs {
            let label_score = ls.get(fmt_name).copied().unwrap_or(0.0);
            let mut score = field_score * (1.0 + label_score / 2.0);

            if mandatory_labels.contains(&fmt_name) && label_score == 0.0 {
                score = 0.0;
            }

            if score > 0.0 {
                combined.insert(fmt_name, score);
            }
        }

        // deprioritize int/float if other formats detected
        let has_non_numeric = combined.keys().any(|k| *k != "float" && *k != "int");
        let mut formats_to_remove: Vec<&str> = Vec::new();
        if has_non_numeric {
            formats_to_remove.push("float");
            formats_to_remove.push("int");
        }

        // apply priority rules
        for (prio, secondaries) in &priorities.rules {
            if let Some(&prio_score) = combined.get(*prio) {
                for sec in secondaries {
                    if let Some(&sec_score) = combined.get(*sec) {
                        if prio_score >= sec_score || prio_score >= 1.0 {
                            formats_to_remove.push(sec);
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
            .max_by(|a, b| {
                a.1.partial_cmp(b.1)
                    .unwrap_or(std::cmp::Ordering::Equal)
                    .then(b.0.cmp(a.0))
            });

        let detection = match best {
            Some((&fmt_name, &score)) => {
                let python_type = det_map
                    .get(fmt_name)
                    .map(|d| d.python_type())
                    .unwrap_or("string");
                ColumnDetection {
                    python_type: python_type.to_string(),
                    format: fmt_name.to_string(),
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

fn detect_categorical(columns: &[ColumnStats], header: &[String], total_lines: usize) -> Vec<String> {
    let mut result = Vec::new();
    for (i, col) in columns.iter().enumerate() {
        if total_lines == 0 {
            continue;
        }
        let n_unique = col.value_counts.keys().filter(|v| !v.is_empty()).count();
        if n_unique <= MAX_CATEGORICAL_VALUES
            || (n_unique as f64 / total_lines as f64) <= CATEGORICAL_PCT
        {
            result.push(header[i].clone());
        }
    }
    result
}

// --- Main analysis ---

pub fn analyze(file_path: &Path, _num_rows: i64, stats: bool) -> Analysis {
    use std::io::{BufRead, BufReader, Read, Seek, SeekFrom};
    use std::time::Instant;

    let t_start = Instant::now();

    let mut file = match fs::File::open(file_path) {
        Ok(f) => f,
        Err(_) => return empty_analysis(),
    };

    // Read a sample (first 64KB) for encoding detection
    let mut sample_buf = vec![0u8; 64 * 1024];
    let sample_len = {
        use std::io::Read;
        let mut total = 0;
        while total < sample_buf.len() {
            match file.read(&mut sample_buf[total..]) {
                Ok(0) => break,
                Ok(n) => total += n,
                Err(_) => break,
            }
        }
        total
    };
    sample_buf.truncate(sample_len);

    let encoding = detect_encoding(&sample_buf);
    let is_utf8 = encoding == "utf-8";

    #[allow(unused_assignments)]
    let mut full_content = String::new();
    let mut reader: Box<dyn BufRead> = if is_utf8 {
        file.seek(SeekFrom::Start(0)).unwrap();
        Box::new(BufReader::new(file))
    } else {
        let raw = if sample_len < 64 * 1024 {
            sample_buf.clone()
        } else {
            file.seek(SeekFrom::Start(0)).unwrap();
            let mut all = Vec::new();
            std::io::Read::read_to_end(&mut file, &mut all).unwrap_or(0);
            all
        };
        let enc = encoding_rs::Encoding::for_label(encoding.as_bytes()).unwrap_or(encoding_rs::UTF_8);
        let (decoded, _, _) = enc.decode(&raw);
        full_content = decoded.into_owned();
        Box::new(std::io::Cursor::new(full_content.as_bytes()))
    };
    if stats { eprintln!("[stats] read + decode: {:.3}s", t_start.elapsed().as_secs_f64()); }

    // Read lines until we find the header (first line that differs from previous)
    let mut header_row_idx = 0;
    let mut header_line = String::new();
    if reader.read_line(&mut header_line).unwrap_or(0) == 0 {
        return empty_analysis();
    }
    let header_line = header_line.trim_end_matches('\n').trim_end_matches('\r').to_string();

    let mut sample_lines: Vec<String> = vec![header_line.clone()];
    loop {
        let mut next_line = String::new();
        if reader.read_line(&mut next_line).unwrap_or(0) == 0 {
            break;
        }
        let next_line = next_line.trim_end_matches('\n').trim_end_matches('\r').to_string();
        sample_lines.push(next_line.clone());
        if next_line != header_line {
            break;
        }
        header_row_idx += 1;
    }
    let header_line = &sample_lines[header_row_idx];

    let separator = detect_separator(header_line);
    let sep_char = match separator.as_str() {
        "\\t" => '\t',
        s => s.chars().next().unwrap_or(','),
    };

    let sample_refs: Vec<&str> = sample_lines.iter().map(|s| s.as_str()).collect();
    let (heading_columns, trailing_columns) = count_edge_columns(&sample_refs, sep_char);

    let header: Vec<String> = {
        let mut rdr = csv::ReaderBuilder::new()
            .delimiter(sep_char as u8)
            .has_headers(false)
            .from_reader(header_line.as_bytes());
        match rdr.records().next() {
            Some(Ok(record)) => record.iter().map(|s| s.trim().to_string()).collect(),
            _ => header_line.split(sep_char).map(|s| s.trim().to_string()).collect(),
        }
    };

    // Build a chained reader: remaining sample lines + rest of file
    let remaining_sample: String = sample_lines[header_row_idx..].join("\n") + "\n";
    let chained = std::io::Cursor::new(remaining_sample.into_bytes()).chain(reader);

    let t_csv = Instant::now();
    let streamed = stream_csv(chained, sep_char, header.len());
    if stats { eprintln!("[stats] csv streaming + value_counts + duplicates ({} lines, {} cols): {:.3}s", streamed.total_lines, header.len(), t_csv.elapsed().as_secs_f64()); }

    let total_lines = streamed.total_lines;
    let nb_duplicates = streamed.nb_duplicates;
    let categorical = detect_categorical(&streamed.columns, &header, total_lines);

    let detectors = formats::all_formats();
    let t_score = Instant::now();
    let mut scoring = score_all(&header, &streamed.columns, &detectors, total_lines, stats);
    if stats { eprintln!("[stats] scoring total: {:.3}s", t_score.elapsed().as_secs_f64()); }
    handle_empty_columns(&mut scoring.field_scores);

    let priorities = Priorities::new();
    let (columns, formats) =
        build_combined_output(&header, &scoring, &detectors, &priorities);

    if stats { eprintln!("[stats] total: {:.3}s", t_start.elapsed().as_secs_f64()); }

    Analysis {
        encoding,
        separator,
        heading_columns,
        trailing_columns,
        header_row_idx,
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
