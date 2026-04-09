use std::collections::HashSet;
use std::sync::LazyLock;

use super::Detector;
use super::fr_geo::normalize;

static PAYS: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/pays.txt")
        .lines()
        .map(|l| l.to_string())
        .collect()
});

pub struct PaysFormat;

impl PaysFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let n = normalize(val);
        if PAYS.contains(&n) { Some(()) } else { None }
    }
}

impl Detector for PaysFormat {
    fn name(&self) -> &'static str { "pays" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.6 }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("pays", 1.0), ("payslieu", 1.0), ("paysorg", 1.0), ("country", 1.0),
            ("pays lib", 1.0), ("lieupays", 1.0), ("pays beneficiaire", 1.0),
            ("nom du pays", 1.0), ("libelle pays", 1.0),
        ]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
