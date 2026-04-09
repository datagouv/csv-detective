use std::sync::LazyLock;

use aho_corasick::AhoCorasick;

use super::Detector;
use crate::value::Value;

const VOIE_KEYWORDS: &[&str] = &[
    "aire ", "allee ", "avenue ", "base ", "boulevard ", "cami ", "carrefour ",
    "chemin ", "cheminement ", "chaussee ", "cite ", "clos ", "coin ", "corniche ",
    "cote ", "cour ", "cours ", "domaine ", "descente ", "ecart ", "esplanade ",
    "faubourg ", "gare ", "grande rue", "hameau ", "halle ", "ilot ", "impasse ",
    "lieu dit", "lotissement ", "marche ", "montee ", "parc ", "passage ", "place ",
    "plan ", "plaine ", "plateau ", "pont ", "port ", "promenade ", "parvis ",
    "quartier ", "quai ", "residence ", "ruelle ", "rocade ", "rond point",
    "route ", "rue ", "square ", "tour ", "traverse ", "villa ", "village ",
    "voie ", "zone artisanale", "zone d'amenagement concerte",
    "zone d'amenagement differe", "zone industrielle", "zone ",
    // abbreviations
    "av ", "pl ", "bd ", "chs ", "dom ", "ham ", "ld ", "vlge ", "za ",
    "zac ", "zad ", "zi ", "fg ", "imp ", "mte",
];

static AC: LazyLock<AhoCorasick> =
    LazyLock::new(|| AhoCorasick::new(VOIE_KEYWORDS).expect("failed to build AhoCorasick"));

fn normalize_adresse(val: &str) -> String {
    let mut result = String::with_capacity(val.len());
    for c in val.chars() {
        match c {
            'A'..='Z' => result.push(c.to_ascii_lowercase()),
            'a'..='z' | '0'..='9' | ' ' | '-' => result.push(c),
            'à' | 'â' => result.push('a'),
            'ç' => result.push('c'),
            'é' | 'è' | 'ê' => result.push('e'),
            'î' | 'ï' => result.push('i'),
            'ô' | 'ö' => result.push('o'),
            'ù' | 'û' | 'ü' => result.push('u'),
            '\'' => result.push(' '),
            _ => result.push(c),
        }
    }
    result
}

impl Detector for AdresseFormat {
    fn name(&self) -> &'static str { "adresse" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.55 }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("adresse", 1.0), ("localisation", 1.0), ("adresse postale", 1.0),
            ("adresse geographique", 1.0), ("adr", 0.5), ("adresse complete", 1.0),
            ("adresse station", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool {
        let raw = val.raw();
        if raw.len() > 150 {
            return false;
        }
        let normalized = normalize_adresse(raw);
        AC.is_match(&normalized)
    }
}

pub struct AdresseFormat;
