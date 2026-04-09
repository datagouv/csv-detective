use crate::value::Value;

pub fn luhn_check(digits: &[u8]) -> Option<()> {
    let mut sum = 0u32;
    let mut double = digits.len() % 2 == 0;
    for &b in digits {
        let mut d = (b - b'0') as u32;
        if double {
            d *= 2;
        }
        sum += d / 10 + d % 10;
        double = !double;
    }
    if sum % 10 == 0 { Some(()) } else { None }
}

pub fn detect(val: &str) -> Option<()> {
    let cleaned: String = val.chars().filter(|c| *c != ' ').collect();
    let bytes = cleaned.as_bytes();
    if bytes.len() != 9 || !bytes.iter().all(|b| b.is_ascii_digit()) {
        return None;
    }
    luhn_check(bytes)
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
