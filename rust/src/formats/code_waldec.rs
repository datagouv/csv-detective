use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    // ^W\d[\dA-Z]\d{7}$
    let bytes = val.as_bytes();
    if bytes.len() != 10 || bytes[0] != b'W' {
        return None;
    }
    if !bytes[1].is_ascii_digit() {
        return None;
    }
    if !bytes[2].is_ascii_digit() && !bytes[2].is_ascii_uppercase() {
        return None;
    }
    if bytes[3..].iter().all(|b| b.is_ascii_digit()) { Some(()) } else { None }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
