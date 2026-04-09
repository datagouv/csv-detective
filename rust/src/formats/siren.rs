use super::Detector;
use crate::value::Value;

pub struct SirenFormat;

pub fn luhn_check(digits: &[u8]) -> Option<()> {
    let mut sum = 0u32;
    let mut double = digits.len() % 2 == 0;
    for &b in digits {
        let mut d = (b - b'0') as u32;
        if double {
            d *= 2;
        }
        sum += d / 10 + d % 10;
        double = !double;
    }
    if sum % 10 == 0 { Some(()) } else { None }
}

impl SirenFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let cleaned: String = val.chars().filter(|c| *c != ' ').collect();
        let bytes = cleaned.as_bytes();
        if bytes.len() != 9 || !bytes.iter().all(|b| b.is_ascii_digit()) {
            return None;
        }
        luhn_check(bytes)
    }
}

impl Detector for SirenFormat {
    fn name(&self) -> &'static str { "siren" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.9 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("siren", 1.0), ("n° siren", 1.0), ("siren organisme", 1.0),
            ("siren titulaire", 1.0), ("numero siren", 1.0), ("epci", 0.9),
        ]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
