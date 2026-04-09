use super::Detector;

pub struct JsonFormat;

impl JsonFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
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
}

impl Detector for JsonFormat {
    fn name(&self) -> &'static str { "json" }
    fn python_type(&self) -> &'static str { "json" }
    fn proportion(&self) -> f64 { 1.0 }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("list", 1.0), ("dict", 1.0), ("complex", 1.0)]
    }
    fn tags(&self) -> &'static [&'static str] { &["type"] }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
