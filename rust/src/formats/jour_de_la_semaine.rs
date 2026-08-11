use crate::value::Value;

const VALID: &[&str] = &[
    "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche",
    "lun", "mar", "mer", "jeu", "ven", "sam", "dim",
];

pub fn detect(val: &str) -> Option<()> {
    let lower = val.to_lowercase();
    if VALID.contains(&lower.as_str()) {
        Some(())
    } else {
        None
    }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
