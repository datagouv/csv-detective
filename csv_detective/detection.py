import random
random.seed(42)
import pandas as pd
from cchardet import UniversalDetector

def detect_ints_as_floats(table):
    '''Détecte les colonnes contenant des entiers possibles écrits sous forme de float'''
    regex = r'^[0-9]+\.0+$'
    res = table.apply(lambda serie: serie.str.match(regex).all() and any(serie.notnull()))
    return res.index[res]


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


def parse_table(the_file, encoding, sep, headers_row, num_rows):
    # Takes care of some problems
    for encoding in [encoding, 'ISO-8859-1', 'utf-8']:
        # TODO : modification systematique
        if encoding is None:
            continue

        if 'ISO-8859' in encoding:
            encoding = 'ISO-8859-1'

        the_file.seek(0)
        # skip random lines to extract `num_rows` randomly
        total_lines = sum(1 for line in the_file)
        if total_lines > num_rows + headers_row:
            skip = sorted(
                random.sample(
                    range(1, total_lines),
                    total_lines - num_rows
                )
            )
            # also skip headers
            if headers_row:
                skip += range(headers_row + 1)
        else:
            skip = headers_row

        try:
            the_file.seek(0)
            table = pd.read_csv(
                the_file,
                sep=sep,
                skiprows=skip,
                dtype='unicode',
                encoding=encoding
            )
            break
        except TypeError:
            print('Trying encoding : {encoding}'.format(encoding=encoding))
    else:
        print('  >> encoding not found')
        return None, total_lines

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
