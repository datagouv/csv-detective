use crate::value::Value;

const VALID: &[&str] = &["homme", "femme", "h", "f", "m", "masculin", "feminin"];

pub fn detect(val: &str) -> Option<()> {
    let lower = val.to_lowercase();
    // normalize accents for feminin/féminin
    let normalized = lower.replace('é', "e");
    if VALID.contains(&normalized.as_str()) {
        Some(())
    } else {
        None
    }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
