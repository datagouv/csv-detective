use super::Detector;

pub struct UuidFormat;

impl UuidFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^[{]?[0-9a-fA-F]{8}-?([0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}[}]?$
        let bytes = val.as_bytes();
        let mut i = 0;

        // optional opening brace
        let has_brace = i < bytes.len() && bytes[i] == b'{';
        if has_brace {
            i += 1;
        }

        // 8 hex digits
        i = consume_hex(bytes, i, 8)?;

        // optional dash
        let has_dash = i < bytes.len() && bytes[i] == b'-';
        if has_dash {
            i += 1;
        }

        // 3 groups of 4 hex digits with optional dashes
        for _ in 0..3 {
            i = consume_hex(bytes, i, 4)?;
            if has_dash {
                if i >= bytes.len() || bytes[i] != b'-' {
                    return None;
                }
                i += 1;
            }
        }

        // 12 hex digits
        i = consume_hex(bytes, i, 12)?;

        // optional closing brace
        if has_brace {
            if i >= bytes.len() || bytes[i] != b'}' {
                return None;
            }
            i += 1;
        }

        if i == bytes.len() { Some(()) } else { None }
    }
}

fn consume_hex(bytes: &[u8], start: usize, count: usize) -> Option<usize> {
    if start + count > bytes.len() {
        return None;
    }
    for &b in &bytes[start..start + count] {
        if !b.is_ascii_hexdigit() {
            return None;
        }
    }
    Some(start + count)
}

impl Detector for UuidFormat {
    fn name(&self) -> &'static str {
        "uuid"
    }
    fn python_type(&self) -> &'static str {
        "string"
    }
    fn proportion(&self) -> f64 {
        0.8
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("id", 1.0), ("identifiant", 1.0)]
    }
    fn test(&self, val: &str) -> bool {
        self.detect(val).is_some()
    }
}
