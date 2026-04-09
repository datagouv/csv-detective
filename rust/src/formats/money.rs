use super::Detector;
use crate::value::Value;
use super::float::FloatFormat;

pub struct MoneyFormat;

const CURRENCY_SYMBOLS: &[char] = &['€', '$', '£', '¥'];

impl MoneyFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let last = val.chars().last()?;
        if !CURRENCY_SYMBOLS.contains(&last) {
            return None;
        }
        let num_part = &val[..val.len() - last.len_utf8()];
        FloatFormat.detect(num_part)?;
        Some(())
    }
}

impl Detector for MoneyFormat {
    fn name(&self) -> &'static str {
        "money"
    }
    fn python_type(&self) -> &'static str {
        "string"
    }
    fn proportion(&self) -> f64 {
        0.8
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("budget", 1.0),
            ("salaire", 1.0),
            ("euro", 1.0),
            ("euros", 1.0),
            ("pret", 1.0),
            ("montant", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
