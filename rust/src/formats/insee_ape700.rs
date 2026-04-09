use std::collections::HashSet;
use std::sync::LazyLock;

use super::Detector;

static APE_CODES: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/insee_ape700.txt")
        .lines()
        .map(|l| l.trim().to_uppercase())
        .filter(|l| !l.is_empty())
        .collect()
});

pub struct InseeApe700Format;

impl InseeApe700Format {
    pub fn detect(&self, val: &str) -> Option<()> {
        let upper = val.to_uppercase();
        if APE_CODES.contains(&upper) { Some(()) } else { None }
    }
}

impl Detector for InseeApe700Format {
    fn name(&self) -> &'static str { "insee_ape700" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.8 }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("code ape", 1.0), ("code activite (ape)", 1.0), ("code naf", 1.0),
            ("code naf organisme designe", 1.0), ("code naf organisme designant", 1.0),
            ("base sirene : code ape de l etablissement siege", 1.0),
            ("naf", 0.75), ("ape", 0.5),
        ]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
