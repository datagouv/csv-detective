use super::Detector;
use crate::value::Value;

pub struct DatetimeNaiveFormat;

impl DatetimeNaiveFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let len = val.len();
        if len < 15 || len > 30 {
            return None;
        }
        // security prefix: ^\d{2}[-/:]?\d{2}
        let bytes = val.as_bytes();
        if !bytes[0].is_ascii_digit() || !bytes[1].is_ascii_digit() {
            return None;
        }
        let mut i = 2;
        if i < bytes.len() && (bytes[i] == b'-' || bytes[i] == b'/' || bytes[i] == b':') {
            i += 1;
        }
        if i + 1 >= bytes.len() || !bytes[i].is_ascii_digit() || !bytes[i + 1].is_ascii_digit() {
            return None;
        }

        // pattern: YYYY-MM-DD[T ]HH:MM:SS(.ffffff) without timezone
        try_datetime_naive_pattern(val)
    }
}

fn try_datetime_naive_pattern(val: &str) -> Option<()> {
    let bytes = val.as_bytes();

    // YYYY
    if bytes.len() < 19 {
        return None;
    }
    for &b in &bytes[0..4] {
        if !b.is_ascii_digit() {
            return None;
        }
    }

    // separator between date parts
    let date_sep = bytes[4];
    if date_sep != b'-' && date_sep != b'/' {
        return None;
    }

    // MM
    if !bytes[5].is_ascii_digit() || !bytes[6].is_ascii_digit() {
        return None;
    }

    if bytes[7] != date_sep {
        return None;
    }

    // DD
    if !bytes[8].is_ascii_digit() || !bytes[9].is_ascii_digit() {
        return None;
    }

    // T or space
    if bytes[10] != b'T' && bytes[10] != b' ' {
        return None;
    }

    // HH:MM:SS
    if !bytes[11].is_ascii_digit()
        || !bytes[12].is_ascii_digit()
        || bytes[13] != b':'
        || !bytes[14].is_ascii_digit()
        || !bytes[15].is_ascii_digit()
        || bytes[16] != b':'
        || !bytes[17].is_ascii_digit()
        || !bytes[18].is_ascii_digit()
    {
        return None;
    }

    let mut i = 19;

    // optional fractional seconds
    if i < bytes.len() && bytes[i] == b'.' {
        i += 1;
        if i >= bytes.len() || !bytes[i].is_ascii_digit() {
            return None;
        }
        while i < bytes.len() && bytes[i].is_ascii_digit() {
            i += 1;
        }
    }

    // must end here (no timezone)
    if i != bytes.len() {
        return None;
    }

    Some(())
}

impl Detector for DatetimeNaiveFormat {
    fn name(&self) -> &'static str {
        "datetime_naive"
    }
    fn python_type(&self) -> &'static str {
        "datetime"
    }
    fn proportion(&self) -> f64 {
        1.0
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("date", 1.0),
            ("mise a jour", 1.0),
            ("modifie", 1.0),
            ("maj", 0.75),
            ("datemaj", 1.0),
            ("update", 1.0),
            ("created", 1.0),
            ("modified", 1.0),
            ("datetime", 1.0),
            ("timestamp", 1.0),
        ]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["temp", "type"]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
