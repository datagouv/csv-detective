use super::Detector;

pub struct CodeWaldecFormat;

impl CodeWaldecFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^W\d[\dA-Z]\d{7}$
        let bytes = val.as_bytes();
        if bytes.len() != 10 || bytes[0] != b'W' {
            return None;
        }
        if !bytes[1].is_ascii_digit() {
            return None;
        }
        if !bytes[2].is_ascii_digit() && !bytes[2].is_ascii_uppercase() {
            return None;
        }
        if bytes[3..].iter().all(|b| b.is_ascii_digit()) { Some(()) } else { None }
    }
}

impl Detector for CodeWaldecFormat {
    fn name(&self) -> &'static str { "code_waldec" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.9 }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("code waldec", 1.0), ("waldec", 1.0)]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
