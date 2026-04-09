use crate::value::Value;
use super::geo;

pub fn detect(val: &str) -> Option<()> {
    // same as latlon but lon,lat order
    let inner = if val.starts_with('[') && val.ends_with(']') {
        &val[1..val.len() - 1]
    } else {
        val
    };

    let comma_pos = inner.find(',')?;
    let lon_str = inner[..comma_pos].trim();
    let lat_str = inner[comma_pos + 1..].trim();

    geo::detect_longitude_wgs(lon_str)?;
    geo::detect_latitude_wgs(lat_str)?;

    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
