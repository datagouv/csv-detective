use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    if val.is_empty() || val.len() >= 20 {
        return None;
    }
    if val.contains('.') || val.contains('_') || val.contains('+') {
        return None;
    }
    // reject leading zeros (except "0" itself)
    if val.len() > 1 && val.starts_with('0') {
        return None;
    }
    if val.len() > 1 && val.starts_with("-0") {
        return None;
    }
    val.parse::<i64>().ok()?;
    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
