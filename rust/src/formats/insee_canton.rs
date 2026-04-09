use std::collections::HashSet;
use std::sync::LazyLock;

use super::Detector;
use crate::value::Value;

static CANTONS: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/cantons.txt")
        .lines()
        .map(|l| l.to_string())
        .collect()
});

pub struct InseeCantonFormat;

impl Detector for InseeCantonFormat {
    fn name(&self) -> &'static str { "insee_canton" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.9 }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("insee canton", 1.0), ("canton", 1.0), ("cant", 0.5), ("nom canton", 1.0)]
    }
    fn test(&self, val: &Value) -> bool { CANTONS.contains(val.normalized()) }
}
