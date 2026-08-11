use crate::value::Value;

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

pub fn test(val: &Value) -> bool { test_date_fr(val.normalized()) }
