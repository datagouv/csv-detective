# Analyse des Optimisations de Performance

## Problèmes identifiés

### 1. **CRITIQUE: `test_col_val` - `.sample().apply()` sur toute la série** ⚠️

**Fichier:** `csv_detective/parsing/columns.py:32-33`

**Problème:**
```python
def apply_test_func(serie: pd.Series, test_func: Callable, _range: int):
    return serie.sample(n=_range).apply(test_func)
```

**Ligne 43:** `result = apply_test_func(serie, test_func, ser_len).sum() / ser_len`

**Impact:** 
- Pour `test_almost_uniform_column` avec 10M de lignes, on fait:
  1. `.sample(n=10_000_000)` → O(n) pour créer un nouveau Series
  2. `.apply(test_func)` → O(n) pour appliquer la fonction sur chaque élément
  3. `.sum()` → O(n) pour sommer
- **Total: O(3n)** alors qu'on pourrait faire mieux

**Optimisation:**
```python
# Au lieu de sample puis apply, on peut:
# Option 1: Si limited_output=False, on n'a pas besoin de sample!
if not limited_output:
    # Appliquer directement sur toute la série
    result = serie.apply(test_func).sum() / len(serie)
    
# Option 2: Si on veut vraiment sample, utiliser vectorisation
# ou au moins éviter de créer un nouveau Series
if not limited_output:
    # Utiliser directement les valeurs sans créer un nouveau Series
    sampled_indices = serie.sample(n=ser_len, random_state=42).index
    result = serie.loc[sampled_indices].apply(test_func).sum() / ser_len
```

**Gain estimé:** 30-50% pour les gros fichiers

---

### 2. **CRITIQUE: `test_col` - `.apply()` sur toutes les colonnes pour chaque type** ⚠️

**Fichier:** `csv_detective/parsing/columns.py:98-107`

**Problème:**
```python
return_table.loc[name] = table.apply(
    lambda serie: test_col_val(serie, ...)
)
```

**Impact:**
- Pour chaque type de test (int, float, date, etc.), on itère sur **toutes les colonnes**
- Si on a 20 types de tests et 10 colonnes, on fait 200 itérations
- Chaque itération appelle `test_col_val` qui peut être lent

**Optimisation:**
```python
# Au lieu de apply qui cache une boucle, utiliser une boucle explicite
# qui permet d'arrêter tôt si nécessaire
for col in table.columns:
    return_table.loc[name, col] = test_col_val(
        table[col],
        attributes["func"],
        attributes["prop"],
        skipna=skipna,
        limited_output=limited_output,
        verbose=verbose,
    )
```

