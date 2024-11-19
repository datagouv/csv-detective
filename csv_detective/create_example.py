import random
import uuid
import string
from dateutil.parser import parse
import pandas as pd
from typing import List, Union
import json
import requests
import rstr
from faker import Faker

fake = Faker()


def create_example_csv_file(
    fields: Union[dict, None] = None,
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

    if not (fields or schema_path):
        raise ValueError("At least fields or schema_path must be specified.")

    def potential_skip(required):
        if ignore_required:
            return False
        if not required:
            # for now 30% chance to have an optional value, this could go as an argument
            return random.randint(0, 100) < 30

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
        format='%Y-%m-%d',
        required=True,
    ):
        if potential_skip(required):
            return ''
        assert all([k in format for k in ['%d', '%m', '%Y']])
        if date_range is None:
            return fake.date(format)
        else:
            if len(date_range) != 2:
                raise ValueError('"date_range" must have exactly two elements.')
            return fake.date_between_dates(
                parse(date_range[0]),
                parse(date_range[1])
            ).strftime(format)

    def make_random_time(
        format='%H:%M:%S',
        required=True,
    ):
        if potential_skip(required):
            return ''
        assert all([k in format for k in ['%H', '%M', '%S']])
        # maybe add a time_range argument?
        return fake.time(format)

    def make_random_datetime(
        datetime_range: Union[None, List[str]] = None,
        format='%Y-%m-%d %H-%M-%S',
        required=True,
    ):
        if potential_skip(required):
            return ''
        assert all([k in format for k in ['%d', '%m', '%Y', '%H', '%M', '%S']])
        if datetime_range is None:
            return fake.date_time().strftime(format)
        else:
            if len(datetime_range) != 2:
                raise ValueError('"date_range" must have exactly two elements.')
            return fake.date_time_between(
                parse(datetime_range[0]),
                parse(datetime_range[1])
            ).strftime(format)

    def make_random_url(required=True, seed=None):
        if potential_skip(required):
            return ''
        random.seed(seed)
        return f'http://{rstr.domainsafe()}.{rstr.letters(3)}/{rstr.urlsafe()}/?{rstr.urlsafe()}'

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
        for _ in ['pattern', 'enum', 'format']:
            if _ in constraints:
                args[_] = constraints[_]
        if 'minimum' in constraints and 'maximum' in constraints:
            args['num_range'] = [constraints['minimum'], constraints['maximum']]
        # changer pour de meilleures valeurs ?
        elif 'minimum' in constraints:
            args['num_range'] = [constraints['minimum'], 10 + constraints['minimum']]
        elif 'maximum' in constraints:
            args['num_range'] = [constraints['maximum'] - 10, constraints['maximum']]
        if 'minLength' in constraints:
            args['length'] = constraints['minLength']
        if 'maxLength' in constraints:
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

    if schema_path:
        if schema_path.startswith('http'):
            schema = requests.get(schema_path).json()
        else:
            with open(schema_path, encoding=encoding) as jsonfile:
                schema = json.load(jsonfile)
        if not ('fields' in schema.keys()):
            raise ValueError('The schema must have a "fields" key.')
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
            fields[k]['args']['num_range'] = [1990, 2050]

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
