use std::collections::HashSet;
use std::sync::LazyLock;

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

pub fn test_commune(val: &Value) -> bool { COMMUNES.contains(val.normalized()) }

pub fn test_departement(val: &Value) -> bool { DEPARTEMENTS.contains(val.normalized()) }

pub fn test_region(val: &Value) -> bool { REGIONS.contains(val.normalized()) }

pub fn test_code_postal(val: &Value) -> bool { CODES_POSTAUX.contains(val.raw()) }

pub fn test_code_commune(val: &Value) -> bool { CODES_COMMUNES.contains(val.raw()) }

pub fn test_code_departement(val: &Value) -> bool {
    CODES_DEPARTEMENTS.contains(&val.raw().to_lowercase())
}

pub fn test_code_region(val: &Value) -> bool { CODES_REGIONS.contains(val.raw()) }
