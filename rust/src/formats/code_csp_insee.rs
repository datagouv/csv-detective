use crate::value::Value;

const SPECIAL_CODES: &[&str] = &[
    "7100", "7200", "7400", "7500", "7700", "7800", "8100", "8300", "8400", "8500", "8600",
];

pub fn detect(val: &str) -> Option<()> {
    if val.len() != 4 {
        return None;
    }
    if SPECIAL_CODES.contains(&val) {
        return Some(());
    }
    // ^[123456][0-9]{2}[abcdefghijkl]$
    let bytes = val.as_bytes();
    if !matches!(bytes[0], b'1'..=b'6') {
        return None;
    }
    if !bytes[1].is_ascii_digit() || !bytes[2].is_ascii_digit() {
        return None;
    }
    if matches!(bytes[3], b'a'..=b'l') { Some(()) } else { None }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
