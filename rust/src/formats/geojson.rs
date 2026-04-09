use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    let trimmed = val.trim();
    if !trimmed.starts_with('{') {
        return None;
    }
    let obj: serde_json::Value = serde_json::from_str(trimmed).ok()?;
    let map = obj.as_object()?;
    // either has type+coordinates, or geometry.coordinates
    if map.contains_key("type") && map.contains_key("coordinates") {
        return Some(());
    }
    if let Some(geom) = map.get("geometry") {
        if let Some(g) = geom.as_object() {
            if g.contains_key("coordinates") {
                return Some(());
            }
        }
    }
    None
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
