use std::collections::HashSet;
use std::sync::LazyLock;

use super::Detector;
use crate::value::Value;

static PARTIAL_CODES: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/codes_fantoir_partial.txt")
        .lines()
        .map(|l| l.to_string())
        .collect()
});

pub struct CodeFantoirFormat;

impl CodeFantoirFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let bytes = val.as_bytes();
        if bytes.len() != 5 {
            return None;
        }
        if !bytes[4].is_ascii_uppercase() {
            return None;
        }
        let prefix = &val[..4];
        if PARTIAL_CODES.contains(prefix) { Some(()) } else { None }
    }
}

impl Detector for CodeFantoirFormat {
    fn name(&self) -> &'static str { "code_fantoir" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("cadastre1", 1.0), ("code fantoir", 1.0), ("fantoir", 1.0)]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
