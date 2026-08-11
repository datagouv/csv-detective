use std::collections::HashSet;
use std::sync::LazyLock;

use crate::value::Value;

static PAYS: LazyLock<HashSet<String>> = LazyLock::new(|| {
    include_str!("../../data/pays.txt")
        .lines()
        .map(|l| l.to_string())
        .collect()
});

pub fn test(val: &Value) -> bool { PAYS.contains(val.normalized()) }
