use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    // ^W\d{9}$
    let bytes = val.as_bytes();
    if bytes.len() != 10 || bytes[0] != b'W' {
        return None;
    }
    if bytes[1..].iter().all(|b| b.is_ascii_digit()) { Some(()) } else { None }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
