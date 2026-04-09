use super::Detector;

pub struct BoolFormat;

impl BoolFormat {
    pub fn detect(&self, val: &str) -> Option<bool> {
        match val.to_ascii_lowercase().as_str() {
            "1" | "vrai" | "true" | "oui" | "yes" | "y" | "o" => Some(true),
            "0" | "faux" | "false" | "non" | "no" | "n" => Some(false),
            _ => None,
        }
    }
}

impl Detector for BoolFormat {
    fn name(&self) -> &'static str {
        "booleen"
    }
    fn python_type(&self) -> &'static str {
        "bool"
    }
    fn proportion(&self) -> f64 {
        1.0
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("is ", 1.0), ("has ", 1.0), ("est ", 1.0)]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["type"]
    }
    fn test(&self, val: &str) -> bool {
        self.detect(val).is_some()
    }
}
