use super::Detector;
use crate::value::Value;
use super::siren::luhn_check;

pub struct SiretFormat;

impl SiretFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let cleaned: String = val.chars().filter(|c| *c != ' ').collect();
        let bytes = cleaned.as_bytes();
        if bytes.len() != 14 || !bytes.iter().all(|b| b.is_ascii_digit()) {
            return None;
        }
        // SIREN check (first 9 digits)
        luhn_check(&bytes[..9])?;
        // SIRET check (all 14 digits)
        luhn_check(bytes)?;
        Some(())
    }
}

impl Detector for SiretFormat {
    fn name(&self) -> &'static str { "siret" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.8 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("siret", 1.0), ("num siret", 1.0), ("siretacheteur", 1.0),
            ("n° siret", 1.0), ("coll siret", 1.0), ("epci", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
