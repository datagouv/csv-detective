use super::Detector;
use crate::value::Value;

fn parse_float_not_int(val: &str) -> Option<f64> {
    if val.is_empty() {
        return None;
    }
    // must not be a pure integer
    if !val.contains('.') && !val.contains(',') {
        return None;
    }
    let normalized = val.replace(',', ".");
    normalized.parse::<f64>().ok()
}

// --- Latitude WGS84 ---

pub struct LatitudeWgsFormat;

impl LatitudeWgsFormat {
    pub fn detect(&self, val: &str) -> Option<f64> {
        let f = parse_float_not_int(val)?;
        if (-90.0..=90.0).contains(&f) { Some(f) } else { None }
    }
}

impl Detector for LatitudeWgsFormat {
    fn name(&self) -> &'static str { "latitude_wgs" }
    fn python_type(&self) -> &'static str { "float" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("latitude", 1.0), ("lat", 0.75), ("y", 0.5), ("yf", 0.5), ("yd", 0.5),
            ("coordonnee y", 1.0), ("coord y", 1.0), ("ycoord", 1.0), ("ylat", 1.0),
            ("y gps", 1.0), ("latitude wgs84", 1.0), ("y wgs84", 1.0), ("wsg", 0.75),
            ("gps", 0.5),
        ]
    }
    fn test(&self, val: &Value) -> bool {
        let raw = val.raw();
        if !raw.contains('.') && !raw.contains(',') { return false; }
        match val.as_float() {
            Some(f) => (-90.0..=90.0).contains(&f),
            None => false,
        }
    }
}

// --- Longitude WGS84 ---

pub struct LongitudeWgsFormat;

impl LongitudeWgsFormat {
    pub fn detect(&self, val: &str) -> Option<f64> {
        let f = parse_float_not_int(val)?;
        if (-180.0..=180.0).contains(&f) { Some(f) } else { None }
    }
}

impl Detector for LongitudeWgsFormat {
    fn name(&self) -> &'static str { "longitude_wgs" }
    fn python_type(&self) -> &'static str { "float" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("longitude", 1.0), ("long", 0.75), ("lon", 0.75), ("lng", 0.5),
            ("x", 0.5), ("xf", 0.5), ("xd", 0.5), ("coordonnee x", 1.0), ("coord x", 1.0),
            ("xcoord", 1.0), ("xlon", 1.0), ("xlong", 1.0), ("x gps", 1.0),
            ("longitude wgs84", 1.0), ("x wgs84", 1.0), ("wsg", 0.75), ("gps", 0.5),
        ]
    }
    fn test(&self, val: &Value) -> bool {
        let raw = val.raw();
        if !raw.contains('.') && !raw.contains(',') { return false; }
        match val.as_float() {
            Some(f) => (-180.0..=180.0).contains(&f),
            None => false,
        }
    }
}

// --- Latitude WGS84 France métropolitaine ---

pub struct LatitudeWgsFrFormat;

impl LatitudeWgsFrFormat {
    pub fn detect(&self, val: &str) -> Option<f64> {
        let f = LatitudeWgsFormat.detect(val)?;
        if (41.3..=51.3).contains(&f) { Some(f) } else { None }
    }
}

impl Detector for LatitudeWgsFrFormat {
    fn name(&self) -> &'static str { "latitude_wgs_fr_metropole" }
    fn python_type(&self) -> &'static str { "float" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        LatitudeWgsFormat.labels()
    }
    fn test(&self, val: &Value) -> bool {
        let raw = val.raw();
        if !raw.contains('.') && !raw.contains(',') { return false; }
        match val.as_float() {
            Some(f) => (41.3..=51.3).contains(&f),
            None => false,
        }
    }
}

// --- Longitude WGS84 France métropolitaine ---

pub struct LongitudeWgsFrFormat;

impl LongitudeWgsFrFormat {
    pub fn detect(&self, val: &str) -> Option<f64> {
        let f = LongitudeWgsFormat.detect(val)?;
        if (-5.5..=9.8).contains(&f) { Some(f) } else { None }
    }
}

impl Detector for LongitudeWgsFrFormat {
    fn name(&self) -> &'static str { "longitude_wgs_fr_metropole" }
    fn python_type(&self) -> &'static str { "float" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        LongitudeWgsFormat.labels()
    }
    fn test(&self, val: &Value) -> bool {
        let raw = val.raw();
        if !raw.contains('.') && !raw.contains(',') { return false; }
        match val.as_float() {
            Some(f) => (-5.5..=9.8).contains(&f),
            None => false,
        }
    }
}

// --- Latitude Lambert 93 ---

pub struct LatitudeL93Format;

impl LatitudeL93Format {
    pub fn detect(&self, val: &str) -> Option<f64> {
        let normalized = val.replace(',', ".");
        let f: f64 = normalized.parse().ok()?;
        // frformat LatitudeL93 range: roughly 6000000-7200000
        if (6_000_000.0..=7_200_000.0).contains(&f) { Some(f) } else { None }
    }
}

impl Detector for LatitudeL93Format {
    fn name(&self) -> &'static str { "latitude_l93" }
    fn python_type(&self) -> &'static str { "float" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("latitude", 1.0), ("lat", 0.75), ("y", 0.5), ("yf", 0.5), ("yd", 0.5),
            ("coordonnee y", 1.0), ("coord y", 1.0), ("ycoord", 1.0), ("ylat", 1.0),
            ("y gps", 1.0), ("latitude wgs84", 1.0), ("y wgs84", 1.0), ("wsg", 0.75),
            ("gps", 0.5), ("y l93", 1.0), ("latitude lb93", 1.0), ("lamby", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool {
        match val.as_float() {
            Some(f) => (6_000_000.0..=7_200_000.0).contains(&f),
            None => false,
        }
    }
}

// --- Longitude Lambert 93 ---

pub struct LongitudeL93Format;

impl LongitudeL93Format {
    pub fn detect(&self, val: &str) -> Option<f64> {
        let normalized = val.replace(',', ".");
        let f: f64 = normalized.parse().ok()?;
        // frformat LongitudeL93 range: roughly 100000-1300000
        if (100_000.0..=1_300_000.0).contains(&f) { Some(f) } else { None }
    }
}

impl Detector for LongitudeL93Format {
    fn name(&self) -> &'static str { "longitude_l93" }
    fn python_type(&self) -> &'static str { "float" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("longitude", 1.0), ("long", 0.75), ("lon", 0.75), ("lng", 0.5),
            ("x", 0.5), ("xf", 0.5), ("xd", 0.5), ("coordonnee x", 1.0), ("coord x", 1.0),
            ("xcoord", 1.0), ("xlon", 1.0), ("xlong", 1.0), ("x gps", 1.0),
            ("longitude wgs84", 1.0), ("x wgs84", 1.0), ("wsg", 0.75), ("gps", 0.5),
            ("x l93", 1.0), ("longitude lb93", 1.0), ("lambx", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool {
        match val.as_float() {
            Some(f) => (100_000.0..=1_300_000.0).contains(&f),
            None => false,
        }
    }
}
