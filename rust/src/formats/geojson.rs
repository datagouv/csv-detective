use super::Detector;

pub struct GeoJsonFormat;

impl GeoJsonFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
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
}

impl Detector for GeoJsonFormat {
    fn name(&self) -> &'static str { "geojson" }
    fn python_type(&self) -> &'static str { "json" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("json geojson", 1.0), ("json", 1.0), ("geojson", 1.0),
            ("geo shape", 1.0), ("geom", 0.75), ("geometry", 1.0), ("geoshape", 1.0),
        ]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
