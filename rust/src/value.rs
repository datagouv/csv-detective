use std::cell::OnceCell;

use crate::formats::fr_geo::normalize;

pub struct Value<'a> {
    raw: &'a str,
    normalized: OnceCell<String>,
    as_float: OnceCell<Option<f64>>,
}

impl<'a> Value<'a> {
    pub fn new(raw: &'a str) -> Self {
        Self {
            raw,
            normalized: OnceCell::new(),
            as_float: OnceCell::new(),
        }
    }

    pub fn raw(&self) -> &str {
        self.raw
    }

    pub fn normalized(&self) -> &str {
        self.normalized.get_or_init(|| normalize(self.raw))
    }

    pub fn as_float(&self) -> Option<f64> {
        *self.as_float.get_or_init(|| {
            let s = self.raw.replace(',', ".");
            s.parse::<f64>().ok()
        })
    }
}
