use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    // must parse as JSON and be a list or dict (not a scalar)
    let trimmed = val.trim();
    if trimmed.is_empty() {
        return None;
    }
    let first = trimmed.as_bytes()[0];
    if first != b'{' && first != b'[' {
        return None;
    }
    // validate it's parseable JSON
    serde_json::from_str::<serde_json::Value>(trimmed)
        .ok()
        .and_then(|v| {
            if v.is_array() || v.is_object() {
                Some(())
            } else {
                None
            }
        })
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
