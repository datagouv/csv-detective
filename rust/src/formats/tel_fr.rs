use super::Detector;
use crate::value::Value;

pub struct TelFrFormat;

impl TelFrFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        if val.len() < 10 {
            return None;
        }
        // strip dots, dashes, spaces
        let cleaned: String = val
            .chars()
            .filter(|c| *c != '.' && *c != '-' && *c != ' ')
            .collect();
        // ^(0|\+33|0033)?[0-9]{9}$
        let bytes = cleaned.as_bytes();
        let start = if cleaned.starts_with("+33") {
            3
        } else if cleaned.starts_with("0033") {
            4
        } else if bytes.first() == Some(&b'0') {
            1
        } else {
            return None;
        };
        let rest = &bytes[start..];
        if rest.len() != 9 {
            return None;
        }
        if rest.iter().all(|b| b.is_ascii_digit()) {
            Some(())
        } else {
            None
        }
    }
}

impl Detector for TelFrFormat {
    fn name(&self) -> &'static str {
        "tel_fr"
    }
    fn python_type(&self) -> &'static str {
        "string"
    }
    fn proportion(&self) -> f64 {
        0.7
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("telephone", 1.0),
            ("tel", 1.0),
            ("phone", 1.0),
            ("num tel", 1.0),
            ("tel mob", 1.0),
        ]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["fr"]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
