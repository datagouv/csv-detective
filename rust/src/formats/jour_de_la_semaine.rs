use super::Detector;
use crate::value::Value;

pub struct JourSemaineFormat;

const VALID: &[&str] = &[
    "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche",
    "lun", "mar", "mer", "jeu", "ven", "sam", "dim",
];

impl JourSemaineFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        let lower = val.to_lowercase();
        if VALID.contains(&lower.as_str()) {
            Some(())
        } else {
            None
        }
    }
}

impl Detector for JourSemaineFormat {
    fn name(&self) -> &'static str {
        "jour_de_la_semaine"
    }
    fn python_type(&self) -> &'static str {
        "string"
    }
    fn proportion(&self) -> f64 {
        0.8
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("jour semaine", 1.0),
            ("type jour", 1.0),
            ("jour de la semaine", 1.0),
            ("saufjour", 1.0),
            ("nomjour", 1.0),
            ("jour", 0.75),
            ("jour de fermeture", 1.0),
        ]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["fr", "temp"]
    }
    fn test(&self, val: &Value) -> bool {
        self.detect(val.raw()).is_some()
    }
}
