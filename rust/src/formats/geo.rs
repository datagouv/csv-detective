use crate::value::Value;

fn parse_float_not_int(val: &str) -> Option<f64> {
    if val.is_empty() {
        return None;
    }
    // must not be a pure integer
    if !val.contains('.') && !val.contains(',') {
        return None;
    }
    let normalized = val.replace(',', ".");
    normalized.parse::<f64>().ok()
}

pub fn detect_latitude_wgs(val: &str) -> Option<f64> {
    let f = parse_float_not_int(val)?;
    if (-90.0..=90.0).contains(&f) { Some(f) } else { None }
}

pub fn detect_longitude_wgs(val: &str) -> Option<f64> {
    let f = parse_float_not_int(val)?;
    if (-180.0..=180.0).contains(&f) { Some(f) } else { None }
}

pub fn test_latitude_wgs(val: &Value) -> bool {
    let raw = val.raw();
    if !raw.contains('.') && !raw.contains(',') { return false; }
    match val.as_float() {
        Some(f) => (-90.0..=90.0).contains(&f),
        None => false,
    }
}

pub fn test_longitude_wgs(val: &Value) -> bool {
    let raw = val.raw();
    if !raw.contains('.') && !raw.contains(',') { return false; }
    match val.as_float() {
        Some(f) => (-180.0..=180.0).contains(&f),
        None => false,
    }
}

pub fn test_latitude_wgs_fr(val: &Value) -> bool {
    let raw = val.raw();
    if !raw.contains('.') && !raw.contains(',') { return false; }
    match val.as_float() {
        Some(f) => (41.3..=51.3).contains(&f),
        None => false,
    }
}

pub fn test_longitude_wgs_fr(val: &Value) -> bool {
    let raw = val.raw();
    if !raw.contains('.') && !raw.contains(',') { return false; }
    match val.as_float() {
        Some(f) => (-5.5..=9.8).contains(&f),
        None => false,
    }
}

pub fn test_latitude_l93(val: &Value) -> bool {
    match val.as_float() {
        Some(f) => (6_000_000.0..=7_200_000.0).contains(&f),
        None => false,
    }
}

pub fn test_longitude_l93(val: &Value) -> bool {
    match val.as_float() {
        Some(f) => (100_000.0..=1_300_000.0).contains(&f),
        None => false,
    }
}
