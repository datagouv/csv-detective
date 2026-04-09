use super::Detector;
use crate::value::Value;

pub struct IntFormat;

impl IntFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        if val.is_empty() || val.len() >= 20 {
            return None;
        }
        if val.contains('.') || val.contains('_') || val.contains('+') {
            return None;
        }
        // reject leading zeros (except "0" itself)
        if val.len() > 1 && val.starts_with('0') {
            return None;
        }
        if val.len() > 1 && val.starts_with("-0") {
            return None;
        }
        val.parse::<i64>().ok()?;
        Some(())
    }
}

impl Detector for IntFormat {
    fn name(&self) -> &'static str {
        "int"
    }
    fn python_type(&self) -> &'static str {
        "int"
    }
    fn proportion(&self) -> f64 {
        1.0
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("nb", 0.75), ("nombre", 1.0), ("nbre", 0.75)]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
