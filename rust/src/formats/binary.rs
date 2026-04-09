use super::Detector;

pub struct BinaryFormat;

impl BinaryFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // starts with b' and ends with ', or starts with b" and ends with "
        let bytes = val.as_bytes();
        if bytes.len() < 3 || bytes[0] != b'b' {
            return None;
        }
        let quote = bytes[1];
        if (quote == b'\'' && *bytes.last()? == b'\'')
            || (quote == b'"' && *bytes.last()? == b'"')
        {
            Some(())
        } else {
            None
        }
    }
}

impl Detector for BinaryFormat {
    fn name(&self) -> &'static str { "binary" }
    fn python_type(&self) -> &'static str { "binary" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["type"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("bytes", 1.0), ("binary", 1.0), ("image", 1.0), ("encode", 1.0), ("content", 1.0)]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
