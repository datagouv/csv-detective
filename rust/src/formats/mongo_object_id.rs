use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    // ^[0-9a-fA-F]{24}$
    let bytes = val.as_bytes();
    if bytes.len() != 24 {
        return None;
    }
    if bytes.iter().all(|b| b.is_ascii_hexdigit()) {
        Some(())
    } else {
        None
    }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
