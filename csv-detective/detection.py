import pandas as pd
from cchardet import UniversalDetector
from ast import literal_eval

def detect_ints_as_floats(table):
    '''Détecte les colonnes contenant des entiers possibles écrits sous forme de float'''
    regex = r'^[0-9]+\.0+$'
    res = table.apply(lambda serie: serie.str.match(regex).all() and any(serie.notnull()))
    return res.index[res]


def detect_continuous_variable(table, continuous_th=0.9):
    """
    Detects whether a column contains continuous variables. We consider a continuous column one that contains
    a considerable amount of float values.
    We removed the integers as we then end up with postal codes, insee codes, and all sort of codes and types.
    This is not optimal but it will do for now.
    :param table:
    :return:
    """

    def check_threshold(serie, continuous_th):
        count = serie.value_counts().to_dict()
        total_nb = len(serie)
        if float in count:
            nb_floats = count[float]
        else:
            return False
        if nb_floats / total_nb >= continuous_th:
            return True
        else:
            return False


    def parses_to_integer(value):
        try:
            value = value.replace(',', '.')
            value = literal_eval(value)
            return type(value)

        except:
            return False
    res = table.apply(lambda serie: check_threshold(serie.apply(parses_to_integer), continuous_th))
    return res.index[res]


def detetect_categorical_variable(table, threshold_pct_categorical=0.05, max_number_categorical_values=25):
    """
    Heuristically detects whether a table (df) contains categorical values according to
    the number of unique values contained.
    As the idea of detecting categorical values is to then try to learn models to predict them, we limit
    categorical values to at most 25 different modes. Postal code, insee code, code region and so on, may be thus not
    considered categorical values.
    :param table:
    :param threshold_pct_categorical:
    :param max_number_categorical_values:
    :return:
    """
    def abs_number_different_values(column_values):
        return len(column_values.unique())

    def rel_number_different_values(column_values):
        return len(column_values.unique()) / len(column_values)

    def detect_categorical(column_values):
        is_categorical = False
        abs_unique_values = abs_number_different_values(column_values)
        rel_unique_values = rel_number_different_values(column_values)
        if abs_unique_values < max_number_categorical_values:
            if rel_unique_values < threshold_pct_categorical:
                is_categorical = True
        return is_categorical

    res = table.apply(lambda serie: detect_categorical(serie))
    return res.index[res], res


def detect_separator(file):
    '''Detects csv separator'''
    # TODO: add a robust detection:
    # si on a un point virgule comme texte et \t comme séparateur, on renvoit
    # pour l'instant un point virgule
    file.seek(0)
    header = file.readline()
    possible_separators = [";", ",", "|", "\t"]
    sep_count = dict()
    for sep in possible_separators:
        sep_count[sep] = header.count(sep)
    return max(sep_count, key = sep_count.get)


def detect_encoding(the_file):
    '''Detects file encoding using chardet based on N first lines
    '''
    detector = UniversalDetector()
    for line in the_file.readlines():
        detector.feed(line)
        if detector.done:
            break
    detector.close()

    return detector.result


def parse_table(the_file, encoding, sep, num_rows, random_state=42):
    # Takes care of some problems
    table = None

    if not isinstance(the_file, str):
        the_file.seek(0)

    total_lines = None
    for encoding in [encoding, 'ISO-8859-1', 'utf-8']:
        # TODO : modification systematique
        if encoding is None:
            continue

        if 'ISO-8859' in encoding:
            encoding = 'ISO-8859-1'
        try:
            table = pd.read_csv(
                the_file,
                sep=sep,
                dtype='unicode',
                encoding=encoding
            )
            total_lines = len(table)
            num_rows = min(num_rows - 1, total_lines)
            table = table.sample(num_rows, random_state=random_state)
            break
        except TypeError:
            print('Trying encoding : {encoding}'.format(encoding=encoding))

    if table is None:
        print('  >> encoding not found')
        return table, "NA"

    return table, total_lines


def detect_extra_columns(file, sep):
    ''' regarde s'il y a des colonnes en trop
        Attention, file ne doit pas avoir de ligne vide '''
    file.seek(0)
    retour = False
    nb_useless_col = 99999

    for i in range(10):
        line = file.readline()
        # regarde si on a un retour
        if retour:
            assert line[-1] == "\n"
        if line[-1] == "\n":
            retour = True

        # regarde le nombre de derniere colonne inutile
        deb = 0 + retour
        line = line[::-1][deb:]
        k = 0
        for sign in line:
            if sign != sep:
                break
            k += 1
        if k == 0:
            return 0, retour
        nb_useless_col = min(k, nb_useless_col)
    return nb_useless_col, retour


def detect_headers(file, sep):
    ''' Tests 10 first rows for possible header (header not in 1st line)'''
    file.seek(0)
    for i in range(10):
        header = file.readline()
        chaine = [c for c in header.replace('\n', '').split(sep) if c]
        if (chaine[-1] not in ['', '\n'] and
             all([mot not in ['', '\n'] for mot in chaine[1:-1]])):
            return i, chaine
    return 0,  None


def detect_heading_columns(file, sep):
    ''' Tests first 10 lines to see if there are empty heading columns'''
    file.seek(0)
    return_int = float('Inf')
    for i in range(10):
        line = file.readline()
        return_int = min(return_int, len(line) - len(line.strip(sep)))
        if return_int == 0:
            return 0
    return return_int


def detect_trailing_columns(file, sep, heading_columns):
    ''' Tests first 10 lines to see if there are empty trailing columns'''
    file.seek(0)
    return_int = float('Inf')
    for i in range(10):
        line = file.readline()
        return_int = min(return_int, len(line.replace('\n', '')) - len(line.replace('\n', '').strip(sep)) - heading_columns)
        if return_int == 0:
            return 0
    return return_int
