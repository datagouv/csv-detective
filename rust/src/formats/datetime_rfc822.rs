use super::Detector;
use crate::value::Value;

pub struct DatetimeRfc822Format;

const DAYS: &[&str] = &["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const MONTHS: &[&str] = &[
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
];
const NAMED_TZ: &[&str] = &[
    "ut", "gmt", "est", "edt", "cst", "cdt", "mst", "mdt", "pst", "pdt",
];

impl DatetimeRfc822Format {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^(day), DD Mon YYYY HH:MM:SS TZ$
        // early reject if not ASCII (RFC 822 is pure ASCII)
        if !val.is_ascii() {
            return None;
        }
        let lower = val.to_ascii_lowercase();
        let bytes = lower.as_bytes();

        // day, (3 letters + comma + space)
        if bytes.len() < 26 {
            return None;
        }
        let day = &lower[0..3];
        if !DAYS.contains(&day) {
            return None;
        }
        if bytes[3] != b',' || bytes[4] != b' ' {
            return None;
        }

        // DD (with leading zero)
        let dd = parse_2digits(bytes, 5)?;
        if dd == 0 || dd > 31 {
            return None;
        }

        if bytes[7] != b' ' {
            return None;
        }

        // Mon
        let mon = &lower[8..11];
        if !MONTHS.contains(&mon) {
            return None;
        }

        if bytes[11] != b' ' {
            return None;
        }

        // YYYY
        for &b in &bytes[12..16] {
            if !b.is_ascii_digit() {
                return None;
            }
        }

        if bytes[16] != b' ' {
            return None;
        }

        // HH:MM:SS
        let hh = parse_2digits(bytes, 17)?;
        if hh > 23 {
            return None;
        }
        if bytes[19] != b':' {
            return None;
        }
        let mm = parse_2digits(bytes, 20)?;
        if mm > 59 {
            return None;
        }
        if bytes[22] != b':' {
            return None;
        }
        let ss = parse_2digits(bytes, 23)?;
        if ss > 59 {
            return None;
        }

        if bytes[25] != b' ' {
            return None;
        }

        // timezone
        let tz = &lower[26..];
        if NAMED_TZ.contains(&tz) {
            return Some(());
        }

        // +HHMM or -HHMM
        let tz_bytes = tz.as_bytes();
        if tz_bytes.len() != 5 {
            return None;
        }
        if tz_bytes[0] != b'+' && tz_bytes[0] != b'-' {
            return None;
        }
        let tz_hh = parse_2digits(tz_bytes, 1)?;
        if tz_hh > 13 {
            return None;
        }
        // last two must be 00
        if tz_bytes[3] != b'0' || tz_bytes[4] != b'0' {
            return None;
        }

        Some(())
    }
}

fn parse_2digits(bytes: &[u8], pos: usize) -> Option<u32> {
    if pos + 2 > bytes.len() {
        return None;
    }
    let d1 = (bytes[pos] as char).to_digit(10)?;
    let d2 = (bytes[pos + 1] as char).to_digit(10)?;
    Some(d1 * 10 + d2)
}

impl Detector for DatetimeRfc822Format {
    fn name(&self) -> &'static str {
        "datetime_rfc822"
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
