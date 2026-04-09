use super::Detector;
use crate::value::Value;

pub struct DateFrFormat;

const MOIS: &[&str] = &[
    "janvier", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
];

fn test_date_fr(normalized: &str) -> bool {
    let bytes = normalized.as_bytes();
    if bytes.is_empty() {
        return false;
    }

    let mut i = 0;
    if i < bytes.len() && bytes[i] == b'0' {
        i += 1;
    }
    if i >= bytes.len() || !bytes[i].is_ascii_digit() {
        return false;
    }
    i += 1;
    if i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }

    if i >= bytes.len() || !matches!(bytes[i], b' ' | b'-' | b'/') {
        return false;
    }
    i += 1;

    let month_start = i;
    while i < bytes.len() && bytes[i].is_ascii_alphabetic() {
        i += 1;
    }
    let month = &normalized[month_start..i];
    if !MOIS.contains(&month) {
        return false;
    }

    if i >= bytes.len() || !matches!(bytes[i], b' ' | b'-' | b'/') {
        return false;
    }
    i += 1;

    let year_start = i;
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    if i - year_start != 4 {
        return false;
    }

    i == bytes.len()
}

impl Detector for DateFrFormat {
    fn name(&self) -> &'static str { "date_fr" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["fr", "temp"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("date", 1.0)]
    }
    fn test(&self, val: &Value) -> bool { test_date_fr(val.normalized()) }
}
