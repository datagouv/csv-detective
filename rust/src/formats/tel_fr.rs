use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    if val.len() < 10 {
        return None;
    }
    // strip dots, dashes, spaces
    let cleaned: String = val
        .chars()
        .filter(|c| *c != '.' && *c != '-' && *c != ' ')
        .collect();
    // ^(0|\+33|0033)?[0-9]{9}$
    let bytes = cleaned.as_bytes();
    let start = if cleaned.starts_with("+33") {
        3
    } else if cleaned.starts_with("0033") {
        4
    } else if bytes.first() == Some(&b'0') {
        1
    } else {
        return None;
    };
    let rest = &bytes[start..];
    if rest.len() != 9 {
        return None;
    }
    if rest.iter().all(|b| b.is_ascii_digit()) {
        Some(())
    } else {
        None
    }
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
