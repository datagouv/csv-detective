use super::Detector;

pub struct MoisFormat;

const VALID: &[&str] = &[
    "janvier", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
    "jan", "fev", "mar", "avr", "jun", "jui", "juil", "aou",
    "sep", "sept", "oct", "nov", "dec",
];

impl MoisFormat {
    pub fn detect(&self, val: &str) -> Option<()> {
        // normalize unicode + lowercase
        let lower = val.to_lowercase();
        let normalized = normalize_accents(&lower);
        if VALID.contains(&normalized.as_str()) {
            Some(())
        } else {
            None
        }
    }
}

fn normalize_accents(s: &str) -> String {
    s.replace('é', "e")
        .replace('è', "e")
        .replace('ê', "e")
        .replace('û', "u")
        .replace('ù', "u")
        .replace('â', "a")
        .replace('à', "a")
        .replace('î', "i")
        .replace('ô', "o")
}

impl Detector for MoisFormat {
    fn name(&self) -> &'static str {
        "mois_de_lannee"
    }
    fn python_type(&self) -> &'static str {
        "string"
    }
    fn proportion(&self) -> f64 {
        1.0
    }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("mois", 1.0), ("month", 1.0)]
    }
    fn tags(&self) -> &'static [&'static str] {
        &["fr", "temp"]
    }
    fn test(&self, val: &str) -> bool {
        self.detect(val).is_some()
    }
}
