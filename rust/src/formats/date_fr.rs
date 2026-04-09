use super::Detector;
use super::fr_geo::normalize;

pub struct DateFrFormat;

const MOIS: &[&str] = &[
    "janvier", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
];

impl DateFrFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^(0?[1-9]|[12][0-9]|3[01])[ \-/](mois)[ \-/]\d{4}$
        let normalized = normalize(val);
        let bytes = normalized.as_bytes();
        if bytes.is_empty() {
            return None;
        }

        let mut i = 0;
        // day: 1 or 2 digits
        if i < bytes.len() && bytes[i] == b'0' {
            i += 1;
        }
        if i >= bytes.len() || !bytes[i].is_ascii_digit() {
            return None;
        }
        i += 1;
        if i < bytes.len() && bytes[i].is_ascii_digit() {
            i += 1;
        }

        // separator
        if i >= bytes.len() || !matches!(bytes[i], b' ' | b'-' | b'/') {
            return None;
        }
        i += 1;

        // month name
        let month_start = i;
        while i < bytes.len() && bytes[i].is_ascii_alphabetic() {
            i += 1;
        }
        let month = &normalized[month_start..i];
        if !MOIS.contains(&month) {
            return None;
        }

        // separator
        if i >= bytes.len() || !matches!(bytes[i], b' ' | b'-' | b'/') {
            return None;
        }
        i += 1;

        // year: exactly 4 digits
        let year_start = i;
        while i < bytes.len() && bytes[i].is_ascii_digit() {
            i += 1;
        }
        if i - year_start != 4 {
            return None;
        }

        if i == bytes.len() { Some(()) } else { None }
    }
}

impl Detector for DateFrFormat {
    fn name(&self) -> &'static str { "date_fr" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["fr", "temp"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("date", 1.0)]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
