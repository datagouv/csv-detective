use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    // starts with b' and ends with ', or starts with b" and ends with "
    let bytes = val.as_bytes();
    if bytes.len() < 3 || bytes[0] != b'b' {
        return None;
    }
    let quote = bytes[1];
    if (quote == b'\'' && *bytes.last()? == b'\'')
        || (quote == b'"' && *bytes.last()? == b'"')
    {
        Some(())
    } else {
        None
    }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
