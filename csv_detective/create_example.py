import random
import uuid
import string
import pandas as pd
from typing import Dict, List, Literal, Union


def create_example_csv_file(
    fields: dict,
    file_length: int = 50,
    output_file: bool = True,
    output_name: str = 'example_file.csv',
    output_sep: str = ';'
) -> pd.DataFrame:
    '''
    Create an example file based on a list of dicts like follows:
    [
        {
            "name": "column_name",
            "type": "column_type",
            "args": {dict_of_args}
        },
        ...
    ]
    '''

    def make_random_string(length, seed=None):
        random.seed(seed)
        letters = string.ascii_lowercase
        res = ''.join(random.choice(letters) for i in range(length))
        random.seed(None)
        return res

    def make_random_id(seed=None):
        return uuid.uuid4()

    def get_random_from_list(the_list, seed=None):
        random.seed(seed)
        res = random.choice(the_list)
        random.seed(None)
        return res

    def make_random_date(
        date_range: Union[None, List[str]],
        date_format='DD-MM-YYYY',
        seed=None
    ):
        assert all([k in date_format for k in ['DD', 'MM', 'YYYY']])
        random.seed(seed)
        if date_range is None:
            dd = random.randint(1,28)
            mm = random.randint(1,12)
            yyyy = random.randint(1900,2100)
            return date_format \
                .replace('DD', f'{"0"*(2-len(str(dd))) + str(dd)}') \
                .replace('MM', f'{"0"*(2-len(str(mm))) + str(mm)}') \
                .replace('YYYY', f'{yyyy}')
        else:
            assert len(date_range) == 2
            start = {
                'DD': date_range[0][date_format.rfind('DD'):date_format.rfind('DD')+2],
                'MM': date_range[0][date_format.rfind('MM'):date_format.rfind('MM')+2],
                'YYYY': date_range[0][date_format.rfind('YYYY'):date_format.rfind('YYYY')+4],
            }
            end = {
                'DD': date_range[1][date_format.rfind('DD'):date_format.rfind('DD')+2],
                'MM': date_range[1][date_format.rfind('MM'):date_format.rfind('MM')+2],
                'YYYY': date_range[1][date_format.rfind('YYYY'):date_format.rfind('YYYY')+4],
            }

            dd = random.randint(int(start['DD']),int(end['DD']))
            mm = random.randint(int(start['MM']),int(end['MM']))
            yyyy = random.randint(int(start['YYYY']),int(end['YYYY']))

        return date_format \
            .replace('DD', f'{"0"*(2-len(str(dd))) + str(dd)}') \
            .replace('MM', f'{"0"*(2-len(str(mm))) + str(mm)}') \
            .replace('YYYY', f'{yyyy}')

    def make_random_url(length=10, seed=None):
        return 'http://'+make_random_string(length=length, seed=seed) + '.' + random.choice(['example'])

    def make_random_number(
        num_type: Union[int, float] = int,
        num_range: Union[None, List[float]] = None
    ):
        assert num_range is None or len(num_range) == 2
        if num_range is None:
            num_range = [0, 1000]
        if num_type == int:
            return random.randint(num_range[0], num_range[1])
        else:
            return round(random.uniform(num_range[0], num_range[1]), 1)

    types_to_func = {
        'int': make_random_number,
        'float': make_random_number,
        'date': make_random_date,
        'str': make_random_string,
        'url': make_random_url,
        'id': make_random_id,
    }

    for k in range(len(fields)):
        if fields[k]['type'] == 'float':
            fields[k]['args']['num_type'] = float
        elif fields[k]['type'] == 'int':
            fields[k]['args']['num_type'] = int

    output = pd.DataFrame(columns=[f["name"] for f in fields])
    # would it be better to create by column or by row (as for now)?
    for k in range(file_length):
        new = [
            types_to_func[f['type']](**f['args']) for f in fields
        ]
        output = pd.concat([output, pd.Series(new, index=output.columns).to_frame().T], axis=0)

    if output_file:
        output.to_csv(output_name, sep=output_sep, index=False)

    return output
