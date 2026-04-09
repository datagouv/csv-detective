use super::Detector;
use crate::value::Value;

pub struct IdRnbFormat;

const VALID_CHARS: &[u8] = b"123456789ABCDEFGHJKMNPQRSTVWXYZ";

impl IdRnbFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let bytes = val.as_bytes();
        if bytes.len() != 12 {
            return None;
        }
        if bytes.iter().all(|b| VALID_CHARS.contains(b)) { Some(()) } else { None }
    }
}

impl Detector for IdRnbFormat {
    fn name(&self) -> &'static str { "id_rnb" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("rnb", 1.0), ("batid", 1.0)]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
