use crate::value::Value;

pub fn detect(val: &str) -> Option<bool> {
    match val.to_ascii_lowercase().as_str() {
        "1" | "vrai" | "true" | "oui" | "yes" | "y" | "o" => Some(true),
        "0" | "faux" | "false" | "non" | "no" | "n" => Some(false),
        _ => None,
    }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
