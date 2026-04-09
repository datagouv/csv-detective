use super::Detector;

pub struct FloatFormat;

impl FloatFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        if val.is_empty() || val.len() >= 20 {
            return None;
        }
        if val.contains('_') {
            return None;
        }
        // reject leading zero followed by something other than . or ,
        if val.len() > 1 && val.starts_with('0') {
            let second = val.as_bytes().get(1)?;
            if *second != b'.' && *second != b',' {
                return None;
            }
        }
        if val.len() > 2 && val.starts_with("-0") {
            let third = val.as_bytes().get(2)?;
            if *third != b'.' && *third != b',' {
                return None;
            }
        }
        // reject + sign
        if val.contains('+') || val.contains('e') || val.contains('E') {
            // only accept scientific notation matching ^-?\d+\.\d+[eE][+-]?\d+$
            return detect_scientific(val);
        }
        // try parsing with comma as decimal separator
        let normalized = val.replace(',', ".");
        let f = normalized.parse::<f64>().ok()?;
        if f.is_nan() || f.is_infinite() {
            // Python accepts inf/nan but let's match behavior
            return Some(());
        }
        Some(())
    }
}

fn detect_scientific(val: &str) -> Option<()> {
    // pattern: ^-?\d+\.\d+[eE][+-]?\d+$
    let bytes = val.as_bytes();
    let mut i = 0;
    if i < bytes.len() && bytes[i] == b'-' {
        i += 1;
    }
    if i >= bytes.len() || !bytes[i].is_ascii_digit() {
        return None;
    }
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    if i >= bytes.len() || bytes[i] != b'.' {
        return None;
    }
    i += 1;
    if i >= bytes.len() || !bytes[i].is_ascii_digit() {
        return None;
    }
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    if i >= bytes.len() || (bytes[i] != b'e' && bytes[i] != b'E') {
        return None;
    }
    i += 1;
    if i < bytes.len() && (bytes[i] == b'+' || bytes[i] == b'-') {
        i += 1;
    }
    if i >= bytes.len() || !bytes[i].is_ascii_digit() {
        return None;
    }
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    if i == bytes.len() { Some(()) } else { None }
}

impl Detector for FloatFormat {
    fn name(&self) -> &'static str {
        "float"
    }
    fn python_type(&self) -> &'static str {
        "float"
    }
    fn proportion(&self) -> f64 {
        1.0
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("part", 1.0), ("ratio", 1.0), ("taux", 1.0)]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["type"]
    }
    fn test(&self, val: &str) -> bool {
        self.detect(val).is_some()
    }
}
