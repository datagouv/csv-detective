use crate::value::Value;
use super::float;

pub fn detect(val: &str) -> Option<()> {
    if !val.ends_with('%') {
        return None;
    }
    let num_part = &val[..val.len() - 1];
    float::detect(num_part)?;
    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
