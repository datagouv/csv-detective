use super::Detector;
use super::geo::{LatitudeWgsFormat, LongitudeWgsFormat};

pub struct LonlatWgsFormat;

impl LonlatWgsFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // same as latlon but lon,lat order
        let inner = if val.starts_with('[') && val.ends_with(']') {
            &val[1..val.len() - 1]
        } else {
            val
        };

        let comma_pos = inner.find(',')?;
        let lon_str = inner[..comma_pos].trim();
        let lat_str = inner[comma_pos + 1..].trim();

        LongitudeWgsFormat.detect(lon_str)?;
        LatitudeWgsFormat.detect(lat_str)?;

        Some(())
    }
}

impl Detector for LonlatWgsFormat {
    fn name(&self) -> &'static str { "lonlat_wgs" }
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
            ("point", 1.0), ("position", 1.0), ("wgs84", 1.0), ("lonlat", 1.0),
            ("lon lat", 1.0), ("y x", 0.75), ("yx", 0.75),
        ]
    }
    fn test(&self, val: &str) -> bool { self.detect(val).is_some() }
}
