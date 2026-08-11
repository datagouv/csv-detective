use crate::value::Value;
use super::geo;

pub fn detect(val: &str) -> Option<()> {
    // optional brackets
    let inner = if val.starts_with('[') && val.ends_with(']') {
        &val[1..val.len() - 1]
    } else {
        val
    };

    // split on comma — must have exactly one comma
    let comma_pos = inner.find(',')?;
    let lat_str = inner[..comma_pos].trim();
    let lon_str = inner[comma_pos + 1..].trim();

    // both must be valid floats (not integers)
    geo::detect_latitude_wgs(lat_str)?;
    geo::detect_longitude_wgs(lon_str)?;

    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
