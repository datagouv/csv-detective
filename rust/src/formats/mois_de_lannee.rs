use crate::value::Value;

const VALID: &[&str] = &[
    "janvier", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
    "jan", "fev", "mar", "avr", "jun", "jui", "juil", "aou",
    "sep", "sept", "oct", "nov", "dec",
];

pub fn detect(val: &str) -> Option<()> {
    // normalize unicode + lowercase
    let lower = val.to_lowercase();
    let normalized = normalize_accents(&lower);
    if VALID.contains(&normalized.as_str()) {
        Some(())
    } else {
        None
    }
}

fn normalize_accents(s: &str) -> String {
    s.replace('é', "e")
        .replace('è', "e")
        .replace('ê', "e")
        .replace('û', "u")
        .replace('ù', "u")
        .replace('â', "a")
        .replace('à', "a")
        .replace('î', "i")
        .replace('ô', "o")
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
