use std::collections::HashSet;
use std::sync::LazyLock;

use super::Detector;
use crate::value::Value;

fn load_set(data: &str) -> HashSet<String> {
    data.lines().map(|l| l.to_string()).collect()
}

pub fn normalize(val: &str) -> String {
    let mut result = String::with_capacity(val.len());
    let mut last_was_space = true;

    for c in val.chars() {
        match c {
            'A'..='Z' => {
                result.push(c.to_ascii_lowercase());
                last_was_space = false;
            }
            'a'..='z' | '0'..='9' => {
                result.push(c);
                last_was_space = false;
            }
            'à' | 'â' | 'ä' | 'À' | 'Â' | 'Ä' => { result.push('a'); last_was_space = false; }
            'ç' | 'Ç' => { result.push('c'); last_was_space = false; }
            'é' | 'è' | 'ê' | 'ë' | 'É' | 'È' | 'Ê' | 'Ë' => { result.push('e'); last_was_space = false; }
            'î' | 'ï' | 'Î' | 'Ï' => { result.push('i'); last_was_space = false; }
            'ô' | 'ö' | 'Ô' | 'Ö' => { result.push('o'); last_was_space = false; }
            'ù' | 'û' | 'ü' | 'Ù' | 'Û' | 'Ü' => { result.push('u'); last_was_space = false; }
            'ÿ' | 'Ÿ' => { result.push('y'); last_was_space = false; }
            'œ' | 'Œ' => { result.push_str("oe"); last_was_space = false; }
            'æ' | 'Æ' => { result.push_str("ae"); last_was_space = false; }
            _ => {
                if !last_was_space {
                    result.push(' ');
                    last_was_space = true;
                }
            }
        }
    }

    if last_was_space && !result.is_empty() {
        result.pop();
    }
    result
}

static COMMUNES: LazyLock<HashSet<String>> =
    LazyLock::new(|| load_set(include_str!("../../data/communes.txt")));
static DEPARTEMENTS: LazyLock<HashSet<String>> =
    LazyLock::new(|| load_set(include_str!("../../data/departements.txt")));
static REGIONS: LazyLock<HashSet<String>> =
    LazyLock::new(|| load_set(include_str!("../../data/regions.txt")));
static CODES_POSTAUX: LazyLock<HashSet<String>> =
    LazyLock::new(|| load_set(include_str!("../../data/codes_postaux.txt")));
static CODES_COMMUNES: LazyLock<HashSet<String>> =
    LazyLock::new(|| load_set(include_str!("../../data/codes_communes.txt")));
static CODES_DEPARTEMENTS: LazyLock<HashSet<String>> =
    LazyLock::new(|| load_set(include_str!("../../data/codes_departements.txt")));
static CODES_REGIONS: LazyLock<HashSet<String>> =
    LazyLock::new(|| load_set(include_str!("../../data/codes_regions.txt")));

// --- Commune ---

pub struct CommuneFormat;

impl Detector for CommuneFormat {
    fn name(&self) -> &'static str { "commune" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.8 }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[("commune", 1.0), ("ville", 1.0), ("libelle commune", 1.0)]
    }
    fn test(&self, val: &Value) -> bool { COMMUNES.contains(val.normalized()) }
}

// --- Departement ---

pub struct DepartementFormat;

impl Detector for DepartementFormat {
    fn name(&self) -> &'static str { "departement" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.9 }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("departement", 1.0), ("libelle du departement", 1.0), ("deplib", 1.0),
            ("nom dept", 1.0), ("dept", 0.75), ("libdepartement", 1.0),
            ("nom departement", 1.0), ("libelle dep", 1.0), ("libelle departement", 1.0),
            ("lb departements", 1.0), ("dep libusage", 1.0), ("lb departement", 1.0),
            ("nom dep", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool { DEPARTEMENTS.contains(val.normalized()) }
}

// --- Region ---

pub struct RegionFormat;

impl Detector for RegionFormat {
    fn name(&self) -> &'static str { "region" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("region", 1.0), ("libelle region", 1.0), ("nom region", 1.0),
            ("libelle reg", 1.0), ("nom reg", 1.0), ("reg libusage", 1.0),
            ("nom de la region", 1.0), ("regionorg", 1.0), ("regionlieu", 1.0),
            ("reg", 0.5), ("nom officiel region", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool { REGIONS.contains(val.normalized()) }
}

// --- Code postal ---

pub struct CodePostalFormat;

impl Detector for CodePostalFormat {
    fn name(&self) -> &'static str { "code_postal" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.9 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("code postal", 1.0), ("postal code", 1.0), ("postcode", 1.0),
            ("post code", 1.0), ("cp", 0.5), ("codes postaux", 1.0),
            ("location postcode", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool { CODES_POSTAUX.contains(val.raw()) }
}

// --- Code commune ---

pub struct CodeCommuneFormat;

impl Detector for CodeCommuneFormat {
    fn name(&self) -> &'static str { "code_commune" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 0.75 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("code commune insee", 1.0), ("code insee", 1.0), ("codes insee", 1.0),
            ("code commune", 1.0), ("code insee commune", 1.0), ("insee", 0.75),
            ("code com", 1.0), ("com", 0.5), ("code", 0.5),
        ]
    }
    fn test(&self, val: &Value) -> bool { CODES_COMMUNES.contains(val.raw()) }
}

// --- Code département ---

pub struct CodeDepartementFormat;

impl Detector for CodeDepartementFormat {
    fn name(&self) -> &'static str { "code_departement" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("code departement", 1.0), ("code_departement", 1.0),
            ("dep", 0.5), ("departement", 1.0), ("dept", 0.75),
        ]
    }
    fn test(&self, val: &Value) -> bool {
        CODES_DEPARTEMENTS.contains(&val.raw().to_lowercase())
    }
}

// --- Code région ---

pub struct CodeRegionFormat;

impl Detector for CodeRegionFormat {
    fn name(&self) -> &'static str { "code_region" }
    fn python_type(&self) -> &'static str { "string" }
    fn proportion(&self) -> f64 { 1.0 }
    fn mandatory_label(&self) -> bool { true }
    fn tags(&self) -> &'static [&'static str] { &["fr", "geo"] }
    fn labels(&self) -> &'static [(&'static str, f64)] {
        &[
            ("code region", 1.0), ("reg", 0.5),
            ("code insee region", 1.0), ("region", 1.0),
        ]
    }
    fn test(&self, val: &Value) -> bool { CODES_REGIONS.contains(val.raw()) }
}
