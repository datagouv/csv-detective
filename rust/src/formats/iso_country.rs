use std::collections::HashSet;
use std::sync::LazyLock;

use crate::value::Value;

static ALPHA2: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/iso_country_code_alpha2.txt")
        .lines()
        .map(|l| l.trim().to_uppercase())
        .filter(|l| !l.is_empty())
        .collect()
});

static ALPHA3: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/iso_country_code_alpha3.txt")
        .lines()
        .map(|l| l.trim().to_uppercase())
        .filter(|l| !l.is_empty())
        .collect()
});

static NUMERIC: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/iso_country_code_numeric.txt")
        .lines()
        .map(|l| l.trim().to_string())
        .filter(|l| !l.is_empty())
        .collect()
});

pub fn test_alpha2(val: &Value) -> bool {
    let raw = val.raw();
    if raw.len() != 2 || !raw.bytes().all(|b| b.is_ascii_alphabetic()) {
        return false;
    }
    let upper = raw.to_uppercase();
    ALPHA2.contains(&upper)
}

pub fn test_alpha3(val: &Value) -> bool {
    let raw = val.raw();
    if raw.len() != 3 || !raw.bytes().all(|b| b.is_ascii_alphabetic()) {
        return false;
    }
    let upper = raw.to_uppercase();
    ALPHA3.contains(&upper)
}

pub fn test_numeric(val: &Value) -> bool {
    let raw = val.raw();
    if raw.len() != 3 || !raw.bytes().all(|b| b.is_ascii_digit()) {
        return false;
    }
    NUMERIC.contains(raw)
}
