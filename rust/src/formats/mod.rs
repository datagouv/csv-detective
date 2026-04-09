mod adresse;
mod binary;
mod booleen;
mod code_csp_insee;
mod code_epci;
mod code_fantoir;
mod code_import;
mod code_rna;
mod code_waldec;
mod csp_insee;
mod date;
mod date_fr;
mod datetime_aware;
mod datetime_naive;
mod datetime_rfc822;
mod email;
pub(crate) mod float;
pub(crate) mod fr_geo;
pub(crate) mod geo;
mod geojson;
mod id_rnb;
mod insee_ape700;
mod insee_canton;
mod int;
mod iso_country;
mod jour_de_la_semaine;
mod json;
mod latlon_wgs;
mod lonlat_wgs;
mod mois_de_lannee;
mod money;
mod mongo_object_id;
mod pays;
mod percent;
mod sexe;
pub(crate) mod siren;
mod siret;
mod tel_fr;
mod uai;
mod url;
mod username;
mod uuid;
mod year;

use crate::value::Value;

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
    fn test(&self, val: &Value) -> bool;
}

pub fn all_detectors() -> Vec<Box<dyn Detector>> {
    vec![
        Box::new(int::IntFormat),
        Box::new(float::FloatFormat),
        Box::new(booleen::BoolFormat),
        Box::new(year::YearFormat),
        Box::new(date::DateFormat),
        Box::new(datetime_naive::DatetimeNaiveFormat),
        Box::new(datetime_aware::DatetimeAwareFormat),
        Box::new(datetime_rfc822::DatetimeRfc822Format),
        Box::new(email::EmailFormat),
        Box::new(url::UrlFormat),
        Box::new(uuid::UuidFormat),
        Box::new(username::UsernameFormat),
        Box::new(sexe::SexeFormat),
        Box::new(tel_fr::TelFrFormat),
        Box::new(jour_de_la_semaine::JourSemaineFormat),
        Box::new(mois_de_lannee::MoisFormat),
        Box::new(percent::PercentFormat),
        Box::new(money::MoneyFormat),
        Box::new(geo::LatitudeWgsFormat),
        Box::new(geo::LongitudeWgsFormat),
        Box::new(geo::LatitudeWgsFrFormat),
        Box::new(geo::LongitudeWgsFrFormat),
        Box::new(geo::LatitudeL93Format),
        Box::new(geo::LongitudeL93Format),
        Box::new(siren::SirenFormat),
        Box::new(siret::SiretFormat),
        Box::new(mongo_object_id::MongoObjectIdFormat),
        Box::new(json::JsonFormat),
        Box::new(latlon_wgs::LatlonWgsFormat),
        Box::new(fr_geo::CommuneFormat),
        Box::new(fr_geo::DepartementFormat),
        Box::new(fr_geo::RegionFormat),
        Box::new(fr_geo::CodePostalFormat),
        Box::new(fr_geo::CodeCommuneFormat),
        Box::new(fr_geo::CodeDepartementFormat),
        Box::new(fr_geo::CodeRegionFormat),
        Box::new(adresse::AdresseFormat),
        Box::new(code_rna::CodeRnaFormat),
        Box::new(code_waldec::CodeWaldecFormat),
        Box::new(uai::UaiFormat),
        Box::new(code_epci::CodeEpciFormat),
        Box::new(code_fantoir::CodeFantoirFormat),
        Box::new(code_import::CodeImportFormat),
        Box::new(insee_ape700::InseeApe700Format),
        Box::new(csp_insee::CspInseeFormat),
        Box::new(code_csp_insee::CodeCspInseeFormat),
        Box::new(pays::PaysFormat),
        Box::new(insee_canton::InseeCantonFormat),
        Box::new(id_rnb::IdRnbFormat),
        Box::new(geojson::GeoJsonFormat),
        Box::new(lonlat_wgs::LonlatWgsFormat),
        Box::new(iso_country::IsoAlpha2Format),
        Box::new(iso_country::IsoAlpha3Format),
        Box::new(iso_country::IsoNumericFormat),
        Box::new(date_fr::DateFrFormat),
        Box::new(binary::BinaryFormat),
    ]
}
