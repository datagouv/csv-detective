use super::Detector;
use crate::value::Value;
use super::float::FloatFormat;

pub struct PercentFormat;

impl PercentFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        if !val.ends_with('%') {
            return None;
        }
        let num_part = &val[..val.len() - 1];
        FloatFormat.detect(num_part)?;
        Some(())
    }
}

impl Detector for PercentFormat {
    fn name(&self) -> &'static str {
        "percent"
    }
    fn python_type(&self) -> &'static str {
        "string"
    }
    fn proportion(&self) -> f64 {
        0.8
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("pourcent", 1.0), ("part", 0.75), ("pct", 0.75)]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
