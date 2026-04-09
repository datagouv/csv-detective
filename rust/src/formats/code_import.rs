use super::Detector;
use crate::value::Value;

pub struct CodeImportFormat;

impl CodeImportFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // ^(\d{3}[SP]\d{4,10}(.\w{1,3}\d{0,5})?|\d[A-Z0-9]\d[SP]\w(\w-?\w{0,2}\d{0,6})?)$
        let bytes = val.as_bytes();
        if bytes.is_empty() {
            return None;
        }
        try_pattern1(bytes).or_else(|| try_pattern2(bytes))
    }
}

// \d{3}[SP]\d{4,10}(.\w{1,3}\d{0,5})?
fn try_pattern1(bytes: &[u8]) -> Option<()> {
    if bytes.len() < 8 {
        return None;
    }
    if !bytes[0..3].iter().all(|b| b.is_ascii_digit()) {
        return None;
    }
    if bytes[3] != b'S' && bytes[3] != b'P' {
        return None;
    }
    let mut i = 4;
    let digit_start = i;
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    let digit_count = i - digit_start;
    if digit_count < 4 || digit_count > 10 {
        return None;
    }
    if i == bytes.len() {
        return Some(());
    }
    // optional: .\w{1,3}\d{0,5}
    i += 1; // any char as separator
    if i >= bytes.len() {
        return None;
    }
    let word_start = i;
    while i < bytes.len() && (bytes[i].is_ascii_alphanumeric() || bytes[i] == b'_') {
        i += 1;
    }
    let word_count = i - word_start;
    if word_count < 1 || word_count > 3 {
        return None;
    }
    let digit_start2 = i;
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    if i - digit_start2 > 5 {
        return None;
    }
    if i == bytes.len() { Some(()) } else { None }
}

// \d[A-Z0-9]\d[SP]\w(\w-?\w{0,2}\d{0,6})?
fn try_pattern2(bytes: &[u8]) -> Option<()> {
    if bytes.len() < 5 {
        return None;
    }
    if !bytes[0].is_ascii_digit() {
        return None;
    }
    if !bytes[1].is_ascii_uppercase() && !bytes[1].is_ascii_digit() {
        return None;
    }
    if !bytes[2].is_ascii_digit() {
        return None;
    }
    if bytes[3] != b'S' && bytes[3] != b'P' {
        return None;
    }
    if !(bytes[4].is_ascii_alphanumeric() || bytes[4] == b'_') {
        return None;
    }
    if bytes.len() == 5 {
        return Some(());
    }
    // (\w-?\w{0,2}\d{0,6})?
    let mut i = 5;
    if i < bytes.len() && (bytes[i].is_ascii_alphanumeric() || bytes[i] == b'_') {
        i += 1;
    }
    if i < bytes.len() && bytes[i] == b'-' {
        i += 1;
    }
    let word_start = i;
    while i < bytes.len() && (bytes[i].is_ascii_alphanumeric() || bytes[i] == b'_') && i - word_start < 2 {
        i += 1;
    }
    let digit_start = i;
    while i < bytes.len() && bytes[i].is_ascii_digit() && i - digit_start < 6 {
        i += 1;
    }
    if i == bytes.len() { Some(()) } else { None }
}

impl Detector for CodeImportFormat {
    fn name(&self) -> &'static str { "code_import" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.9 }
    fn tags(&self) -> &'static [&'static str] { &["fr"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("code", 0.5)]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
