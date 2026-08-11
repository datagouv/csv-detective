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

impl Format {
    pub fn name(&self) -> &'static str {
        match self {
            Format::Int => "int",
            Format::Float => "float",
            Format::Bool => "booleen",
            Format::Year => "year",
            Format::Date => "date",
            Format::DatetimeNaive => "datetime_naive",
            Format::DatetimeAware => "datetime_aware",
            Format::DatetimeRfc822 => "datetime_rfc822",
            Format::Email => "email",
            Format::Url => "url",
            Format::Uuid => "uuid",
            Format::Username => "username",
            Format::Sexe => "sexe",
            Format::TelFr => "tel_fr",
            Format::JourSemaine => "jour_de_la_semaine",
            Format::Mois => "mois_de_lannee",
            Format::Percent => "percent",
            Format::Money => "money",
            Format::LatitudeWgs => "latitude_wgs",
            Format::LongitudeWgs => "longitude_wgs",
            Format::LatitudeWgsFr => "latitude_wgs_fr_metropole",
            Format::LongitudeWgsFr => "longitude_wgs_fr_metropole",
            Format::LatitudeL93 => "latitude_l93",
            Format::LongitudeL93 => "longitude_l93",
            Format::Siren => "siren",
            Format::Siret => "siret",
            Format::MongoObjectId => "mongo_object_id",
            Format::Json => "json",
            Format::LatlonWgs => "latlon_wgs",
            Format::Commune => "commune",
            Format::Departement => "departement",
            Format::Region => "region",
            Format::CodePostal => "code_postal",
            Format::CodeCommune => "code_commune",
            Format::CodeDepartement => "code_departement",
            Format::CodeRegion => "code_region",
            Format::Adresse => "adresse",
            Format::CodeRna => "code_rna",
            Format::CodeWaldec => "code_waldec",
            Format::Uai => "uai",
            Format::CodeEpci => "code_epci",
            Format::CodeFantoir => "code_fantoir",
            Format::CodeImport => "code_import",
            Format::InseeApe700 => "insee_ape700",
            Format::CspInsee => "csp_insee",
            Format::CodeCspInsee => "code_csp_insee",
            Format::Pays => "pays",
            Format::InseeCanton => "insee_canton",
            Format::IdRnb => "id_rnb",
            Format::GeoJson => "geojson",
            Format::LonlatWgs => "lonlat_wgs",
            Format::IsoAlpha2 => "iso_country_code_alpha2",
            Format::IsoAlpha3 => "iso_country_code_alpha3",
            Format::IsoNumeric => "iso_country_code_numeric",
            Format::DateFr => "date_fr",
            Format::Binary => "binary",
        }
    }

    pub fn python_type(&self) -> &'static str {
        match self {
            Format::Int | Format::Year => "int",
            Format::Float
            | Format::LatitudeWgs
            | Format::LongitudeWgs
            | Format::LatitudeWgsFr
            | Format::LongitudeWgsFr
            | Format::LatitudeL93
            | Format::LongitudeL93 => "float",
            Format::Bool => "bool",
            Format::Date => "date",
            Format::DatetimeNaive | Format::DatetimeAware | Format::DatetimeRfc822 => "datetime",
            Format::Json | Format::GeoJson => "json",
            Format::Binary => "binary",
            _ => "string",
        }
    }

    pub fn proportion(&self) -> f64 {
        match self {
            Format::Email => 0.9,
            Format::Uuid => 0.8,
            Format::TelFr => 0.7,
            Format::JourSemaine => 0.8,
            Format::Percent => 0.8,
            Format::Money => 0.8,
            Format::Commune => 0.8,
            Format::Departement => 0.9,
            Format::CodePostal => 0.9,
            Format::CodeCommune => 0.75,
            Format::Adresse => 0.55,
            Format::CodeRna => 0.9,
            Format::CodeWaldec => 0.9,
            Format::Uai => 0.8,
            Format::CodeEpci => 0.9,
            Format::Siren => 0.9,
            Format::Siret => 0.8,
            Format::MongoObjectId => 0.8,
            Format::InseeApe700 => 0.8,
            Format::InseeCanton => 0.9,
            Format::Pays => 0.6,
            Format::CodeImport => 0.9,
            _ => 1.0,
        }
    }

    pub fn mandatory_label(&self) -> bool {
        matches!(
            self,
            Format::LatitudeWgs
                | Format::LongitudeWgs
                | Format::LatitudeWgsFr
                | Format::LongitudeWgsFr
                | Format::LatitudeL93
                | Format::LongitudeL93
                | Format::Siren
                | Format::Siret
                | Format::CodeEpci
                | Format::CodeFantoir
                | Format::CodePostal
                | Format::CodeCommune
                | Format::CodeDepartement
                | Format::CodeRegion
                | Format::LatlonWgs
                | Format::LonlatWgs
                | Format::IdRnb
        )
    }

    pub fn labels(&self) -> &'static [(&'static str, f64)] {
        match self {
            Format::Int => &[("nb", 0.75), ("nombre", 1.0), ("nbre", 0.75)],
            Format::Float => &[("part", 1.0), ("ratio", 1.0), ("taux", 1.0)],
            Format::Bool => &[("is ", 1.0), ("has ", 1.0), ("est ", 1.0)],
            Format::Year => &[("year", 1.0), ("annee", 1.0), ("naissance", 1.0), ("exercice", 1.0)],
            Format::Date => &[("date", 1.0), ("mise a jour", 1.0), ("modifie", 1.0), ("maj", 0.75), ("datemaj", 1.0), ("update", 1.0), ("created", 1.0), ("modified", 1.0), ("jour", 0.75), ("periode", 0.75), ("dpc", 0.5), ("yyyymmdd", 1.0), ("aaaammjj", 1.0)],
            Format::DatetimeNaive | Format::DatetimeAware | Format::DatetimeRfc822 => &[("date", 1.0), ("mise a jour", 1.0), ("modifie", 1.0), ("maj", 0.75), ("datemaj", 1.0), ("update", 1.0), ("created", 1.0), ("modified", 1.0), ("datetime", 1.0), ("timestamp", 1.0)],
            Format::Email => &[("email", 1.0), ("mail", 1.0), ("courriel", 1.0), ("contact", 1.0), ("mel", 1.0), ("lieucourriel", 1.0), ("coordinates.emailcontact", 1.0), ("e mail", 1.0), ("mo mail", 1.0), ("adresse mail", 1.0), ("adresse email", 1.0)],
            Format::Url => &[("url", 1.0), ("url source", 1.0), ("site web", 1.0), ("source url", 1.0), ("site internet", 1.0), ("remote url", 1.0), ("web", 1.0), ("site", 1.0), ("lien", 1.0), ("site data", 1.0), ("lien url", 1.0), ("lien vers le fichier", 1.0), ("sitweb", 1.0), ("interneturl", 1.0)],
            Format::Uuid => &[("id", 1.0), ("identifiant", 1.0)],
            Format::Username => &[("account", 1.0), ("username", 1.0), ("user", 0.75)],
            Format::Sexe => &[("sexe", 1.0), ("sex", 1.0), ("civilite", 1.0), ("genre", 1.0)],
            Format::TelFr => &[("telephone", 1.0), ("tel", 1.0), ("phone", 1.0), ("num tel", 1.0), ("tel mob", 1.0)],
            Format::JourSemaine => &[("jour semaine", 1.0), ("type jour", 1.0), ("jour de la semaine", 1.0), ("saufjour", 1.0), ("nomjour", 1.0), ("jour", 0.75), ("jour de fermeture", 1.0)],
            Format::Mois => &[("mois", 1.0), ("month", 1.0)],
            Format::Percent => &[("pourcent", 1.0), ("part", 0.75), ("pct", 0.75)],
            Format::Money => &[("budget", 1.0), ("salaire", 1.0), ("euro", 1.0), ("euros", 1.0), ("pret", 1.0), ("montant", 1.0)],
            Format::LatitudeWgs | Format::LatitudeWgsFr => &[("latitude", 1.0), ("lat", 0.75), ("y", 0.5), ("yf", 0.5), ("yd", 0.5), ("coordonnee y", 1.0), ("coord y", 1.0), ("ycoord", 1.0), ("ylat", 1.0), ("y gps", 1.0), ("latitude wgs84", 1.0), ("y wgs84", 1.0), ("wsg", 0.75), ("gps", 0.5)],
            Format::LongitudeWgs | Format::LongitudeWgsFr => &[("longitude", 1.0), ("long", 0.75), ("lon", 0.75), ("lng", 0.5), ("x", 0.5), ("xf", 0.5), ("xd", 0.5), ("coordonnee x", 1.0), ("coord x", 1.0), ("xcoord", 1.0), ("xlon", 1.0), ("xlong", 1.0), ("x gps", 1.0), ("longitude wgs84", 1.0), ("x wgs84", 1.0), ("wsg", 0.75), ("gps", 0.5)],
            Format::LatitudeL93 => &[("latitude", 1.0), ("lat", 0.75), ("y", 0.5), ("yf", 0.5), ("yd", 0.5), ("coordonnee y", 1.0), ("coord y", 1.0), ("ycoord", 1.0), ("ylat", 1.0), ("y gps", 1.0), ("latitude wgs84", 1.0), ("y wgs84", 1.0), ("wsg", 0.75), ("gps", 0.5), ("y l93", 1.0), ("latitude lb93", 1.0), ("lamby", 1.0)],
            Format::LongitudeL93 => &[("longitude", 1.0), ("long", 0.75), ("lon", 0.75), ("lng", 0.5), ("x", 0.5), ("xf", 0.5), ("xd", 0.5), ("coordonnee x", 1.0), ("coord x", 1.0), ("xcoord", 1.0), ("xlon", 1.0), ("xlong", 1.0), ("x gps", 1.0), ("longitude wgs84", 1.0), ("x wgs84", 1.0), ("wsg", 0.75), ("gps", 0.5), ("x l93", 1.0), ("longitude lb93", 1.0), ("lambx", 1.0)],
            Format::Siren => &[("siren", 1.0), ("n° siren", 1.0), ("siren organisme", 1.0), ("siren titulaire", 1.0), ("numero siren", 1.0), ("epci", 0.9)],
            Format::Siret => &[("siret", 1.0), ("num siret", 1.0), ("siretacheteur", 1.0), ("n° siret", 1.0), ("coll siret", 1.0), ("epci", 1.0)],
            Format::MongoObjectId => &[("id", 1.0), ("objectid", 1.0)],
            Format::Json => &[("list", 1.0), ("dict", 1.0), ("complex", 1.0)],
            Format::GeoJson => &[("json geojson", 1.0), ("json", 1.0), ("geojson", 1.0), ("geo shape", 1.0), ("geom", 0.75), ("geometry", 1.0), ("geoshape", 1.0)],
            Format::LatlonWgs => &[("ban", 1.0), ("coordinates", 1.0), ("coordonnees", 1.0), ("coordonnees insee", 1.0), ("coord", 1.0), ("geo", 0.5), ("geopoint", 1.0), ("geoloc", 1.0), ("geolocalisation", 1.0), ("geom", 0.75), ("geometry", 1.0), ("gps", 1.0), ("localisation", 1.0), ("point", 1.0), ("position", 1.0), ("wgs84", 1.0), ("latlon", 1.0), ("lat lon", 1.0), ("x y", 0.75), ("xy", 0.75)],
            Format::LonlatWgs => &[("ban", 1.0), ("coordinates", 1.0), ("coordonnees", 1.0), ("coordonnees insee", 1.0), ("coord", 1.0), ("geo", 0.5), ("geopoint", 1.0), ("geoloc", 1.0), ("geolocalisation", 1.0), ("geom", 0.75), ("geometry", 1.0), ("gps", 1.0), ("localisation", 1.0), ("point", 1.0), ("position", 1.0), ("wgs84", 1.0), ("lonlat", 1.0), ("lon lat", 1.0), ("y x", 0.75), ("yx", 0.75)],
            Format::Commune => &[("commune", 1.0), ("ville", 1.0), ("libelle commune", 1.0)],
            Format::Departement => &[("departement", 1.0), ("libelle du departement", 1.0), ("deplib", 1.0), ("nom dept", 1.0), ("dept", 0.75), ("libdepartement", 1.0), ("nom departement", 1.0), ("libelle dep", 1.0), ("libelle departement", 1.0), ("lb departements", 1.0), ("dep libusage", 1.0), ("lb departement", 1.0), ("nom dep", 1.0)],
            Format::Region => &[("region", 1.0), ("libelle region", 1.0), ("nom region", 1.0), ("libelle reg", 1.0), ("nom reg", 1.0), ("reg libusage", 1.0), ("nom de la region", 1.0), ("regionorg", 1.0), ("regionlieu", 1.0), ("reg", 0.5), ("nom officiel region", 1.0)],
            Format::CodePostal => &[("code postal", 1.0), ("postal code", 1.0), ("postcode", 1.0), ("post code", 1.0), ("cp", 0.5), ("codes postaux", 1.0), ("location postcode", 1.0)],
            Format::CodeCommune => &[("code commune insee", 1.0), ("code insee", 1.0), ("codes insee", 1.0), ("code commune", 1.0), ("code insee commune", 1.0), ("insee", 0.75), ("code com", 1.0), ("com", 0.5), ("code", 0.5)],
            Format::CodeDepartement => &[("code departement", 1.0), ("code_departement", 1.0), ("dep", 0.5), ("departement", 1.0), ("dept", 0.75)],
            Format::CodeRegion => &[("code region", 1.0), ("reg", 0.5), ("code insee region", 1.0), ("region", 1.0)],
            Format::Adresse => &[("adresse", 1.0), ("localisation", 1.0), ("adresse postale", 1.0), ("adresse geographique", 1.0), ("adr", 0.5), ("adresse complete", 1.0), ("adresse station", 1.0)],
            Format::CodeRna => &[("code rna", 1.0), ("rna", 1.0), ("n° inscription association", 1.0), ("identifiant association", 1.0), ("asso", 0.75)],
            Format::CodeWaldec => &[("code waldec", 1.0), ("waldec", 1.0)],
            Format::Uai => &[("uai", 1.0), ("code etablissement", 1.0), ("code uai", 1.0), ("uai   identifiant", 1.0), ("numero uai", 1.0), ("rne", 0.75), ("numero de l etablissement", 1.0), ("code rne", 1.0), ("codeetab", 1.0), ("code uai de l etablissement", 1.0), ("ref uai", 1.0), ("cd rne", 1.0), ("numerouai", 1.0), ("numero d etablissement", 1.0), ("numero etablissement", 1.0)],
            Format::CodeEpci => &[("epci", 1.0)],
            Format::CodeFantoir => &[("cadastre1", 1.0), ("code fantoir", 1.0), ("fantoir", 1.0)],
            Format::CodeImport => &[("code", 0.5)],
            Format::InseeApe700 => &[("code ape", 1.0), ("code activite (ape)", 1.0), ("code naf", 1.0), ("code naf organisme designe", 1.0), ("code naf organisme designant", 1.0), ("base sirene : code ape de l etablissement siege", 1.0), ("naf", 0.75), ("ape", 0.5)],
            Format::CspInsee => &[("csp insee", 1.0), ("csp", 0.75), ("categorie socioprofessionnelle", 1.0), ("sociopro", 1.0)],
            Format::CodeCspInsee => &[("code csp insee", 1.0), ("code csp", 1.0)],
            Format::Pays => &[("pays", 1.0), ("payslieu", 1.0), ("paysorg", 1.0), ("country", 1.0), ("pays lib", 1.0), ("lieupays", 1.0), ("pays beneficiaire", 1.0), ("nom du pays", 1.0), ("libelle pays", 1.0)],
            Format::InseeCanton => &[("insee canton", 1.0), ("canton", 1.0), ("cant", 0.5), ("nom canton", 1.0)],
            Format::IdRnb => &[("rnb", 1.0), ("batid", 1.0)],
            Format::IsoAlpha2 | Format::IsoAlpha3 | Format::IsoNumeric => &[("iso country code", 1.0), ("code pays", 1.0), ("pays", 1.0), ("country", 1.0), ("nation", 1.0), ("pays code", 1.0), ("code pays (iso)", 1.0), ("code", 0.5)],
            Format::DateFr => &[("date", 1.0)],
            Format::Binary => &[("bytes", 1.0), ("binary", 1.0), ("image", 1.0), ("encode", 1.0), ("content", 1.0)],
        }
    }

    pub fn test(&self, val: &Value) -> bool {
        match self {
            Format::Int => int::test(val),
            Format::Float => float::test(val),
            Format::Bool => booleen::test(val),
            Format::Year => year::test(val),
            Format::Date => date::test(val),
            Format::DatetimeNaive => datetime_naive::test(val),
            Format::DatetimeAware => datetime_aware::test(val),
            Format::DatetimeRfc822 => datetime_rfc822::test(val),
            Format::Email => email::test(val),
            Format::Url => url::test(val),
            Format::Uuid => uuid::test(val),
            Format::Username => username::test(val),
            Format::Sexe => sexe::test(val),
            Format::TelFr => tel_fr::test(val),
            Format::JourSemaine => jour_de_la_semaine::test(val),
            Format::Mois => mois_de_lannee::test(val),
            Format::Percent => percent::test(val),
            Format::Money => money::test(val),
            Format::LatitudeWgs => geo::test_latitude_wgs(val),
            Format::LongitudeWgs => geo::test_longitude_wgs(val),
            Format::LatitudeWgsFr => geo::test_latitude_wgs_fr(val),
            Format::LongitudeWgsFr => geo::test_longitude_wgs_fr(val),
            Format::LatitudeL93 => geo::test_latitude_l93(val),
            Format::LongitudeL93 => geo::test_longitude_l93(val),
            Format::Siren => siren::test(val),
            Format::Siret => siret::test(val),
            Format::MongoObjectId => mongo_object_id::test(val),
            Format::Json => json::test(val),
            Format::LatlonWgs => latlon_wgs::test(val),
            Format::Commune => fr_geo::test_commune(val),
            Format::Departement => fr_geo::test_departement(val),
            Format::Region => fr_geo::test_region(val),
            Format::CodePostal => fr_geo::test_code_postal(val),
            Format::CodeCommune => fr_geo::test_code_commune(val),
            Format::CodeDepartement => fr_geo::test_code_departement(val),
            Format::CodeRegion => fr_geo::test_code_region(val),
            Format::Adresse => adresse::test(val),
            Format::CodeRna => code_rna::test(val),
            Format::CodeWaldec => code_waldec::test(val),
            Format::Uai => uai::test(val),
            Format::CodeEpci => code_epci::test(val),
            Format::CodeFantoir => code_fantoir::test(val),
            Format::CodeImport => code_import::test(val),
            Format::InseeApe700 => insee_ape700::test(val),
            Format::CspInsee => csp_insee::test(val),
            Format::CodeCspInsee => code_csp_insee::test(val),
            Format::Pays => pays::test(val),
            Format::InseeCanton => insee_canton::test(val),
            Format::IdRnb => id_rnb::test(val),
            Format::GeoJson => geojson::test(val),
            Format::LonlatWgs => lonlat_wgs::test(val),
            Format::IsoAlpha2 => iso_country::test_alpha2(val),
            Format::IsoAlpha3 => iso_country::test_alpha3(val),
            Format::IsoNumeric => iso_country::test_numeric(val),
            Format::DateFr => date_fr::test(val),
            Format::Binary => binary::test(val),
        }
    }
}

pub fn all_formats() -> Vec<Format> {
    use strum::IntoEnumIterator;
    Format::iter().collect()
}
