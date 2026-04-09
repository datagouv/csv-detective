use std::sync::LazyLock;

use aho_corasick::AhoCorasick;

use super::Detector;

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
    let lower = val.to_lowercase();
    lower
        .replace('à', "a")
        .replace('â', "a")
        .replace('ç', "c")
        .replace('é', "e")
        .replace('è', "e")
        .replace('ê', "e")
        .replace('î', "i")
        .replace('ï', "i")
        .replace('ô', "o")
        .replace('ö', "o")
        .replace('ù', "u")
        .replace('û', "u")
        .replace('ü', "u")
        .replace('\'', " ")
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
    fn test(&self, val: &str) -> bool {
        if val.len() > 150 {
            return false;
        }
        let normalized = normalize_adresse(val);
        AC.is_match(&normalized)
    }
}

pub struct AdresseFormat;
