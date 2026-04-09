use super::Detector;
use crate::value::Value;

pub struct CodeCspInseeFormat;

const SPECIAL_CODES: &[&str] = &[
    "7100", "7200", "7400", "7500", "7700", "7800", "8100", "8300", "8400", "8500", "8600",
];

impl CodeCspInseeFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        if val.len() != 4 {
            return None;
        }
        if SPECIAL_CODES.contains(&val) {
            return Some(());
        }
        // ^[123456][0-9]{2}[abcdefghijkl]$
        let bytes = val.as_bytes();
        if !matches!(bytes[0], b'1'..=b'6') {
            return None;
        }
        if !bytes[1].is_ascii_digit() || !bytes[2].is_ascii_digit() {
            return None;
        }
        if matches!(bytes[3], b'a'..=b'l') { Some(()) } else { None }
    }
}

impl Detector for CodeCspInseeFormat {
    fn name(&self) -> &'static str { "code_csp_insee" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("code csp insee", 1.0), ("code csp", 1.0)]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
