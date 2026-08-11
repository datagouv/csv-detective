use crate::value::Value;
use super::float;

const CURRENCY_SYMBOLS: &[char] = &['€', '$', '£', '¥'];

pub fn detect(val: &str) -> Option<()> {
    let last = val.chars().last()?;
    if !CURRENCY_SYMBOLS.contains(&last) {
        return None;
    }
    let num_part = &val[..val.len() - last.len_utf8()];
    float::detect(num_part)?;
    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
