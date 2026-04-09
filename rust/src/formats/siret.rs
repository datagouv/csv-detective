use crate::value::Value;
use super::siren::luhn_check;

pub fn detect(val: &str) -> Option<()> {
    let cleaned: String = val.chars().filter(|c| *c != ' ').collect();
    let bytes = cleaned.as_bytes();
    if bytes.len() != 14 || !bytes.iter().all(|b| b.is_ascii_digit()) {
        return None;
    }
    // SIREN check (first 9 digits)
    luhn_check(&bytes[..9])?;
    // SIRET check (all 14 digits)
    luhn_check(bytes)?;
    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
