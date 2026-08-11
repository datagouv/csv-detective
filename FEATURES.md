# csv-detective — Cahier des charges fonctionnel

Outil d'analyse automatique de fichiers tabulaires. Détecte l'encodage, le séparateur, le type de chaque colonne et produit un rapport structuré.

---

## 0. API publique

Trois fonctions publiques :

- **`routine(file_path, ...)`** : analyse complète d'un fichier. Point d'entrée principal.
- **`validate(file_path, previous_analysis, ...)`** : vérifie qu'un fichier est toujours conforme à une analyse précédente. Retourne `(is_valid, analysis, col_values)`.
- **`validate_then_detect(file_path, previous_analysis, ...)`** : valide d'abord, relance une analyse complète si la validation échoue.

### Paramètres communs

| Paramètre | Type | Défaut | Description |
|---|---|---|---|
| `file_path` | `str` | requis | Chemin local ou URL du fichier |
| `num_rows` | `int` | `500` | Nombre de lignes à échantillonner (-1 = tout le fichier) |
| `tags` | `list[str] \| None` | `None` | Filtrer les formats par tags (ex: `["geo", "fr"]`) |
| `limited_output` | `bool` | `True` | `True` = un seul format par colonne, `False` = tous les formats détectés |
| `save_results` | `bool \| str` | `True` | Sauvegarder en JSON (`True` = à côté du fichier, `str` = chemin custom) |
| `encoding` | `str \| None` | `None` | Forcer l'encodage (sinon auto-détecté) |
| `sep` | `str \| None` | `None` | Forcer le séparateur (sinon auto-détecté) |
| `skipna` | `bool` | `True` | Ignorer les NaN dans les tests |
| `output_profile` | `bool` | `False` | Ajouter un profil statistique (requiert `num_rows=-1`) |
| `output_schema` | `bool` | `False` | Ajouter un schéma Table Schema |
| `output_df` | `bool` | `False` | Retourner aussi le DataFrame casté |
| `cast_json` | `bool` | `True` | Caster les colonnes JSON en objets Python |
| `verbose` | `bool` | `False` | Logs détaillés |
| `sheet_name` | `str \| int \| None` | `None` | Feuille à lire pour les fichiers Excel |
| `custom_proportions` | `float \| int \| dict \| None` | `None` | Surcharger les seuils de proportion |

### Retour

