use super::Detector;

pub struct MongoObjectIdFormat;

impl MongoObjectIdFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^[0-9a-fA-F]{24}$
        let bytes = val.as_bytes();
        if bytes.len() != 24 {
            return None;
        }
        if bytes.iter().all(|b| b.is_ascii_hexdigit()) {
            Some(())
        } else {
            None
        }
    }
}

impl Detector for MongoObjectIdFormat {
    fn name(&self) -> &'static str { "mongo_object_id" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.8 }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("id", 1.0), ("objectid", 1.0)]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
