use crate::value::Value;

pub fn detect(val: &str) -> Option<u16> {
    let n: u16 = val.parse().ok()?;
    if (1800..=2100).contains(&n) {
        Some(n)
    } else {
        None
    }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
