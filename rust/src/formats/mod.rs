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

#[derive(Clone, Copy, strum::EnumIter)]
pub enum Format {
    Int,
    Float,
    Bool,
    Year,
    Date,
    DatetimeNaive,
    DatetimeAware,
    DatetimeRfc822,
    Email,
    Url,
    Uuid,
    Username,
    Sexe,
    TelFr,
    JourSemaine,
    Mois,
    Percent,
    Money,
    LatitudeWgs,
    LongitudeWgs,
    LatitudeWgsFr,
    LongitudeWgsFr,
    LatitudeL93,
    LongitudeL93,
    Siren,
    Siret,
    MongoObjectId,
    Json,
    LatlonWgs,
    Commune,
    Departement,
    Region,
    CodePostal,
    CodeCommune,
    CodeDepartement,
    CodeRegion,
    Adresse,
    CodeRna,
    CodeWaldec,
    Uai,
    CodeEpci,
    CodeFantoir,
    CodeImport,
    InseeApe700,
    CspInsee,
    CodeCspInsee,
    Pays,
    InseeCanton,
    IdRnb,
    GeoJson,
    LonlatWgs,
    IsoAlpha2,
    IsoAlpha3,
    IsoNumeric,
    DateFr,
    Binary,
}

macro_rules! dispatch {
    ($self:expr, $method:ident $(, $arg:expr)*) => {
        match $self {
            Format::Int => int::IntFormat.$method($($arg),*),
            Format::Float => float::FloatFormat.$method($($arg),*),
            Format::Bool => booleen::BoolFormat.$method($($arg),*),
            Format::Year => year::YearFormat.$method($($arg),*),
            Format::Date => date::DateFormat.$method($($arg),*),
            Format::DatetimeNaive => datetime_naive::DatetimeNaiveFormat.$method($($arg),*),
            Format::DatetimeAware => datetime_aware::DatetimeAwareFormat.$method($($arg),*),
            Format::DatetimeRfc822 => datetime_rfc822::DatetimeRfc822Format.$method($($arg),*),
            Format::Email => email::EmailFormat.$method($($arg),*),
            Format::Url => url::UrlFormat.$method($($arg),*),
            Format::Uuid => uuid::UuidFormat.$method($($arg),*),
            Format::Username => username::UsernameFormat.$method($($arg),*),
            Format::Sexe => sexe::SexeFormat.$method($($arg),*),
            Format::TelFr => tel_fr::TelFrFormat.$method($($arg),*),
            Format::JourSemaine => jour_de_la_semaine::JourSemaineFormat.$method($($arg),*),
            Format::Mois => mois_de_lannee::MoisFormat.$method($($arg),*),
            Format::Percent => percent::PercentFormat.$method($($arg),*),
            Format::Money => money::MoneyFormat.$method($($arg),*),
            Format::LatitudeWgs => geo::LatitudeWgsFormat.$method($($arg),*),
            Format::LongitudeWgs => geo::LongitudeWgsFormat.$method($($arg),*),
            Format::LatitudeWgsFr => geo::LatitudeWgsFrFormat.$method($($arg),*),
            Format::LongitudeWgsFr => geo::LongitudeWgsFrFormat.$method($($arg),*),
            Format::LatitudeL93 => geo::LatitudeL93Format.$method($($arg),*),
            Format::LongitudeL93 => geo::LongitudeL93Format.$method($($arg),*),
            Format::Siren => siren::SirenFormat.$method($($arg),*),
            Format::Siret => siret::SiretFormat.$method($($arg),*),
            Format::MongoObjectId => mongo_object_id::MongoObjectIdFormat.$method($($arg),*),
            Format::Json => json::JsonFormat.$method($($arg),*),
            Format::LatlonWgs => latlon_wgs::LatlonWgsFormat.$method($($arg),*),
            Format::Commune => fr_geo::CommuneFormat.$method($($arg),*),
            Format::Departement => fr_geo::DepartementFormat.$method($($arg),*),
            Format::Region => fr_geo::RegionFormat.$method($($arg),*),
            Format::CodePostal => fr_geo::CodePostalFormat.$method($($arg),*),
            Format::CodeCommune => fr_geo::CodeCommuneFormat.$method($($arg),*),
            Format::CodeDepartement => fr_geo::CodeDepartementFormat.$method($($arg),*),
            Format::CodeRegion => fr_geo::CodeRegionFormat.$method($($arg),*),
            Format::Adresse => adresse::AdresseFormat.$method($($arg),*),
            Format::CodeRna => code_rna::CodeRnaFormat.$method($($arg),*),
            Format::CodeWaldec => code_waldec::CodeWaldecFormat.$method($($arg),*),
            Format::Uai => uai::UaiFormat.$method($($arg),*),
            Format::CodeEpci => code_epci::CodeEpciFormat.$method($($arg),*),
            Format::CodeFantoir => code_fantoir::CodeFantoirFormat.$method($($arg),*),
            Format::CodeImport => code_import::CodeImportFormat.$method($($arg),*),
            Format::InseeApe700 => insee_ape700::InseeApe700Format.$method($($arg),*),
            Format::CspInsee => csp_insee::CspInseeFormat.$method($($arg),*),
            Format::CodeCspInsee => code_csp_insee::CodeCspInseeFormat.$method($($arg),*),
            Format::Pays => pays::PaysFormat.$method($($arg),*),
            Format::InseeCanton => insee_canton::InseeCantonFormat.$method($($arg),*),
            Format::IdRnb => id_rnb::IdRnbFormat.$method($($arg),*),
            Format::GeoJson => geojson::GeoJsonFormat.$method($($arg),*),
            Format::LonlatWgs => lonlat_wgs::LonlatWgsFormat.$method($($arg),*),
            Format::IsoAlpha2 => iso_country::IsoAlpha2Format.$method($($arg),*),
            Format::IsoAlpha3 => iso_country::IsoAlpha3Format.$method($($arg),*),
            Format::IsoNumeric => iso_country::IsoNumericFormat.$method($($arg),*),
            Format::DateFr => date_fr::DateFrFormat.$method($($arg),*),
            Format::Binary => binary::BinaryFormat.$method($($arg),*),
        }
    };
}

impl Format {
    pub fn name(&self) -> &'static str { dispatch!(self, name) }
    pub fn python_type(&self) -> &'static str { dispatch!(self, python_type) }
    pub fn proportion(&self) -> f64 { dispatch!(self, proportion) }
    pub fn labels(&self) -> &'static [(&'static str, f64)] { dispatch!(self, labels) }
    pub fn mandatory_label(&self) -> bool { dispatch!(self, mandatory_label) }
    pub fn test(&self, val: &Value) -> bool { dispatch!(self, test, val) }
}

pub fn all_formats() -> Vec<Format> {
    use strum::IntoEnumIterator;
    Format::iter().collect()
}
