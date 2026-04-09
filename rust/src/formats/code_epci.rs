use super::Detector;
use crate::value::Value;
use super::siren::luhn_check;

pub struct CodeEpciFormat;

impl CodeEpciFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let cleaned: String = val.chars().filter(|c| *c != ' ').collect();
        let bytes = cleaned.as_bytes();
        if bytes.len() != 9 || !bytes[0] == b'2' {
            return None;
        }
        if !bytes.iter().all(|b| b.is_ascii_digit()) {
            return None;
        }
        if bytes[0] != b'2' {
            return None;
        }
        luhn_check(bytes)
    }
}

impl Detector for CodeEpciFormat {
    fn name(&self) -> &'static str { "code_epci" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.9 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("epci", 1.0)]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
