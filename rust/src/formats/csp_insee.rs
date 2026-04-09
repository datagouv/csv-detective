use std::collections::HashSet;
use std::sync::LazyLock;

use super::Detector;
use crate::detect::process_text;

static CSP_VALUES: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/csp_insee.txt")
        .lines()
        .map(|l| l.trim().to_string())
        .filter(|l| !l.is_empty())
        .collect()
});

pub struct CspInseeFormat;

impl CspInseeFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let processed = process_text(val);
        if CSP_VALUES.contains(&processed) { Some(()) } else { None }
    }
}

impl Detector for CspInseeFormat {
    fn name(&self) -> &'static str { "csp_insee" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("csp insee", 1.0), ("csp", 0.75),
            ("categorie socioprofessionnelle", 1.0), ("sociopro", 1.0),
        ]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
