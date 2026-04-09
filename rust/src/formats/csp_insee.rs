use std::collections::HashSet;
use std::sync::LazyLock;

use crate::detect::process_text;
use crate::value::Value;

static CSP_VALUES: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/csp_insee.txt")
        .lines()
        .map(|l| l.trim().to_string())
        .filter(|l| !l.is_empty())
        .collect()
});

pub fn detect(val: &str) -> Option<()> {
    let processed = process_text(val);
    if CSP_VALUES.contains(&processed) { Some(()) } else { None }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
