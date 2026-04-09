mod booleen;
mod float;
mod int;

pub trait Detector {
    fn name(&self) -> &'static str;
    fn python_type(&self) -> &'static str;
    fn proportion(&self) -> f64;
    fn labels(&self) -> &'static [(&'static str, f64)];
    fn mandatory_label(&self) -> bool {
        false
    }
    fn tags(&self) -> &'static [&'static str] {
        &[]
    }
    fn test(&self, val: &str) -> bool;
}

pub fn all_detectors() -> Vec<Box<dyn Detector>> {
    vec![
        Box::new(int::IntFormat),
        Box::new(float::FloatFormat),
        Box::new(booleen::BoolFormat),
    ]
}
