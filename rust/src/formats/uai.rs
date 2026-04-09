use super::Detector;
use crate::value::Value;

pub struct UaiFormat;

impl UaiFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^(0[0-8][0-9]|09[0-5]|9[78][0-9]|[67]20)[0-9]{4}[A-Z]$
        let bytes = val.as_bytes();
        if bytes.len() != 8 {
            return None;
        }
        // check prefix (3 digits)
        let prefix = &bytes[0..3];
        if !prefix.iter().all(|b| b.is_ascii_digit() || b.is_ascii_uppercase()) {
            return None;
        }
        let p0 = prefix[0];
        let p1 = prefix[1];
        let p2 = prefix[2];
        let valid_prefix = match p0 {
            b'0' => match p1 {
                b'0'..=b'8' => p2.is_ascii_digit(),
                b'9' => p2 >= b'0' && p2 <= b'5',
                _ => false,
            },
            b'9' => (p1 == b'7' || p1 == b'8') && p2.is_ascii_digit(),
            b'6' | b'7' => p1 == b'2' && p2 == b'0',
            _ => false,
        };
        if !valid_prefix {
            return None;
        }
        // 4 digits
        if !bytes[3..7].iter().all(|b| b.is_ascii_digit()) {
            return None;
        }
        // trailing uppercase letter
        if bytes[7].is_ascii_uppercase() { Some(()) } else { None }
    }
}

impl Detector for UaiFormat {
    fn name(&self) -> &'static str { "uai" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.8 }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("uai", 1.0), ("code etablissement", 1.0), ("code uai", 1.0),
            ("uai   identifiant", 1.0), ("numero uai", 1.0), ("rne", 0.75),
            ("numero de l etablissement", 1.0), ("code rne", 1.0), ("codeetab", 1.0),
            ("code uai de l etablissement", 1.0), ("ref uai", 1.0), ("cd rne", 1.0),
            ("numerouai", 1.0), ("numero d etablissement", 1.0), ("numero etablissement", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
