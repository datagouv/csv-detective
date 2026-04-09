use super::Detector;
use crate::value::Value;

pub struct UsernameFormat;

impl UsernameFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^@[A-Za-z0-9_]+$
        let bytes = val.as_bytes();
        if bytes.len() < 2 || bytes[0] != b'@' {
            return None;
        }
        for &b in &bytes[1..] {
            if !b.is_ascii_alphanumeric() && b != b'_' {
                return None;
            }
        }
        Some(())
    }
}

impl Detector for UsernameFormat {
    fn name(&self) -> &'static str {
        "username"
    }
    fn python_type(&self) -> &'static str {
        "string"
    }
    fn proportion(&self) -> f64 {
        1.0
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("account", 1.0), ("username", 1.0), ("user", 0.75)]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
