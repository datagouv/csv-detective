# List of currently available formats

| name | description | python type | tags | default proportion | mandatory label | example |
|------|-------------|-------------|------|--------------------|-----------------|---------|
| adresse | French address | string | fr, geo | 0.55 | False | `rue du martyr` |
| binary | Binary data (bytes string) | binary | type | 1 | False | `b''` |
| booleen | Boolean or boolean-like value (yes/no, 1/0...) | bool | type | 1 | False | `oui` |
| code_commune | French commune code, from the INSEE reference source | string | fr, geo | 0.75 | True | `91471` |
| code_csp_insee | French socio-professional category code, from the INSEE reference source | string | fr | 1 | False | `121f` |
| code_departement | French département code | string | fr, geo | 1 | True | `75` |
| code_epci | French EPCI (group of communes) code, subgroup of SIREN | string | fr, geo | 0.9 | True | `200000172` |
| code_fantoir | Code from the [FANTOIR reference source](https://www.data.gouv.fr/datasets/fichier-fantoir-des-voies-et-lieux-dits) (deprecated since july 2023) | string | fr, geo | 1 | True | `7755A` |
| code_import | Code from the [Import registry](https://www.data.gouv.fr/datasets/repertoire-national-des-associations) | string | fr | 0.9 | False | `123S1871092288` |
| code_postal | French postcode from [La Poste registry](https://www.data.gouv.fr/datasets/base-officielle-des-codes-postaux) | string | fr, geo | 0.9 | True | `75020` |
| code_region | French région code | string | fr, geo | 1 | True | `32` |
| code_rna | French association identifier, from the national assiocation registry ([RNA](https://www.data.gouv.fr/datasets/repertoire-national-des-associations)) | string | fr | 0.9 | False | `W751515517` |
| code_waldec | French association identifier, from the [WALDEC registry](https://www.data.gouv.fr/datasets/repertoire-national-des-associations) | string | fr | 0.9 | False | `W123456789` |
| commune | French commune name | string | fr, geo | 0.8 | False | `saint denis` |
| csp_insee | French socio-professional category label, from the INSEE reference source | string | fr | 1 | False | `employes de la poste` |
| date | Date (flexible formats) | date | temp, type | 1 | False | `1960-08-07` |
| date_fr | Full text date in French | string | fr, temp | 1 | False | `13 février 1996` |
| datetime_aware | Datetime with timezone information (flexible formats) | datetime | temp, type | 1 | False | `2021-06-22 10:20:10-04:00` |
| datetime_naive | Datetime with no timezone information (flexible formats) | datetime | temp, type | 1 | False | `2021-06-22 10:20:10` |
| datetime_rfc822 | Datetime in the RFC822 format | datetime | temp, type | 1 | False | `Sun, 06 Nov 1994 08:49:37 GMT` |
| departement | French département name | string | fr, geo | 0.9 | False | `essonne` |
| email | Email | string |  | 0.9 | False | `cdo_intern@data.gouv.fr` |
| float | Float number (with a dot or a comma as decimal separator) | float | type | 1 | False | `1` |
| geojson | JSON object in the [GeoJSON](https://fr.wikipedia.org/wiki/GeoJSON) format | json | geo | 1 | False | `{"coordinates": [45.783753, 3.049342], "type": "63870"}` |
| id_rnb | Building identifier from the French national building reference source ([RNB](https://rnb.beta.gouv.fr/definition)) | string | fr, geo | 1 | True | `FT4RKBXBVH9S` |
| insee_ape700 | French acitvity code from the INSEE reference source (APE) | string | fr | 0.8 | False | `0116Z` |
| insee_canton | French canton name | string | fr, geo | 0.9 | False | `nantua` |
| int | Integer | int |  | 1 | False | `1` |
| iso_country_code_alpha2 | [ISO alpha 2](https://fr.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code | string | geo | 1 | False | `FR` |
| iso_country_code_alpha3 | [ISO alpha 3](https://fr.wikipedia.org/wiki/ISO_3166-1) country code | string | geo | 1 | False | `FRA` |
| iso_country_code_numeric | [ISO numeric](https://fr.wikipedia.org/wiki/ISO_3166-1) country code | string | geo | 1 | False | `250` |
| jour_de_la_semaine | Weekday name in French | string | fr, temp | 0.8 | False | `lundi` |
| json | JSON object | json | type | 1 | False | `{"pomme": "fruit", "reponse": 42}` |
| latitude_l93 | Latitude in the Lambert 93 format | float | fr, geo | 1 | True | `6037008` |
| latitude_wgs | Latitude in the WGS format | float | geo | 1 | True | `43.2872` |
| latitude_wgs_fr_metropole | Latitude within the French metropole bounds in the WGS format | float | fr, geo | 1 | True | `42.576` |
| latlon_wgs | Latitude and longitude pair in the WGS format | string | geo | 1 | True | `43.2,-22.6` |
| longitude_l93 | Longitude in the Lambert 93 format | float | fr, geo | 1 | True | `0` |
| longitude_wgs | Longitude in the WGS format | float | geo | 1 | True | `120.8263` |
| longitude_wgs_fr_metropole | Longitude within the French metropole bounds in the WGS format | float | fr, geo | 1 | True | `-2.01` |
| lonlat_wgs | Longitude and latitude pair in the WGS format | string | geo | 1 | True | `-22.6,43.012` |
| mois_de_lannee | Month name in French | string | fr, temp | 1 | False | `JUIN` |
| money | Money amount | string |  | 0.8 | False | `120€` |
| mongo_object_id | Mongo object identifier | string |  | 0.8 | False | `62320e50f981bc2b57bcc044` |
| pays | Country name in French | string | fr, geo | 0.6 | False | `france` |
| percent | Percentage | string |  | 0.8 | False | `120%` |
| region | French région name | string | fr, geo | 1 | False | `bretagne` |
| sexe | Gender label | string | fr | 1 | False | `femme` |
| siren | French business identifier, from the INSEE reference source (SIRENE) | string | fr | 0.9 | True | `552100554` |
| siret | French business establishment identifier, from the INSEE reference source (SIRENE) | string | fr | 0.8 | True | `13002526500013` |
| tel_fr | French phone number | string | fr | 0.7 | False | `0134643467` |
| uai | French educational struture identifier from the Ministry of education reference source (UAI) | string | fr | 0.8 | False | `0422170F` |
| url | Web URL | string |  | 1 | False | `www.data.gouv.fr` |
| username | Username | string |  | 1 | False | `@accueil1` |
| uuid | Universally unique identifier ([UUID](https://fr.wikipedia.org/wiki/Universally_unique_identifier)) | string |  | 0.8 | False | `884762be-51f3-44c3-b811-1e14c5d89262` |
| year | Year | int | temp | 1 | False | `2015` |
