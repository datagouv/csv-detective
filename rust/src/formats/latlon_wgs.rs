use super::Detector;
use crate::value::Value;
use super::geo::{LatitudeWgsFormat, LongitudeWgsFormat};

pub struct LatlonWgsFormat;

impl LatlonWgsFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // optional brackets
        let inner = if val.starts_with('[') && val.ends_with(']') {
            &val[1..val.len() - 1]
        } else {
            val
        };

        // split on comma — must have exactly one comma
        let comma_pos = inner.find(',')?;
        let lat_str = inner[..comma_pos].trim();
        let lon_str = inner[comma_pos + 1..].trim();

        // both must be valid floats (not integers)
        LatitudeWgsFormat.detect(lat_str)?;
        LongitudeWgsFormat.detect(lon_str)?;

        Some(())
    }
}

impl Detector for LatlonWgsFormat {
    fn name(&self) -> &'static str { "latlon_wgs" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("ban", 1.0), ("coordinates", 1.0), ("coordonnees", 1.0),
            ("coordonnees insee", 1.0), ("coord", 1.0), ("geo", 0.5),
            ("geopoint", 1.0), ("geoloc", 1.0), ("geolocalisation", 1.0),
            ("geom", 0.75), ("geometry", 1.0), ("gps", 1.0), ("localisation", 1.0),
            ("point", 1.0), ("position", 1.0), ("wgs84", 1.0), ("latlon", 1.0),
            ("lat lon", 1.0), ("x y", 0.75), ("xy", 0.75),
        ]
    }
    fn test(&self, val: &Value) -> bool { self.detect(val.raw()).is_some() }
}
