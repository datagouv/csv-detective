use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    // ^@[A-Za-z0-9_]+$
    let bytes = val.as_bytes();
    if bytes.len() < 2 || bytes[0] != b'@' {
        return None;
    }
    for &b in &bytes[1..] {
        if !b.is_ascii_alphanumeric() && b != b'_' {
            return None;
        }
    }
    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
