use std::collections::HashSet;
use std::sync::LazyLock;

use crate::value::Value;

static PARTIAL_CODES: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/codes_fantoir_partial.txt")
        .lines()
        .map(|l| l.to_string())
        .collect()
});

pub fn detect(val: &str) -> Option<()> {
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

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
