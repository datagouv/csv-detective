use std::collections::HashSet;
use std::sync::LazyLock;

use super::Detector;

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

const COUNTRY_LABELS: &[(&str, f64)] = &[
    ("iso country code", 1.0), ("code pays", 1.0), ("pays", 1.0),
    ("country", 1.0), ("nation", 1.0), ("pays code", 1.0),
    ("code pays (iso)", 1.0), ("code", 0.5),
];

// --- Alpha-2 ---

pub struct IsoAlpha2Format;

impl IsoAlpha2Format {
    pub fn detect(&self, val: &str) -> Option<()> {
        if val.len() != 2 || !val.bytes().all(|b| b.is_ascii_alphabetic()) {
            return None;
        }
        let upper = val.to_uppercase();
        if ALPHA2.contains(&upper) { Some(()) } else { None }
    }
}

impl Detector for IsoAlpha2Format {
    fn name(&self) -> &'static str { "iso_country_code_alpha2" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] { COUNTRY_LABELS }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}

// --- Alpha-3 ---

pub struct IsoAlpha3Format;

impl IsoAlpha3Format {
    pub fn detect(&self, val: &str) -> Option<()> {
        if val.len() != 3 || !val.bytes().all(|b| b.is_ascii_alphabetic()) {
            return None;
        }
        let upper = val.to_uppercase();
        if ALPHA3.contains(&upper) { Some(()) } else { None }
    }
}

impl Detector for IsoAlpha3Format {
    fn name(&self) -> &'static str { "iso_country_code_alpha3" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] { COUNTRY_LABELS }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}

// --- Numeric ---

pub struct IsoNumericFormat;

impl IsoNumericFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        if val.len() != 3 || !val.bytes().all(|b| b.is_ascii_digit()) {
            return None;
        }
        if NUMERIC.contains(val) { Some(()) } else { None }
    }
}

impl Detector for IsoNumericFormat {
    fn name(&self) -> &'static str { "iso_country_code_numeric" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] { COUNTRY_LABELS }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
