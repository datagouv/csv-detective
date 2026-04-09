use super::Detector;

pub struct SexeFormat;

const VALID: &[&str] = &["homme", "femme", "h", "f", "m", "masculin", "feminin"];

impl SexeFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let lower = val.to_lowercase();
        // normalize accents for feminin/féminin
        let normalized = lower.replace('é', "e");
        if VALID.contains(&normalized.as_str()) {
            Some(())
        } else {
            None
        }
    }
}

impl Detector for SexeFormat {
    fn name(&self) -> &'static str {
        "sexe"
    }
    fn python_type(&self) -> &'static str {
        "string"
    }
    fn proportion(&self) -> f64 {
        1.0
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("sexe", 1.0), ("sex", 1.0), ("civilite", 1.0), ("genre", 1.0)]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["fr"]
    }
    fn test(&self, val: &str) -> bool {
        self.detect(val).is_some()
    }
}
