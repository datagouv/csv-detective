use super::Detector;
use crate::value::Value;

pub struct DateFormat;

const DATE_SEPS: &[u8] = b" /-*_|;.,";

const TEXT_MONTHS: &[&str] = &[
    "jan", "fev", "feb", "mar", "avr", "apr", "mai", "may", "jun", "jui", "jul", "aou", "aug",
    "sep", "oct", "nov", "dec", "janvier", "fevrier", "mars", "avril", "juin", "juillet", "aout",
    "septembre", "octobre", "novembre", "decembre",
];

pub enum DatePattern {
    DmyWithSep,
    YmdWithSep,
    YmdNoSep,
    TextMonth,
}

impl DateFormat {
    pub fn detect(&self, val: &str) -> Option<DatePattern> {
        let len = val.len();
        if len < 8 || len > 20 {
            return None;
        }
        // exclude floats: ^-?\d+[.|,]\d+$
        if is_float_like(val) {
            return None;
        }

        let lower = val.to_ascii_lowercase();

        if let Some(p) = try_ymd(&lower) {
            return Some(p);
        }
        if let Some(p) = try_dmy(&lower) {
            return Some(p);
        }
        if let Some(p) = try_text_month(&lower) {
            return Some(p);
        }

        None
    }
}

fn is_float_like(val: &str) -> bool {
    let bytes = val.as_bytes();
    let mut i = 0;
    if i < bytes.len() && bytes[i] == b'-' {
        i += 1;
    }
    if i >= bytes.len() || !bytes[i].is_ascii_digit() {
        return false;
    }
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    if i >= bytes.len() {
        return false;
    }
    if bytes[i] != b'.' && bytes[i] != b',' {
        return false;
    }
    i += 1;
    if i >= bytes.len() || !bytes[i].is_ascii_digit() {
        return false;
    }
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    i == bytes.len()
}

fn is_sep(b: u8) -> bool {
    DATE_SEPS.contains(&b)
}

fn parse_2digits(bytes: &[u8], pos: usize) -> Option<u32> {
    if pos + 2 > bytes.len() {
        return None;
    }
    let d1 = (bytes[pos] as char).to_digit(10)?;
    let d2 = (bytes[pos + 1] as char).to_digit(10)?;
    Some(d1 * 10 + d2)
}

fn valid_day(d: u32) -> bool {
    (1..=31).contains(&d)
}

fn valid_month(m: u32) -> bool {
    (1..=12).contains(&m)
}

fn valid_year_4(bytes: &[u8], pos: usize) -> bool {
    if pos + 4 > bytes.len() {
        return false;
    }
    let prefix = &bytes[pos..pos + 2];
    (prefix == b"19" || prefix == b"20")
        && bytes[pos + 2].is_ascii_digit()
        && bytes[pos + 3].is_ascii_digit()
}

// AAAA-MM-JJ with optional separator (accepts 20030502)
fn try_ymd(val: &str) -> Option<DatePattern> {
    let bytes = val.as_bytes();
    if bytes.len() < 8 {
        return None;
    }
    if !valid_year_4(bytes, 0) {
        return None;
    }
    let mut i = 4;

    let has_sep = i < bytes.len() && is_sep(bytes[i]);
    if has_sep {
        i += 1;
    }

    let month = parse_2digits(bytes, i)?;
    if !valid_month(month) {
        return None;
    }
    i += 2;

    if has_sep {
        if i >= bytes.len() || !is_sep(bytes[i]) {
            return None;
        }
        i += 1;
    }

    let day = parse_2digits(bytes, i)?;
    if !valid_day(day) {
        return None;
    }
    i += 2;

    if i != bytes.len() {
        return None;
    }

    if has_sep {
        Some(DatePattern::YmdWithSep)
    } else {
        Some(DatePattern::YmdNoSep)
    }
}

// JJ-MM-AAAA with mandatory separator
fn try_dmy(val: &str) -> Option<DatePattern> {
    let bytes = val.as_bytes();
    if bytes.len() != 10 {
        return None;
    }

    let day = parse_2digits(bytes, 0)?;
    if !valid_day(day) {
        return None;
    }

    if !is_sep(bytes[2]) {
        return None;
    }

    let month = parse_2digits(bytes, 3)?;
    if !valid_month(month) {
        return None;
    }

    if !is_sep(bytes[5]) {
        return None;
    }

    if !valid_year_4(bytes, 6) {
        return None;
    }

    Some(DatePattern::DmyWithSep)
}

// JJ month_text YYYY
fn try_text_month(val: &str) -> Option<DatePattern> {
    // find where the month text starts
    let bytes = val.as_bytes();

    // day: 1-2 digits at start
    let mut i = 0;
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    if i == 0 || i > 2 {
        return None;
    }

    // optional separator
    if i < bytes.len() && is_sep(bytes[i]) {
        i += 1;
    }

    // month text
    let month_start = i;
    while i < bytes.len() && bytes[i].is_ascii_alphabetic() {
        i += 1;
    }
    let month_text = &val[month_start..i];
    if !TEXT_MONTHS.contains(&month_text) {
        return None;
    }

    // optional separator
    if i < bytes.len() && is_sep(bytes[i]) {
        i += 1;
    }

    // year: 2 or 4 digits
    let year_start = i;
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    let year_len = i - year_start;
    if year_len != 2 && year_len != 4 {
        return None;
    }
    if year_len == 4 && !valid_year_4(bytes, year_start) {
        return None;
    }

    if i != bytes.len() {
        return None;
    }

    Some(DatePattern::TextMonth)
}

impl Detector for DateFormat {
    fn name(&self) -> &'static str {
        "date"
    }
    fn python_type(&self) -> &'static str {
        "date"
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
            ("jour", 0.75),
            ("periode", 0.75),
            ("dpc", 0.5),
            ("yyyymmdd", 1.0),
            ("aaaammjj", 1.0),
        ]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["temp", "type"]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
