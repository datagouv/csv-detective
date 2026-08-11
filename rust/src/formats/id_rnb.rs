use crate::value::Value;

const VALID_CHARS: &[u8] = b"123456789ABCDEFGHJKMNPQRSTVWXYZ";

pub fn detect(val: &str) -> Option<()> {
    let bytes = val.as_bytes();
    if bytes.len() != 12 {
        return None;
    }
    if bytes.iter().all(|b| VALID_CHARS.contains(b)) { Some(()) } else { None }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
