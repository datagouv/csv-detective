import random
import uuid
import string
import pandas as pd
from typing import List, Union
import json
import requests
import rstr


def create_example_csv_file(
    fields: Union[dict, None] = None,
    from_schema: bool = False,
    schema_path: Union[str, None] = None,
    file_length: int = 10,
    output_file: bool = True,
    output_name: str = 'example_file.csv',
    output_sep: str = ';',
    encoding: str = 'utf-8',
    ignore_required: bool = False,
) -> pd.DataFrame:
    '''
    Create an example file based on a list of dicts like follows:
    fields = [
        {
            "name": "column_name",
            "type": "column_type",
            "args": {dict_of_args}
        },
        ...
    ]
    Or from a TableSchema
    '''
    # need to make a CLI command

    assert isinstance(fields, list) or (from_schema and isinstance(schema_path, str))

    basic_year_range = [1900, 2100]

    def potential_skip(required):
        if ignore_required:
            return False
        if not required:
            return random.randint(0, 100) > 30

    def make_random_string(length=10, required=True, pattern=None, enum=None, seed=None):
        if potential_skip(required):
            return ''
        random.seed(seed)
        if pattern is not None:
            return rstr.xeger(pattern)
        elif enum is not None:
            return random.choice(enum)
        else:
            letters = string.ascii_lowercase
            return ''.join(random.choice(letters) for i in range(length))

    def make_random_id(required=True, seed=None):
        if potential_skip(required):
            return ''
        random.seed(seed)
        return uuid.uuid4()

    def make_random_date(
        date_range: Union[None, List[str]] = None,
        date_format='YYYY-MM-DD',
        required=True,
        seed=None
    ):
        if potential_skip(required):
            return ''
        # these need to change
        date_format = date_format.upper()
        assert all([k in date_format for k in ['DD', 'MM', 'YYYY']])
        random.seed(seed)
        if date_range is None:
            dd = random.randint(1, 28)
            mm = random.randint(1, 12)
            yyyy = random.randint(basic_year_range[0], basic_year_range[1])
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

            dd = random.randint(int(start['DD']), int(end['DD']))
            mm = random.randint(int(start['MM']), int(end['MM']))
            yyyy = random.randint(int(start['YYYY']), int(end['YYYY']))

        return date_format \
            .replace('DD', f'{"0"*(2-len(str(dd))) + str(dd)}') \
            .replace('MM', f'{"0"*(2-len(str(mm))) + str(mm)}') \
            .replace('YYYY', f'{yyyy}')

    def make_random_time(
        time_range: Union[None, List[str]] = None,
        time_format='HH-MM-SS',
        required=True,
        seed=None
    ):
        if potential_skip(required):
            return ''
        time_format = time_format.upper()
        assert all([k in time_format for k in ['HH', 'MM', 'SS']])
        random.seed(seed)
        if time_range is None:
            hh = random.randint(0, 23)
            mm = random.randint(0, 59)
            ss = random.randint(0, 59)
            return time_format \
                .replace('HH', f'{"0"*(2-len(str(hh))) + str(hh)}') \
                .replace('MM', f'{"0"*(2-len(str(mm))) + str(mm)}') \
                .replace('SS', f'{"0"*(2-len(str(ss))) + str(ss)}')
        else:
            assert len(time_range) == 2
            start = {
                'HH': time_range[0][time_format.rfind('HH'):time_format.rfind('HH')+2],
                'MM': time_range[0][time_format.rfind('MM'):time_format.rfind('MM')+2],
                'SS': time_range[0][time_format.rfind('SS'):time_format.rfind('SS')+2],
            }
            end = {
                'HH': time_range[1][time_format.rfind('HH'):time_format.rfind('HH')+2],
                'MM': time_range[1][time_format.rfind('MM'):time_format.rfind('MM')+2],
                'SS': time_range[1][time_format.rfind('SS'):time_format.rfind('SS')+2],
            }

            hh = random.randint(int(start['HH']), int(end['HH']))
            mm = random.randint(int(start['MM']), int(end['MM']))
            ss = random.randint(int(start['SS']), int(end['SS']))

        return time_format \
            .replace('HH', f'{"0"*(2-len(str(hh))) + str(hh)}') \
            .replace('MM', f'{"0"*(2-len(str(mm))) + str(mm)}') \
            .replace('SS', f'{"0"*(2-len(str(ss))) + str(ss)}')

    def make_random_datetime(
        time_range: Union[None, List[str]] = None,
        date_range: Union[None, List[str]] = None,
        time_format='HH-MM-SS',
        date_format='DD-MM-YYYY',
        required=True,
        seed=None
    ):
        if potential_skip(required):
            return ''
        random.seed(seed)
        return make_random_date(date_range=date_range, date_format=date_format, seed=seed) \
            + make_random_time(time_range=time_range, time_format=time_format, seed=seed) \
            + 'Z'

    def make_random_url(length=10, required=True, seed=None):
        if potential_skip(required):
            return ''
        random.seed(seed)
        return 'http://'+make_random_string(length=length, seed=seed) + '.' + random.choice(['example'])

    def make_random_number(
        num_type: Union[int, float] = int,
        num_range: Union[None, List[float]] = None,
        enum: Union[None, list] = None,
        required=True,
        seed=None
    ):
        if potential_skip(required):
            return ''
        assert num_range is None or len(num_range) == 2
        random.seed(seed)
        if enum:
            return random.choice(enum)
        if num_range is None:
            num_range = [0, 1000]
        if num_type == int:
            return random.randint(num_range[0], num_range[1])
        else:
            return round(random.uniform(num_range[0], num_range[1]), 1)

    def make_random_bool(required=True, seed=None):
        if potential_skip(required):
            return ''
        random.seed(seed)
        return random.randint(0, 1) == 0

    def make_random_array(enum: List[str], required=True, seed=None):
        if potential_skip(required):
            return ''
        random.seed(seed)
        return f"[{','.join(random.sample(enum, random.randint(1, len(enum))))}]"

    def build_args_from_constraints(constraints: dict) -> dict:
        args = {}
        args['required'] = constraints.get('required', False)
        if 'pattern' in constraints.keys():
            args['pattern'] = constraints['pattern']
        if 'enum' in constraints.keys():
            args['enum'] = constraints['enum']
        if 'minimum' in constraints.keys() and 'maximum' in constraints.keys():
            args['num_range'] = [constraints['minimum'], constraints['maximum']]
        # changer pour de meilleures valeurs ?
        elif 'minimum' in constraints.keys():
            args['num_range'] = [constraints['minimum'], 10 + constraints['minimum']]
        elif 'maximum' in constraints.keys():
            args['num_range'] = [constraints['maximum'] - 10, constraints['maximum']]
        if 'minLength' in constraints.keys():
            args['length'] = constraints['minLength']
        if 'maxLength' in constraints.keys():
            args['length'] = constraints['maxLength']
        return args

    schema_types_to_python = {
        'number': 'float',
        'integer': 'int',
        'string': 'str',
        'year': 'year',
        'boolean': 'bool',
        'date': 'date',
        'yearmonth': 'date',
        'time': 'time',
        'datetime': 'datetime',
        'array': 'array'
    }

    if from_schema:
        if schema_path.startswith('http'):
            schema = requests.get(schema_path).json()
        else:
            with open(schema_path, encoding=encoding) as jsonfile:
                schema = json.load(jsonfile)
        if not ('fields' in schema.keys()):
            raise Exception('The schema must have a "fields" key.')
        else:
            fields = [
                {
                    'name': f['name'],
                    'type': schema_types_to_python.get(f['type'], 'str'),
                    # build args from format(FR) too
                    'args': (
                        build_args_from_constraints(f['constraints']) if 'constraints' in f.keys()
                        else build_args_from_constraints(f['arrayItem']['constraints'])
                        if 'arrayItem' in f.keys() and 'constraints' in f['arrayItem'].keys()
                        else {}
                    )
                } for f in schema['fields']
            ]

    for k in range(len(fields)):
        if fields[k]['type'] == 'float':
            fields[k]['args']['num_type'] = float
        elif fields[k]['type'] == 'int':
            fields[k]['args']['num_type'] = int
        elif fields[k]['type'] == 'year':
            fields[k]['args']['num_type'] = int
            fields[k]['args']['num_range'] = basic_year_range

    types_to_func = {
        'int': make_random_number,
        'float': make_random_number,
        'date': make_random_date,
        'time': make_random_time,
        'str': make_random_string,
        'url': make_random_url,
        'id': make_random_id,
        'year': make_random_number,
        'bool': make_random_bool,
        'datetime': make_random_datetime,
        'array': make_random_array,
    }

    output = pd.DataFrame(columns=[f["name"] for f in fields])
    # would it be better to create by column or by row (as for now)?
    for k in range(file_length):
        new = [
            types_to_func.get(f['type'], str)(**f['args']) for f in fields
        ]
        output = pd.concat([output, pd.Series(new, index=output.columns).to_frame().T], axis=0)

    if output_file:
        output.to_csv(output_name, sep=output_sep, index=False)

    return output