**Gain estimé:** 10-20% (meilleure cache locality, possibilité d'early exit)

---

### 3. **CRITIQUE: `test_col_val` - Double filtrage NaN inutile** ⚠️

**Fichier:** `csv_detective/parsing/columns.py:36-37`

**Problème:**
```python
if skipna:
    serie = serie[serie.notnull()]  # O(n) - crée un nouveau Series
ser_len = len(serie)
```

Puis dans `apply_test_func`:
```python
serie.sample(n=_range).apply(test_func)  # O(n) - crée encore un nouveau Series
```

**Impact:**
- Création de multiples copies de Series
- Si `skipna=True` et qu'il y a beaucoup de NaN, on crée un nouveau Series complet

**Optimisation:**
```python
# Utiliser directement les indices non-null
if skipna:
    non_null_mask = serie.notnull()
    non_null_indices = serie[non_null_mask].index
    ser_len = len(non_null_indices)
    if ser_len == 0:
        return 1.0 if skipna else 0.0
    # Utiliser directement les indices au lieu de créer un nouveau Series
    serie_to_test = serie.loc[non_null_indices]
else:
    serie_to_test = serie
    ser_len = len(serie)
```

**Gain estimé:** 5-15% pour les colonnes avec beaucoup de NaN

---

### 4. **MODÉRÉ: `test_col_chunks` - `.apply(axis=1)` pour hashing** ⚠️

**Fichier:** `csv_detective/parsing/columns.py:171, 209`

**Problème:**
```python
row_hashes_count = table.apply(lambda row: hash(tuple(row)), axis=1).value_counts()
```

**Impact:**
- `.apply(axis=1)` est **très lent** dans pandas (boucle Python pure)
- Pour chaque ligne, on crée un tuple, puis on hash
- Pour 10k lignes, c'est 10k appels Python

**Optimisation:**
```python
# Utiliser une approche vectorisée
def hash_rows_vectorized(df):
    # Convertir chaque ligne en tuple de manière plus efficace
    # ou utiliser une méthode de hash plus rapide
    return pd.Series(
        [hash(tuple(row)) for row in df.itertuples(index=False, name=None)],
        index=df.index
    ).value_counts()

# Ou encore mieux, utiliser une fonction C optimisée
import numpy as np
def hash_rows_fast(df):
    # Utiliser numpy pour hasher plus rapidement
    # ou utiliser pd.util.hash_pandas_object si disponible
    return pd.util.hash_pandas_object(df, index=False).value_counts()
```

**Gain estimé:** 50-80% pour le calcul de duplicates

---

### 5. **MODÉRÉ: `detect_continuous_variable` - Double `.apply()` imbriqué** ⚠️

**Fichier:** `csv_detective/detection/variables.py:45`

**Problème:**
```python
res = table.apply(lambda serie: check_threshold(serie.apply(parses_to_integer), continuous_th))
```

**Impact:**
- `.apply()` sur toutes les colonnes (boucle externe)
- Pour chaque colonne, `.apply(parses_to_integer)` (boucle interne)
- **O(n*m)** où n=colonnes, m=lignes

**Optimisation:**
```python
# Éviter le double apply
def detect_continuous_variable_optimized(table, continuous_th=0.9, verbose=False):
    if verbose:
        start = time()
        logging.info("Detecting continuous columns")
    
    res = pd.Series(index=table.columns, dtype=bool)
    for col in table.columns:
        # Appliquer parses_to_integer une seule fois
        types_series = table[col].apply(parses_to_integer)
        count = types_series.value_counts().to_dict()
        total_nb = len(types_series)
        nb_floats = count.get(float, 0)
        res[col] = (nb_floats / total_nb) >= continuous_th if total_nb > 0 else False
    
    if verbose:
        display_logs_depending_process_time(
            f"Detected {sum(res)} continuous columns in {round(time() - start, 3)}s",
            time() - start,
        )
    return res.index[res]
```

**Gain estimé:** 20-30%

---

### 6. **MODÉRÉ: `test_col_chunks` - `value_counts()` appelé plusieurs fois** ⚠️

**Fichier:** `csv_detective/parsing/columns.py:173, 213-215`

**Problème:**
```python
# Ligne 173: value_counts sur le premier chunk
col_values = {col: table[col].value_counts(dropna=False) for col in table.columns}

# Ligne 213-215: value_counts sur chaque batch
for col in batch.columns:
    col_values[col] = col_values[col].add(
        batch[col].value_counts(dropna=False),  # value_counts appelé à nouveau
        fill_value=0,
    )
```

**Impact:**
- `value_counts()` est O(n) - on le fait pour chaque colonne de chaque batch
- Pour un fichier avec 100 batches et 10 colonnes = 1000 appels à `value_counts()`

**Optimisation:**
- Déjà optimisé (on accumule les résultats)
- Mais on pourrait éviter de recalculer `value_counts()` si on a déjà les données

**Gain estimé:** Minimal (déjà optimisé)

---

### 7. **FAIBLE: `create_profile` - `.apply()` pour float_casting** ⚠️

**Fichier:** `csv_detective/output/profile.py:48, 62-64`

**Problème:**
```python
cast_col = table[c].apply(lambda x: float_casting(x) if isinstance(x, str) else pd.NA)
```

**Impact:**
- `.apply()` avec lambda est lent (boucle Python)
- Pour chaque valeur, on fait `isinstance(x, str)` puis `float_casting(x)`

**Optimisation:**
```python
# Utiliser pd.to_numeric avec errors='coerce' qui est vectorisé en C
cast_col = pd.to_numeric(table[c], errors='coerce')

# Ou si float_casting est nécessaire:
# Filtrer d'abord les strings, puis appliquer
mask = table[c].apply(lambda x: isinstance(x, str))
cast_col = table[c].copy()
cast_col.loc[mask] = table[c].loc[mask].apply(float_casting)
cast_col.loc[~mask] = pd.NA
```

**Gain estimé:** 10-20% pour les colonnes float

---

### 8. **FAIBLE: `parse_csv` - `.duplicated()` sur tout le DataFrame** ⚠️

**Fichier:** `csv_detective/parsing/csv.py:45`

**Problème:**
```python
nb_duplicates = len(table.loc[table.duplicated()])
```

**Impact:**
- `table.duplicated()` crée un mask booléen de toute la table (O(n))
- `table.loc[mask]` filtre (O(n))
- `len()` compte (O(n))

**Optimisation:**
```python
# Utiliser directement sum() sur le mask booléen
nb_duplicates = table.duplicated().sum()
```

**Gain estimé:** 5-10% (évite la création d'un nouveau DataFrame)

---

## Résumé des optimisations par priorité

### Priorité 1 (Impact élevé, facile à implémenter)
1. ✅ **`test_col_val` - Éviter `.sample()` inutile quand `limited_output=False`**
   - Gain: 30-50%
   - Complexité: Faible
   
2. ✅ **`parse_csv` - Utiliser `.sum()` au lieu de `len(table.loc[mask])`**
   - Gain: 5-10%
   - Complexité: Très faible

### Priorité 2 (Impact élevé, complexité modérée)
3. ✅ **`test_col_chunks` - Optimiser le hashing des lignes**
   - Gain: 50-80%
   - Complexité: Modérée

4. ✅ **`test_col_val` - Éviter les copies inutiles de Series**
   - Gain: 5-15%
   - Complexité: Faible

5. ✅ **`detect_continuous_variable` - Éviter double `.apply()`**
   - Gain: 20-30%
   - Complexité: Faible

### Priorité 3 (Impact modéré)
6. ✅ **`test_col` - Remplacer `.apply()` par boucle explicite**
   - Gain: 10-20%
   - Complexité: Très faible

7. ✅ **`create_profile` - Optimiser float_casting**
   - Gain: 10-20%
   - Complexité: Modérée

## Estimation totale

**Gain total estimé:** 40-60% de réduction du temps d'exécution pour les gros fichiers

**Temps estimé pour implémenter:** 2-4 heures

## Tests à vérifier après optimisation

1. `test_almost_uniform_column` - devrait passer de ~45s à ~15-25s
2. Tous les autres tests doivent toujours passer
3. Vérifier que les résultats sont identiques

