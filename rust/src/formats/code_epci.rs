use crate::value::Value;
use super::siren::luhn_check;

pub fn detect(val: &str) -> Option<()> {
    let cleaned: String = val.chars().filter(|c| *c != ' ').collect();
    let bytes = cleaned.as_bytes();
    if bytes.len() != 9 || !bytes[0] == b'2' {
        return None;
    }
    if !bytes.iter().all(|b| b.is_ascii_digit()) {
        return None;
    }
    if bytes[0] != b'2' {
        return None;
    }
    luhn_check(bytes)
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
