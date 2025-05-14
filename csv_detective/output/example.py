from datetime import datetime
import json
import random
import string
from typing import Union, Optional, Any, Type
import uuid

from faker import Faker
import pandas as pd
import requests
import rstr

fake = Faker()


def create_example_csv_file(
    fields: Optional[dict] = None,
    schema_path: Optional[str] = None,
    file_length: int = 10,
    output_name: Optional[str] = "example_file.csv",
    output_sep: str = ";",
    encoding: str = "utf-8",
    ignore_required: bool = False,
) -> pd.DataFrame:
    """
    Create an example file based on a list of dicts like follows:
    fields = [
        {
            "name": "column_name",
            "type": "column_type",
            "args": {dict_of_args}  # optional
        },
        ...
    ]
    Or from a TableSchema
    """
    # need to make a CLI command

    if not (fields or schema_path):
        raise ValueError("At least fields or schema_path must be specified.")

    def potential_skip(required: bool) -> bool:
        if ignore_required:
            return False
        if not required:
            # for now 30% chance to have an optional value, this could go as an argument
            return random.randint(1, 100) <= 30

    def _string(
        length: int = 10,
        required: bool = True,
        pattern: Optional[str] = None,
        enum: Optional[str] = None,
    ) -> str:
        if potential_skip(required):
            return ""
        if pattern is not None:
            return rstr.xeger(pattern)
        elif enum is not None:
            return random.choice(enum)
        else:
            letters = string.ascii_lowercase
            return "".join(random.choice(letters) for i in range(length))

    def _id(
        required: bool = True,
    ) -> str:
        if potential_skip(required):
            return ""
        return str(uuid.uuid4())

    def _date(
        date_range: Optional[list[str]] = None,
        format: str = "%Y-%m-%d",
        required: bool = True,
    ) -> str:
        # the bounds specified in date_range are expected in the same format as the desired output format
        assert all([k in format for k in ["%d", "%m", "%Y"]])
        if potential_skip(required):
            return ""
        if date_range is None:
            return fake.date(format)
        else:
            if len(date_range) != 2:
                raise ValueError("'date_range' must have exactly two elements.")
            return fake.date_between_dates(
                datetime.strptime(date_range[0], format),
                datetime.strptime(date_range[1], format),
            ).strftime(format)

    def _time(
        format: str = "%H:%M:%S",
        required: bool = True,
    ) -> str:
        assert all([k in format for k in ["%H", "%M", "%S"]])
        if potential_skip(required):
            return ""
        # maybe add a time_range argument?
        return fake.time(format)

    def _datetime(
        datetime_range: Optional[list[str]] = None,
        format: str = "%Y-%m-%d %H-%M-%S",
        required: bool = True,
    ) -> str:
        # the bounds specified in datetime_range are expected in the same format as the desired output format
        assert all([k in format for k in ["%d", "%m", "%Y", "%H", "%M", "%S"]])
        if potential_skip(required):
            return ""
        if datetime_range is None:
            return fake.date_time().strftime(format)
        else:
            if len(datetime_range) != 2:
                raise ValueError("'date_range' must have exactly two elements.")
            return fake.date_time_between(
                datetime.strptime(datetime_range[0], format),
                datetime.strptime(datetime_range[1], format),
            ).strftime(format)

    def _url(required: bool = True) -> str:
        if potential_skip(required):
            return ""
        return f"http://{rstr.domainsafe()}.{rstr.letters(3)}/{rstr.urlsafe()}"

    def _number(
        num_type: Type[Union[int, float]] = int,
        num_range: Optional[list[float]] = None,
        enum: Optional[list] = None,
        required: bool = True,
    ) -> Union[int, float]:
        assert num_range is None or len(num_range) == 2
        if potential_skip(required):
            return ""
        if enum:
            return random.choice(enum)
        if num_range is None:
            num_range = [0, 1000]
        if num_type == int:
            return random.randint(num_range[0], num_range[1])
        else:
            return round(random.uniform(num_range[0], num_range[1]), 1)

    def _bool(required: bool = True) -> bool:
        if potential_skip(required):
            return ""
        return random.randint(0, 1) == 0

    def _array(enum: list[Any], required: bool = True) -> str:
        if potential_skip(required):
            return ""
        return f"[{','.join(random.sample(enum, random.randint(1, len(enum))))}]"

    def build_args_from_constraints(constraints: dict) -> dict:
        args = {}
        args["required"] = constraints.get("required", False)
        for _ in ["pattern", "enum", "format"]:
            if _ in constraints:
                args[_] = constraints[_]
        if "minimum" in constraints and "maximum" in constraints:
            args["num_range"] = [constraints["minimum"], constraints["maximum"]]
        # maybe there are better values than these?
        elif "minimum" in constraints:
            args["num_range"] = [constraints["minimum"], 10 + constraints["minimum"]]
        elif "maximum" in constraints:
            args["num_range"] = [constraints["maximum"] - 10, constraints["maximum"]]
        if "minLength" in constraints:
            args["length"] = constraints["minLength"]
        if "maxLength" in constraints:
            args["length"] = constraints["maxLength"]
        return args

    schema_types_to_python = {
        "number": "float",
        "integer": "int",
        "string": "str",
        "year": "year",
        "boolean": "bool",
        "date": "date",
        "yearmonth": "date",
        "time": "time",
        "datetime": "datetime",
        "array": "array"
    }

    if schema_path:
        if schema_path.startswith("http"):
            schema = requests.get(schema_path).json()
        else:
            with open(schema_path, encoding=encoding) as jsonfile:
                schema = json.load(jsonfile)
        if not ("fields" in schema.keys()):
            raise ValueError("The schema must have a 'fields' key.")
        else:
            fields = [
                {
                    "name": f["name"],
                    "type": schema_types_to_python.get(f["type"], "str"),
                    # when frformat is supported in TableSchema, we can build args for French standards
                    # linked to https://github.com/datagouv/fr-format/issues/26
                    "args": (
                        build_args_from_constraints(f["constraints"]) if "constraints" in f.keys()
                        else build_args_from_constraints(f["arrayItem"]["constraints"])
                        if "arrayItem" in f.keys() and "constraints" in f["arrayItem"].keys()
                        else {}
                    )
                } for f in schema["fields"]
            ]

    for k in range(len(fields)):
        if "args" not in fields[k]:
            fields[k]["args"] = {}
        if fields[k]["type"] == "float":
            fields[k]["args"]["num_type"] = float
        elif fields[k]["type"] == "int":
            fields[k]["args"]["num_type"] = int
        elif fields[k]["type"] == "year":
            fields[k]["args"]["num_type"] = int
            fields[k]["args"]["num_range"] = [1990, 2050]

    types_to_func = {
        "int": _number,
        "float": _number,
        "date": _date,
        "time": _time,
        "str": _string,
        "url": _url,
        "id": _id,
        "year": _number,
        "bool": _bool,
        "datetime": _datetime,
        "array": _array,
    }

    # would it be better to create by column or by row (as for now)?
    output = pd.DataFrame(
        [
            [
                types_to_func.get(f["type"], "str")(**f["args"])
                for f in fields
            ] for _ in range(file_length)
        ],
        columns=[f["name"] for f in fields],
    )

    if output_name:
        output.to_csv(output_name, sep=output_sep, index=False)

    return output