- Par défaut : `dict` (le rapport d'analyse).
- Si `output_df=True` : `tuple[dict, Iterator[pd.DataFrame]]`.

---

## 1. Entrée / Parsing

### 1.1 Formats de fichiers supportés

| Format | Extensions | Moteur |
|---|---|---|
| CSV | `.csv`, tout fichier texte | pandas `read_csv` |
| CSV compressé gzip | `.csv.gz`, détection MIME | décompression gzip puis CSV |
| Excel (nouveau) | `.xlsx`, `.xlsm`, `.xltx`, `.xltm` | openpyxl |
| Excel (ancien) | `.xls` | xlrd |
| OpenOffice | `.odf`, `.ods`, `.odt` | odf |

La détection du moteur se fait via le type MIME (`python-magic`) quand le fichier n'a pas d'extension `.csv` et qu'aucun séparateur/moteur n'est précisé. Mapping MIME :

| MIME | Moteur |
|---|---|
| `application/gzip`, `application/x-gzip` | gzip |
| `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | openpyxl |
| `application/vnd.ms-excel` | xlrd |
| `application/vnd.oasis.opendocument.spreadsheet` | odf |
| `application/zip` | openpyxl (fallback) |

### 1.2 Source du fichier

Le fichier peut être :
- un **chemin local**
- une **URL** (détection : commence par `http`). Le contenu est téléchargé via `requests.get` avec `allow_redirects=True`.

Pour la détection MIME sur une URL, seuls les 1024 premiers octets sont lus en streaming.

### 1.3 Détection de l'encodage

1. Essayer de décoder en **UTF-8**. Si ça fonctionne, l'encodage est UTF-8 (confiance 100%).
2. Sinon, utiliser **charset_normalizer** (`detect()`).
3. Si aucun encodage détecté → erreur.

L'utilisateur peut forcer l'encodage via le paramètre `encoding`.

### 1.4 Détection du séparateur

1. Lire la **première ligne** du fichier.
2. Compter les occurrences de chaque séparateur candidat : `;`, `,`, `|`, `\t`.
3. Le séparateur le plus fréquent gagne.
4. **Validation** : vérifier sur les 10 premières lignes (via `csv.reader`) que toutes ont le même nombre de champs. Sinon → erreur.

L'utilisateur peut forcer le séparateur via le paramètre `sep`.

### 1.5 Détection de la position du header

Pour les fichiers CSV : tester les 10 premières lignes. La position du header est la première ligne qui est **différente de la ligne suivante**. Si les 10 premières lignes sont toutes identiques → erreur.

Pour les fichiers Excel : si toutes les colonnes sont nommées `Unnamed:*`, parcourir les lignes depuis le début pour trouver la première ligne non entièrement vide, qui devient le header.

### 1.6 Détection des colonnes vides

- **Colonnes en tête (heading)** : sur les 10 premières lignes, compter combien de séparateurs consécutifs en début de ligne.
- **Colonnes en queue (trailing)** : idem en fin de ligne.

### 1.7 Lecture Excel multi-feuilles

Quand aucune feuille n'est spécifiée (`sheet_name=None`), la **feuille la plus grande** (lignes × colonnes) est sélectionnée automatiquement.

Fallback : si xlrd échoue à lire un fichier `.xls` (erreur `XLRDError`), le moteur bascule automatiquement sur `odf` (OpenDocument).

### 1.8 Échantillonnage

- Le fichier est lu en entier jusqu'à `CHUNK_SIZE` lignes (10 000).
- Si le fichier fait ≤ 10 000 lignes, un échantillon aléatoire de `num_rows` (défaut 500) est prélevé avec `random_state=42`.
- Si le fichier dépasse 10 000 lignes, il passe en mode **chunks** (voir section 3.3).
- `num_rows=-1` → analyser toutes les lignes (requis pour le profil).

Toutes les colonnes sont lues en `dtype=str` (aucun casting automatique par pandas).

### 1.9 Validation post-lecture

Après lecture, si une colonne a un nom qui commence par `Unnamed:` ou n'est pas une chaîne → erreur "Could not accurately detect the file's columns".

Si la table est vide → erreur "Table seems to be empty".

---

## 2. Détection des formats

### 2.1 Principe général

Chaque format est défini par :
- **`_is(val) -> bool`** : fonction de test sur une valeur individuelle (string).
- **`proportion`** : seuil de tolérance (0 < p ≤ 1). Une colonne est considérée comme ce format si au moins `proportion` % des valeurs passent le test.
- **`labels`** : dictionnaire `{nom_header: crédibilité}` pour le scoring du nom de colonne.
- **`tags`** : liste de tags pour filtrer les formats (`fr`, `geo`, `temp`, `type`).
- **`mandatory_label`** : si `True`, la colonne ne peut être détectée que si le nom de la colonne match aussi.
- **`python_type`** : type Python associé (`string`, `int`, `float`, `bool`, `date`, `datetime`, `json`, `binary`).

### 2.2 Scoring

Le score final d'une colonne pour un format est calculé en 3 étapes :

1. **Score des valeurs (`columns_fields`)** : proportion des valeurs de la colonne qui passent le test `_is()`.
   - Si `proportion < 1`, le score est la proportion réelle si elle dépasse le seuil, sinon 0.
   - Si `proportion == 1` en mode `limited_output`, optimisation avec early stops (test sur 1 puis 5 valeurs aléatoires avant le test complet).
   - Le test est fait sur les **valeurs uniques** pondérées par leur fréquence d'apparition.

2. **Score des labels (`columns_labels`)** : le nom de la colonne est normalisé (minuscules, accents supprimés, camelCase splitté, caractères spéciaux remplacés par des espaces) puis comparé aux labels du format.
   - Match exact → crédibilité du label.
   - Match partiel (un mot du label contenu dans le header, si le mot fait > 2 caractères) → 0.5 × crédibilité.

3. **Score combiné (`columns`)** : `score_fields × (1 + score_labels / 2)`.
   - Score max possible : 1.5 (100% des valeurs valides + match exact du label).

### 2.3 Labels obligatoires (`mandatory_label`)

Pour certains formats à fort risque de faux positifs, le score combiné est mis à **zéro** si le score du label est 0. Formats concernés :
- `code_postal`
- `code_commune`
- `code_departement`
- `code_region`
- `code_epci`
- `code_fantoir`
- `siren`
- `siret`
- `id_rnb`
- `latitude_wgs`, `longitude_wgs`
- `latitude_wgs_fr_metropole`, `longitude_wgs_fr_metropole`
- `latitude_l93`, `longitude_l93`
- `latlon_wgs`, `lonlat_wgs`

### 2.4 Règles de priorité entre formats

Quand plusieurs formats sont détectés pour une même colonne, les règles de priorité suivantes s'appliquent :

- **`int` et `float` sont toujours déprioritisés** si un autre format est aussi détecté.
- **`int` < `float`** : si `int` est détecté, `float` est supprimé.
- **`booleen` > coordonnées** : bool supprime latitude/longitude (tous systèmes).
- **`geojson` > `json`**
- **`latlon_wgs` > `lonlat_wgs` et `json`**
- **`lonlat_wgs` > `json`**
- **`latitude_wgs_fr_metropole` > `latitude_l93` et `latitude_wgs`**
- **`longitude_wgs_fr_metropole` > `longitude_l93` et `longitude_wgs`**
- **`latitude_wgs` > `latitude_l93`**
- **`longitude_wgs` > `longitude_l93`**
- **`code_region` > `code_departement`**
- **`datetime_rfc822` > `datetime_aware`**
- **`code_epci` > `siren`**

La déprioritisation s'applique si le format prioritaire a un score ≥ au secondaire OU si le score prioritaire est ≥ 1.

En mode `limited_output`, seul le format avec le **meilleur score** est retenu. Si aucun format n'est détecté, le type par défaut est `string` avec un score de 1.0.

### 2.5 Colonnes vides

Si une colonne a un score de 1.0 pour **tous** les formats (ce qui arrive quand elle est entièrement vide/NaN), tous les scores sont mis à 0.

### 2.6 `skipna`

Par défaut (`skipna=True`), les valeurs `NaN` sont ignorées lors des tests. Une colonne 100% NaN score 1.0 en mode skipna, 0.0 sinon.

### 2.7 `custom_proportions`

Permet de surcharger les seuils de proportion :
- Un `float` ou `int` : appliqué à tous les formats.
- Un `dict[str, float]` : seuil spécifique par format (les formats non listés gardent leur valeur par défaut).

---

## 3. Formats détectés

### 3.1 Types de base

#### `int` — Entier
- proportion : 1
- python_type : `int`
- tags : aucun (bug : le module déclare `tag` au singulier au lieu de `tags`, donc non pris en compte par le système de filtrage)
- Règle : doit parser en `int` Python. **Rejeté si** : contient `.`, `_`, `+`, commence par `0` (sauf `"0"` seul), ou ≥ 20 caractères.
- Valide : `"1"`, `"0"`, `"1764"`, `"-24"`
- Invalide : `"01053"`, `"1.2"`, `"123_456"`, `"+35"`, `"14292405299487610865"`

#### `float` — Nombre flottant
- proportion : 1
- python_type : `float`
- tags : `type`
- Accepte la **virgule comme séparateur décimal** (remplacée par `.` avant parsing).
- Accepte la **notation scientifique** : pattern `^-?\d+\.\d+[eE][+-]?\d+$` uniquement.
- **Rejeté si** : contient `_`, commence par `0` suivi d'un caractère autre que `.` ou `,`, contient `+`/`e`/`E` sans matcher la notation scientifique, ou est un entier pur ≥ 20 caractères.
- Note : `"inf"` et `"nan"` sont actuellement acceptés.
- Valide : `"1.2"`, `"1,4292"`, `"1.9764E-1"`, `"-9.1e-9"`
- Invalide : `"01053"`, `"1e3"`, `"123_456"`, `"+35"`

#### `booleen` — Booléen
- proportion : 1
- python_type : `bool`
- tags : `type`
- Valeurs acceptées (insensible à la casse) : `1`, `0`, `vrai`, `faux`, `true`, `false`, `oui`, `non`, `yes`, `no`, `y`, `n`, `o`
- Mapping de casting : `1`→true, `0`→false, `vrai`→true, `faux`→false, `true`→true, `false`→false, `oui`→true, `non`→false, `yes`→true, `no`→false, `y`→true, `n`→false, `o`→true

#### `binary` — Données binaires
- proportion : 1
- python_type : `binary`
- tags : `type`
- Reconnaît les chaînes Python de bytes : commence par `b'` et finit par `'`, ou commence par `b"` et finit par `"`.
- Le contenu est validé via `codecs.escape_decode`.

#### `json` — Objet JSON
- proportion : 1
- python_type : `json`
- tags : `type`
- Doit parser en JSON **et** être un `list` ou `dict` (les scalaires comme `5` sont rejetés).

#### `percent` — Pourcentage
- proportion : 0.8
- tags : aucun
- Dernier caractère = `%`, et la partie avant est un `float` valide.
- Valide : `"120%"`, `"-20.2%"`

#### `money` — Montant monétaire
- proportion : 0.8
- tags : aucun
- Dernier caractère ∈ `{€, $, £, ¥}`, et la partie avant est un `float` valide.
- Valide : `"120€"`, `"-20.2$"`

### 3.2 Dates et temps

#### `date` — Date (formats flexibles)
- proportion : 1
- python_type : `date`
- tags : `temp`, `type`
- Longueur : entre 8 et 20 caractères.
- Séparateurs reconnus dans les patterns : espace, `/`, `-`, `*`, `_`, `|`, `;`, `.`, `,`
- **Pattern JJ-MM-AAAA** : `(0[1-9]|[12][0-9]|3[01])SEP(0[1-9]|1[0-2])SEP((19|20)\d{2})` — séparateur obligatoire.
- **Pattern AAAA-MM-JJ** : `((19|20)\d{2})SEP(0[1-9]|1[0-2])SEP(0[1-9]|[12][0-9]|3[01])` — séparateur optionnel (accepte `20030502`).
- **Pattern mois en texte** : `(0[1-9]|[12][0-9]|3[01])SEP(jan|fev|feb|mar|avr|apr|mai|may|jun|jui|jul|aou|aug|sep|oct|nov|dec|janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)SEP([0-9]{2}|(19|20)[0-9]{2})` — insensible à la casse, séparateur optionnel.
- **Fallback** : si aucun pattern ne matche, un seuil de 30% de caractères numériques est requis, puis parsing via `dateutil.parser.parse` avec fallback sur `dateparser.parse`. Le résultat est rejeté si l'heure/minute/seconde est non nulle (→ c'est un datetime, pas une date).
- Les **floats** (pattern `^-?\d+[\.|,]\d+$`) sont explicitement exclus.
- Les **timestamps Unix** (entiers purs) sont exclus car leur longueur est < 8 ou ce sont des ints.
- Valide : `"1960-08-07"`, `"12/02/2007"`, `"15 jan 1985"`, `"15 décembre 1985"`, `"20030502"`, `"2003.05.02"`
- Invalide : `"39-10-1993"`, `"15 tambour 1985"`, `"12152003"`, `"6.27367393749392839"`

#### `date_fr` — Date en texte français
- proportion : 1
- tags : `fr`, `temp`
- Pattern : `^(0?[1-9]|[12][0-9]|3[01])[ \-/](janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)[ \-/]\d{4}$` — appliqué sur la valeur normalisée (accents supprimés, minuscules).
- Valide : `"13 février 1996"`, `"15 decembre 2024"`

#### `datetime_aware` — Datetime avec fuseau horaire
- proportion : 1
- python_type : `datetime`
- tags : `temp`, `type`
- Longueur : entre 16 et 35 caractères.
- Doit commencer par `^\d{2}[-/:]?\d{2}` (préfixe de sécurité anti faux-positifs).
- **Pattern principal** : date AAAA-MM-JJ suivie de `T` ou espace, puis `HH:MM:SS(.dddddd)` puis timezone (`+HH:MM`, `-HH:MM`, ou `Z`).
- **Fallback** : seuil de 70% de caractères pertinents (chiffres, `-`, `/`, `:`, espace), puis parsing via dateutil/dateparser. Le résultat doit avoir une heure/minute/seconde non nulle ET un `tzinfo`.
- Valide : `"2021-06-22 10:20:10-04:00"`, `"2000-12-21 10:20:10.1Z"`, `"1996/06/22 10:20:10 GMT"`

#### `datetime_naive` — Datetime sans fuseau horaire
- proportion : 1
- python_type : `datetime`
- tags : `temp`, `type`
- labels : hérités de `datetime_aware` (les mêmes labels date + `datetime`, `timestamp`)
- Longueur : entre 15 et 30 caractères.
- Même préfixe de sécurité que datetime_aware.
- **Pattern principal** : date AAAA-MM-JJ suivie de `T` ou espace, puis `HH:MM:SS(.dddddd)`, **sans** timezone.
- **Fallback** : même logique que datetime_aware mais le résultat NE doit PAS avoir de `tzinfo`.
- Valide : `"2021-06-22 10:20:10"`, `"2030/06/22 00:00:00.0028"`
- Invalide : `"1999-12-01T00:00:00Z"`, `"Sun, 06 Nov 1994 08:49:37 GMT"`

#### `datetime_rfc822` — Datetime RFC 822
- proportion : 1
- python_type : `datetime`
- tags : `temp`, `type`
- labels : hérités de `datetime_aware`
- Pattern exact (insensible à la casse) : `^(mon|tue|wed|thu|fri|sat|sun), (0[1-9]|[1-2][0-9]|3[01]) (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) \d{4} ([01][0-9]|2[0-3]):([0-5])([0-9]):([0-5])([0-9]) (ut|gmt|est|edt|cst|cdt|mst|mdt|pst|pdt|[+\-](0[0-9]|1[0-3])00)$`
- Valide : `"Sun, 06 Nov 1994 08:49:37 GMT"`, `"Mon, 24 Feb 2010 23:00:37 +1000"`

#### `year` — Année
- proportion : 1
- python_type : `int`
- tags : `temp`
- Valeur entière entre **1800 et 2100** inclus.

#### `mois_de_lannee` — Mois de l'année (français)
- proportion : 1
- tags : `fr`, `temp`
- Valeurs acceptées (après normalisation unicode et minuscules) : `janvier`, `fevrier`, `mars`, `avril`, `mai`, `juin`, `juillet`, `aout`, `septembre`, `octobre`, `novembre`, `decembre`, `jan`, `fev`, `mar`, `avr`, `mai`, `jun`, `jui`, `juil`, `aou`, `sep`, `sept`, `oct`, `nov`, `dec`

#### `jour_de_la_semaine` — Jour de la semaine (français)
- proportion : 0.8
- tags : `fr`, `temp`
- Valeurs acceptées (minuscules) : `lundi`, `mardi`, `mercredi`, `jeudi`, `vendredi`, `samedi`, `dimanche`, `lun`, `mar`, `mer`, `jeu`, `ven`, `sam`, `dim`

### 3.3 Identifiants et codes web

#### `email` — Adresse email
- proportion : 0.9
- tags : aucun
- Pattern : `^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$` (insensible à la casse)

#### `url` — URL web
- proportion : 1
- tags : aucun
- Pattern : `^((https?|ftp)://|www\.)(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})(/[...]*)?$`
- Supporte les caractères accentués et les espaces dans le chemin.
- Valide : `"www.data.gouv.fr"`, `"https://une-ville.fr/délibérations/2025/Doc avec espaces.pdf"`

#### `uuid` — UUID
- proportion : 0.8
- tags : aucun
- Pattern : `^[{]?[0-9a-fA-F]{8}-?([0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}[}]?$`
- Accepte les accolades optionnelles et les tirets optionnels.

#### `mongo_object_id` — ID MongoDB
- proportion : 0.8
- tags : aucun
- Pattern : `^[0-9a-fA-F]{24}$`

#### `username` — Nom d'utilisateur
- proportion : 1
- tags : aucun
- Pattern : `^@[A-Za-z0-9_]+$`

### 3.4 Géographie

#### `latitude_wgs` — Latitude WGS84
- proportion : 1, mandatory_label : true
- python_type : `float`
- tags : `geo`
- Doit être un float valide, compris entre -90 et 90, et **ne pas être un entier** (pour éviter les codes postaux etc.).

#### `longitude_wgs` — Longitude WGS84
- proportion : 1, mandatory_label : true
- python_type : `float`
- tags : `geo`
- Doit être un float valide, compris entre -180 et 180, et **ne pas être un entier**.

#### `latitude_wgs_fr_metropole` — Latitude WGS84 France métropolitaine
- proportion : 1, mandatory_label : true
- python_type : `float`
- tags : `fr`, `geo`
- labels : hérités de `latitude_wgs`
- Latitude WGS valide + comprise entre **41.3 et 51.3**.

#### `longitude_wgs_fr_metropole` — Longitude WGS84 France métropolitaine
- proportion : 1, mandatory_label : true
- python_type : `float`
- tags : `fr`, `geo`
- labels : hérités de `longitude_wgs`
- Longitude WGS valide + comprise entre **-5.5 et 9.8**.

#### `latitude_l93` — Latitude Lambert 93
- proportion : 1, mandatory_label : true
- python_type : `float`
- tags : `fr`, `geo`
- Doit être un float valide, validé par `frformat.LatitudeL93`.
- Accepte la virgule comme séparateur décimal.
- Valide : `"6037008"`, `"7123528.5"`, `"7124528,5"`

#### `longitude_l93` — Longitude Lambert 93
- proportion : 1, mandatory_label : true
- python_type : `float`
- tags : `fr`, `geo`
- Doit être un float valide, validé par `frformat.LongitudeL93`.
- Valide : `"0"`, `"-154"`, `"1265783,45"`

#### `latlon_wgs` — Paire latitude,longitude WGS84
- proportion : 1, mandatory_label : true
- tags : `geo`
- Format : `lat,lon` — exactement une virgule dans la chaîne. Chaque partie est validée comme latitude/longitude WGS.
- Supporte le format `[lat,lon]` (crochets optionnels, mais les deux doivent être présents).
- L'espace après la virgule dans la longitude est toléré.
- Valide : `"43.2,-22.6"`, `"[-40.791, 10.81]"`
- Invalide : `"1,2"` (ce sont des entiers), `"43, -23"` (la latitude `"43"` est un entier, pas un float)

#### `lonlat_wgs` — Paire longitude,latitude WGS84
- Même logique que `latlon_wgs` mais en ordre inversé (`lon,lat`).

#### `geojson` — GeoJSON
- proportion : 1
- python_type : `json`
- tags : `geo`
- Doit parser en JSON dict, avec soit `type` + `coordinates`, soit `geometry.coordinates`.

#### `iso_country_code_alpha2` — Code pays ISO alpha-2
- proportion : 1
- tags : `geo`
- Pattern : 2 lettres, doit être dans la liste de référence (fichier `data/iso_country_code_alpha2.txt`). Insensible à la casse.

#### `iso_country_code_alpha3` — Code pays ISO alpha-3
- proportion : 1
- tags : `geo`
- labels : hérités de `iso_country_code_alpha2`
- Pattern : 3 lettres, doit être dans la liste de référence. Insensible à la casse.

#### `iso_country_code_numeric` — Code pays ISO numérique
- proportion : 1
- tags : `geo`
- labels : hérités de `iso_country_code_alpha2`
- Pattern : exactement 3 chiffres, doit être dans la liste de référence.

### 3.5 Géographie française

Tous les formats ci-dessous utilisent la bibliothèque **frformat** avec `Millesime.LATEST` et des options de normalisation (insensible à la casse, accents ignorés, caractères non-alphanumériques remplacés par des espaces, espaces multiples ignorés).

#### `commune` — Nom de commune française
- proportion : 0.8
- tags : `fr`, `geo`
- Validé par `frformat.Commune`.

#### `departement` — Nom de département français
- proportion : 0.9
- tags : `fr`, `geo`
- Validé par `frformat.Departement`.

#### `region` — Nom de région française
- proportion : 1
- tags : `fr`, `geo`
- Validé par `frformat.Region` avec des **valeurs supplémentaires** pour les anciennes régions et abréviations : `alsace`, `aquitaine`, `ara`, `aura`, `auvergne`, `auvergne et rhone alpes`, `basse normandie`, `bfc`, `bourgogne`, `bourgogne et franche comte`, `centre`, `champagne ardenne`, `franche comte`, `ge`, `haute normandie`, `hdf`, `languedoc roussillon`, `limousin`, `lorraine`, `midi pyrenees`, `nord pas de calais`, `npdc`, `paca`, `picardie`, `poitou charentes`, `reunion`, `rhone alpes`.

#### `pays` — Nom de pays (en français)
- proportion : 0.6
- tags : `fr`, `geo`
- Validé par `frformat.Pays`.

#### `insee_canton` — Nom de canton
- proportion : 0.9
- tags : `fr`, `geo`
- Validé par `frformat.Canton`.

#### `code_postal` — Code postal français
- proportion : 0.9, mandatory_label : true
- tags : `fr`, `geo`
- Validé par `frformat.CodePostal`.

#### `code_commune` — Code commune INSEE
- proportion : 0.75, mandatory_label : true
- tags : `fr`, `geo`
- Validé par `frformat.CodeCommuneInsee`.

#### `code_departement` — Code département
- proportion : 1, mandatory_label : true
- tags : `fr`, `geo`
- Validé par `frformat.CodeDepartement`. Accepte `2A`, `2b` (insensible à la casse).

#### `code_region` — Code région
- proportion : 1, mandatory_label : true
- tags : `fr`, `geo`
- Validé par `frformat.CodeRegion`.

#### `code_epci` — Code EPCI
- proportion : 0.9, mandatory_label : true
- tags : `fr`, `geo`
- C'est un **SIREN qui commence par `2`**.

#### `code_fantoir` — Code FANTOIR
- proportion : 1, mandatory_label : true
- tags : `fr`, `geo`
- Validé par `frformat.CodeFantoir`.

### 3.6 Identifiants français

#### `siren` — Numéro SIREN
- proportion : 0.9, mandatory_label : true
- tags : `fr`
- 9 chiffres (les espaces sont supprimés avant test).
- **Validation par clé de Luhn** : pour chaque chiffre en alternant ×1 et ×2, sommer les chiffres du résultat. Le total modulo 10 doit être 0.

#### `siret` — Numéro SIRET
- proportion : 0.8, mandatory_label : true
- tags : `fr`
- 14 chiffres (les espaces sont supprimés avant test).
- **Double validation Luhn** : d'abord la clé SIREN (9 premiers chiffres), puis la clé SIRET (14 chiffres complets).

#### `code_rna` — Code RNA
- proportion : 0.9
- tags : `fr`
- Validé par `frformat.CodeRNA`.

#### `code_waldec` — Code WALDEC
- proportion : 0.9
- tags : `fr`
- Pattern : `^W\d[\dA-Z]\d{7}$`

#### `uai` — Code UAI (établissements scolaires)
- proportion : 0.8
- tags : `fr`
- 8 caractères. Pattern : `^(0[0-8][0-9]|09[0-5]|9[78][0-9]|[67]20)[0-9]{4}[A-Z]$`
- Les préfixes 0xx à 095, 97x, 98x, 620, 720 sont valides.

#### `id_rnb` — Identifiant RNB (bâtiment)
- proportion : 1, mandatory_label : true
- tags : `fr`, `geo`
- Validé par `frformat.IdRNB`.

#### `code_import` — Code d'importation
- proportion : 0.9
- tags : `fr`
- Pattern : `^(\d{3}[SP]\d{4,10}(.\w{1,3}\d{0,5})?|\d[A-Z0-9]\d[SP]\w(\w-?\w{0,2}\d{0,6})?)$`

#### `insee_ape700` — Code APE/NAF (activité)
- proportion : 0.8
- tags : `fr`
- La valeur normalisée (majuscules) doit être dans la liste de référence (fichier `data/insee_ape700.txt`).

#### `csp_insee` — Libellé CSP INSEE
- proportion : 1
- tags : `fr`
- La valeur normalisée doit être dans la liste de référence (fichier `data/csp_insee.txt`).

#### `code_csp_insee` — Code CSP INSEE
- proportion : 1
- tags : `fr`
- 4 caractères. Soit `^[123456][0-9]{2}[abcdefghijkl]$`, soit une des valeurs : `7100`, `7200`, `7400`, `7500`, `7700`, `7800`, `8100`, `8300`, `8400`, `8500`, `8600`.

### 3.7 Divers

#### `sexe` — Genre
- proportion : 1
- tags : `fr`
- Valeurs acceptées (après normalisation) : `homme`, `femme`, `h`, `f`, `m`, `masculin`, `feminin`

#### `tel_fr` — Numéro de téléphone français
- proportion : 0.7
- tags : `fr`
- Longueur minimale : 10 caractères.
- Les `.`, `-` et espaces sont supprimés avant test.
- Pattern : `^(0|\+33|0033)?[0-9]{9}$`

#### `adresse` — Adresse française
- proportion : 0.55
- tags : `fr`, `geo`
- Longueur max : 150 caractères.
- Après normalisation, la valeur doit contenir au moins un des mots-clés de voie (attention aux espaces finaux qui font partie du pattern) :
  - Formes longues : `aire `, `allee `, `avenue `, `base `, `boulevard `, `cami `, `carrefour `, `chemin `, `cheminement `, `chaussee `, `cite `, `clos `, `coin `, `corniche `, `cote `, `cour `, `cours `, `domaine `, `descente `, `ecart `, `esplanade `, `faubourg `, `gare `, `grande rue`, `hameau `, `halle `, `ilot `, `impasse `, `lieu dit`, `lotissement `, `marche `, `montee `, `parc `, `passage `, `place `, `plan `, `plaine `, `plateau `, `pont `, `port `, `promenade `, `parvis `, `quartier `, `quai `, `residence `, `ruelle `, `rocade `, `rond point`, `route `, `rue `, `square `, `tour `, `traverse `, `villa `, `village `, `voie `, `zone artisanale`, `zone d'amenagement concerte`, `zone d'amenagement differe`, `zone industrielle`, `zone `
  - Abréviations : `av `, `pl `, `bd `, `chs `, `dom `, `ham `, `ld `, `vlge `, `za `, `zac `, `zad `, `zi `, `fg `, `imp `, `mte`

---

## 4. Normalisation du texte pour les labels et certains formats

La fonction de normalisation applique dans l'ordre :
1. Split du camelCase en mots séparés par des espaces.
2. Passage en minuscules.
3. Remplacement des caractères accentués : `à/â→a`, `ç→c`, `é/è/ê/Ã©→e`, `î/ï→i`, `ô/ö→o`, `ù/û/ü→u`.
4. Remplacement de `-`, `_`, `'`, `,`, double espace par un espace simple.
5. Trim des espaces.

---

## 5. Gestion des gros fichiers (mode chunks)

Quand le fichier dépasse 10 000 lignes (CHUNK_SIZE), le traitement se fait en plusieurs passes :

1. **Premier chunk** (10 000 lignes) : analyse complète, donne un premier score par format/colonne.
2. **Chunks suivants** : regroupés par **batches de 10 chunks** (100 000 lignes) pour les performances. Pour chaque colonne, seuls les formats encore en lice (score > 0) sont testés.
3. **Early stop** : si un batch donne un score 0 pour un format sur une colonne, ce format est éliminé. Sinon, le score est mis à jour par **moyenne pondérée** : `(score_précédent × idx + score_batch) / (idx + 1)`.
4. **Stop global** : si plus aucun format n'est en compétition sur aucune colonne, l'itération s'arrête.
5. Les formats avec `mandatory_label` dont le label ne matche pas la colonne sont exclus des tests dès le départ (optimisation).

Les valeurs de chaque colonne sont accumulées (value_counts) au fil des chunks pour le profil.

---

## 6. Variables catégoriques et continues

### Variables catégoriques
Une colonne est catégorique si :
- ≤ 25 valeurs uniques **OU** ≤ 5% de valeurs uniques par rapport au total.

### Variables continues
(Actuellement désactivé dans le code mais implémenté) : une colonne est continue si ≥ 90% de ses valeurs parsent en float (les entiers seuls ne comptent pas). La virgule est traitée comme séparateur décimal.

---

## 7. Sortie

### 7.1 Structure du rapport (`analysis`)

```
{
  "encoding": "utf-8",                    // CSV uniquement
  "separator": ";",                        // CSV uniquement
  "heading_columns": 0,                   // CSV uniquement
  "trailing_columns": 0,                  // CSV uniquement
  "compression": "gzip",                  // si applicable
  "engine": "openpyxl",                   // Excel uniquement
  "sheet_name": "Feuil1",                 // Excel uniquement
  "header_row_idx": 0,
  "header": ["col1", "col2", ...],
  "total_lines": 1234,
  "nb_duplicates": 56,
  "categorical": ["col1", "col3"],

  // Résultats de détection par méthode
  "columns_fields": { ... },              // score basé sur les valeurs
  "columns_labels": { ... },              // score basé sur les noms de colonnes
  "columns": { ... },                     // score combiné (champs × labels)
  "formats": { "int": ["col1"], ... }     // index inversé (limited_output seulement)
}
```

En mode `limited_output=True`, chaque colonne dans `columns`/`columns_fields`/`columns_labels` contient :
```json
{
  "format": "siren",
  "score": 1.35,
  "python_type": "string"
}
```

En mode `limited_output=False`, c'est une **liste** de toutes les détections non nulles (après priorités) :
```json
[
  {"format": "siren", "score": 1.35, "python_type": "string"},
  {"format": "int", "score": 1.0, "python_type": "int"}
]
```

### 7.2 Sauvegarde JSON

Si `save_results=True`, le rapport est sauvegardé en JSON à côté du fichier source (même nom, extension `.json`). Si `save_results` est un chemin, il est utilisé directement. Pour les URLs, le nom du fichier est extrait. Pour les fichiers Excel, le nom de la feuille est ajouté au nom du fichier.

Les valeurs `NaN`, `Infinity` et `-Infinity` sont remplacées par `null` avant sérialisation.

### 7.3 Profil (`output_profile=True`)

Requiert `num_rows=-1`. Pour chaque colonne :
- **`tops`** : les 10 valeurs les plus fréquentes avec leur count.
- **`nb_distinct`** : nombre de valeurs uniques.
- **`nb_missing_values`** : nombre de valeurs manquantes.
- Si le type est `int` ou `float` : **`min`**, **`max`**, **`mean`**, **`std`** (écart-type).
  - Pour les floats, la virgule est traitée comme séparateur décimal.
  - Pour les ints, casting en `pd.Int64Dtype()` (supporte les NaN).

### 7.4 Table Schema (`output_schema=True`)

Génère un schéma au format [Frictionless Table Schema](https://specs.frictionlessdata.io/table-schema). Chaque champ contient :
- `name`, `description`, `example`, `type` (mapping vers les types Frictionless : `string`, `integer`, `number`, `boolean`, `date`, `datetime`, `year`, `geojson`, `geo_point`).
- `formatFR` : le nom du format csv-detective.
- `constraints` : `required: false` + pattern regex et/ou bornes min/max selon le format.

### 7.5 DataFrame casté (`output_df=True`)

Retourne un itérateur de DataFrames avec les colonnes castées selon le type détecté :
- `string` → pas de changement
- `int` → `pd.Int64Dtype()`
- `float` → casting via `float(val.replace(",", "."))`
- `bool` → mapping booléen (voir section booleen)
- `json` → `json.loads()` (sauf si `cast_json=False`)
- `date` → `datetime.date` via dateutil/dateparser
- `datetime` → `datetime.datetime` via dateutil/dateparser
- `binary` → `bytes` via `codecs.escape_decode`

Les valeurs dans `pd._libs.parsers.STR_NA_VALUES` sont castées en `None`.

Pour les gros fichiers (> CHUNK_SIZE), le DataFrame est retourné en chunks de 10 000 lignes.

---

## 8. Validation

### 8.1 `validate` (fonction publique)

Vérifie si un fichier est conforme à une analyse précédente. Retourne un triplet `(is_valid, analysis, col_values)`.

### 8.2 `validate_then_detect` (fonction publique)

Combinaison : valide d'abord, puis relance une analyse complète si la validation échoue.

### 8.3 Processus de validation :
1. Vérifier que tous les formats de l'analyse précédente existent dans la version courante.
2. Charger le fichier avec les paramètres de l'analyse précédente (encoding, séparateur, etc.).
3. Vérifier que les colonnes sont identiques (même nombre, mêmes noms, même ordre).
4. Pour chaque colonne non-`string`, tester les valeurs avec la fonction `_is` du format détecté.
   - Si `proportion == 1` et qu'un seul chunk contient une valeur invalide → **échec immédiat**.
   - Pour les formats avec `proportion < 1`, la proportion globale est calculée à la fin.
5. Les chunks de validation font 100 000 lignes (VALIDATION_CHUNK_SIZE, 10× plus gros que l'analyse, car le test est plus rapide).

Si la validation échoue (ou si le chargement échoue), `validate_then_detect` relance une analyse complète automatiquement.

---

## 9. Tags de filtrage

Les tags permettent de ne tester qu'un sous-ensemble de formats. Un format est inclus si **tous** les tags demandés sont dans ses tags. Tags disponibles :

| Tag | Formats concernés |
|---|---|
| `type` | int, float, booleen, binary, json, date, datetime_aware, datetime_naive, datetime_rfc822 |
| `temp` | date, date_fr, datetime_aware, datetime_naive, datetime_rfc822, year, mois_de_lannee, jour_de_la_semaine |
| `geo` | geojson, latitude/longitude (tous systèmes), latlon_wgs, lonlat_wgs, iso_country_code_*, commune, departement, region, pays, insee_canton, code_postal, code_commune, code_departement, code_region, code_epci, code_fantoir, adresse, id_rnb |
| `fr` | date_fr, mois_de_lannee, jour_de_la_semaine, sexe, tel_fr, adresse, commune, departement, region, pays, insee_canton, code_postal, code_commune, code_departement, code_region, code_epci, code_fantoir, siren, siret, code_rna, code_waldec, uai, id_rnb, code_import, insee_ape700, csp_insee, code_csp_insee, latitude/longitude_wgs_fr_metropole, latitude/longitude_l93 |

---

## 10. Labels complets par format

Les labels sont les noms de colonnes attendus, avec leur crédibilité (score entre 0 et 1). Chaque label est comparé au header normalisé.

| Format | Labels |
|---|---|
| `int` | `nb:0.75`, `nombre:1`, `nbre:0.75` |
| `float` | `part:1`, `ratio:1`, `taux:1` |
| `booleen` | `is :1`, `has :1`, `est :1` |
| `binary` | `bytes:1`, `binary:1`, `image:1`, `encode:1`, `content:1` |
| `json` | `list:1`, `dict:1`, `complex:1` |
| `percent` | `pourcent:1`, `part:0.75`, `pct:0.75` |
| `money` | `budget:1`, `salaire:1`, `euro:1`, `euros:1`, `prêt:1`, `montant:1` |
| `date` | `date:1`, `mise à jour:1`, `modifie:1`, `maj:0.75`, `datemaj:1`, `update:1`, `created:1`, `modified:1`, `jour:0.75`, `periode:0.75`, `dpc:0.5`, `yyyymmdd:1`, `aaaammjj:1` |
| `date_fr` | `date:1` |
| `datetime_aware` | `date:1`, `mise à jour:1`, `modifie:1`, `maj:0.75`, `datemaj:1`, `update:1`, `created:1`, `modified:1`, `datetime:1`, `timestamp:1` |
| `datetime_naive` | _(hérités de datetime_aware)_ |
| `datetime_rfc822` | _(hérités de datetime_aware)_ |
| `year` | `year:1`, `annee:1`, `naissance:1`, `exercice:1` |
| `mois_de_lannee` | `mois:1`, `month:1` |
| `jour_de_la_semaine` | `jour semaine:1`, `type jour:1`, `jour de la semaine:1`, `saufjour:1`, `nomjour:1`, `jour:0.75`, `jour de fermeture:1` |
| `email` | `email:1`, `mail:1`, `courriel:1`, `contact:1`, `mel:1`, `lieucourriel:1`, `coordinates.emailcontact:1`, `e mail:1`, `mo mail:1`, `adresse mail:1`, `adresse email:1` |
| `url` | `url:1`, `url source:1`, `site web:1`, `source url:1`, `site internet:1`, `remote url:1`, `web:1`, `site:1`, `lien:1`, `site data:1`, `lien url:1`, `lien vers le fichier:1`, `sitweb:1`, `interneturl:1` |
| `uuid` | `id:1`, `identifiant:1` |
| `mongo_object_id` | `id:1`, `objectid:1` |
| `username` | `account:1`, `username:1`, `user:0.75` |
| `sexe` | `sexe:1`, `sex:1`, `civilite:1`, `genre:1` |
| `tel_fr` | `telephone:1`, `tel:1`, `phone:1`, `num tel:1`, `tel mob:1` |
| `adresse` | `adresse:1`, `localisation:1`, `adresse postale:1`, `adresse geographique:1`, `adr:0.5`, `adresse complete:1`, `adresse station:1` |
| `commune` | `commune:1`, `ville:1`, `libelle commune:1` |
| `departement` | `departement:1`, `libelle du departement:1`, `deplib:1`, `nom dept:1`, `dept:0.75`, `libdepartement:1`, `nom departement:1`, `libelle dep:1`, `libelle departement:1`, `lb departements:1`, `dep libusage:1`, `lb departement:1`, `nom dep:1` |
| `region` | `region:1`, `libelle region:1`, `nom region:1`, `libelle reg:1`, `nom reg:1`, `reg libusage:1`, `nom de la region:1`, `regionorg:1`, `regionlieu:1`, `reg:0.5`, `nom officiel region:1` |
| `pays` | `pays:1`, `payslieu:1`, `paysorg:1`, `country:1`, `pays lib:1`, `lieupays:1`, `pays beneficiaire:1`, `nom du pays:1`, `libelle pays:1` |
| `insee_canton` | `insee canton:1`, `canton:1`, `cant:0.5`, `nom canton:1` |
| `code_postal` | `code postal:1`, `postal code:1`, `postcode:1`, `post code:1`, `cp:0.5`, `codes postaux:1`, `location postcode:1` |
| `code_commune` | `code commune insee:1`, `code insee:1`, `codes insee:1`, `code commune:1`, `code insee commune:1`, `insee:0.75`, `code com:1`, `com:0.5`, `code:0.5` |
| `code_departement` | `code departement:1`, `code_departement:1`, `dep:0.5`, `departement:1`, `dept:0.75` |
| `code_region` | `code region:1`, `reg:0.5`, `code insee region:1`, `region:1` |
| `code_epci` | `epci:1` |
| `code_fantoir` | `cadastre1:1`, `code fantoir:1`, `fantoir:1` |
| `siren` | `siren:1`, `n° siren:1`, `siren organisme:1`, `siren titulaire:1`, `numero siren:1`, `epci:0.9` |
| `siret` | `siret:1`, `num siret:1`, `siretacheteur:1`, `n° siret:1`, `coll siret:1`, `epci:1` |
| `code_rna` | `code rna:1`, `rna:1`, `n° inscription association:1`, `identifiant association:1`, `asso:0.75` |
| `code_waldec` | `code waldec:1`, `waldec:1` |
| `uai` | `uai:1`, `code etablissement:1`, `code uai:1`, `uai - identifiant:1`, `numero uai:1`, `rne:0.75`, `numero de l'etablissement:1`, `code rne:1`, `codeetab:1`, `code uai de l'etablissement:1`, `ref uai:1`, `cd rne:1`, `numerouai:1`, `numero d etablissement:1`, `numero etablissement:1` |
| `id_rnb` | `rnb:1`, `batid:1` |
| `code_import` | `code:0.5` |
| `insee_ape700` | `code ape:1`, `code activite (ape):1`, `code naf:1`, `code naf organisme designe:1`, `code naf organisme designant:1`, `base sirene : code ape de l'etablissement siege:1`, `naf:0.75`, `ape:0.5` |
| `csp_insee` | `csp insee:1`, `csp:0.75`, `categorie socioprofessionnelle:1`, `sociopro:1` |
| `code_csp_insee` | `code csp insee:1`, `code csp:1` |
| `latitude_wgs` | `latitude:1`, `lat:0.75`, `y:0.5`, `yf:0.5`, `yd:0.5`, `coordonnee y:1`, `coord y:1`, `ycoord:1`, `ylat:1`, `y gps:1`, `latitude wgs84:1`, `y wgs84:1`, `wsg:0.75`, `gps:0.5` |
| `longitude_wgs` | `longitude:1`, `long:0.75`, `lon:0.75`, `lng:0.5`, `x:0.5`, `xf:0.5`, `xd:0.5`, `coordonnee x:1`, `coord x:1`, `xcoord:1`, `xlon:1`, `xlong:1`, `x gps:1`, `longitude wgs84:1`, `x wgs84:1`, `wsg:0.75`, `gps:0.5` |
| `latitude_wgs_fr_metropole` | _(hérités de latitude_wgs)_ |
| `longitude_wgs_fr_metropole` | _(hérités de longitude_wgs)_ |
| `latitude_l93` | _(labels partagés de latitude_wgs)_ + `y l93:1`, `latitude lb93:1`, `lamby:1` |
| `longitude_l93` | _(labels partagés de longitude_wgs)_ + `x l93:1`, `longitude lb93:1`, `lambx:1` |
| `latlon_wgs` | `ban:1`, `coordinates:1`, `coordonnees:1`, `coordonnees insee:1`, `coord:1`, `geo:0.5`, `geopoint:1`, `geoloc:1`, `geolocalisation:1`, `geom:0.75`, `geometry:1`, `gps:1`, `localisation:1`, `point:1`, `position:1`, `wgs84:1`, `latlon:1`, `lat lon:1`, `x y:0.75`, `xy:0.75` + combinaisons de chaque label partagé avec chaque label spécifique |
| `lonlat_wgs` | mêmes labels partagés que `latlon_wgs` + `lonlat:1`, `lon lat:1`, `y x:0.75`, `yx:0.75` + combinaisons |
| `geojson` | `json geojson:1`, `json:1`, `geojson:1`, `geo shape:1`, `geom:0.75`, `geometry:1`, `geoshape:1` |
| `iso_country_code_alpha2` | `iso country code:1`, `code pays:1`, `pays:1`, `country:1`, `nation:1`, `pays code:1`, `code pays (iso):1`, `code:0.5` |
| `iso_country_code_alpha3` | _(hérités de iso_country_code_alpha2)_ |
| `iso_country_code_numeric` | _(hérités de iso_country_code_alpha2)_ |

---

## 11. Fichiers de données de référence

Les fichiers suivants dans `formats/data/` contiennent les listes de valeurs de référence :
- `insee_ape700.txt` : codes APE/NAF valides (un par ligne)
- `csp_insee.txt` : libellés CSP INSEE (un par ligne, normalisés)
- `iso_country_code_alpha2.txt` : codes pays ISO alpha-2
- `iso_country_code_alpha3.txt` : codes pays ISO alpha-3
- `iso_country_code_numeric.txt` : codes pays ISO numériques

Les formats utilisant **frformat** (commune, département, région, pays, canton, code postal, code commune, code département, code région, code fantoir, code RNA, id RNB, latitude/longitude L93) dépendent des données embarquées dans cette bibliothèque avec le millésime le plus récent (`Millesime.LATEST`).

---

## 12. Génération de fichiers d'exemple

La fonction `create_example_csv_file` peut générer un fichier CSV d'exemple à partir :
- D'une liste de champs avec leur type et arguments optionnels.
- D'un schéma Table Schema (local ou URL).

Types supportés : `str`, `int`, `float`, `date`, `time`, `datetime`, `url`, `id` (UUID), `bool`, `year`, `array`.

Les champs non requis ont 30% de chance d'être vides. Les patterns regex sont supportés via `rstr.xeger`.
