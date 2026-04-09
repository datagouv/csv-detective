use super::Detector;

pub struct CodeRnaFormat;

impl CodeRnaFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^W\d{9}$
        let bytes = val.as_bytes();
        if bytes.len() != 10 || bytes[0] != b'W' {
            return None;
        }
        if bytes[1..].iter().all(|b| b.is_ascii_digit()) { Some(()) } else { None }
    }
}

impl Detector for CodeRnaFormat {
    fn name(&self) -> &'static str { "code_rna" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.9 }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("code rna", 1.0), ("rna", 1.0), ("n° inscription association", 1.0),
            ("identifiant association", 1.0), ("asso", 0.75),
        ]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
