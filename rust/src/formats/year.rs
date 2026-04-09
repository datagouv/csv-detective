use super::Detector;
use crate::value::Value;

pub struct YearFormat;

impl YearFormat {
    pub fn detect(&self, val: &str) -> Option<u16> {
        let n: u16 = val.parse().ok()?;
        if (1800..=2100).contains(&n) {
            Some(n)
        } else {
            None
        }
    }
}

impl Detector for YearFormat {
    fn name(&self) -> &'static str {
        "year"
    }
    fn python_type(&self) -> &'static str {
        "int"
    }
    fn proportion(&self) -> f64 {
        1.0
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("year", 1.0),
            ("annee", 1.0),
            ("naissance", 1.0),
            ("exercice", 1.0),
        ]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["temp"]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
