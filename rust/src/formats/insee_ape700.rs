use std::collections::HashSet;
use std::sync::LazyLock;

use crate::value::Value;

static APE_CODES: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/insee_ape700.txt")
        .lines()
        .map(|l| l.trim().to_uppercase())
        .filter(|l| !l.is_empty())
        .collect()
});

pub fn detect(val: &str) -> Option<()> {
    let upper = val.to_uppercase();
    if APE_CODES.contains(&upper) { Some(()) } else { None }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
