use std::collections::HashSet;
use std::sync::LazyLock;

use crate::value::Value;

static CANTONS: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/cantons.txt")
        .lines()
        .map(|l| l.to_string())
        .collect()
});

pub fn test(val: &Value) -> bool { CANTONS.contains(val.normalized()) }
