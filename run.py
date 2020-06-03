import csv
import sys
from enum import Enum
from typing import TextIO, Optional

import pydantic
import yaml
from pydantic import validator

try:
    from yaml import CLoader as YAMLLoader, CDumper as YAMLDumper
except ImportError:
    from yaml import Loader as YAMLLoader, Dumper as YAMLDumper



class FieldType(str, Enum):
    INTEGER = 'Integer'
    FLOAT = 'Float'
    UNICODE = 'Unicode'
    UNKNOWN = 'NULL'


class Field(pydantic.BaseModel):
    field: str
    type: FieldType
    sum: str
    min: str
    max: str
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    mean: Optional[float] = None
    stddev: Optional[float] = None

    @validator('min_length', 'max_length', pre=True)
    def validate_lengths(cls, value):
        if value == '':
            return None

        return value


def line_to_field(line: dict) -> Field:  # type: ignore
    """Convert raw dict to a Field instance."""
    for name in ['mean', 'stddev']:
        if line.get(name) == '':
            line.pop(name)

    try:
        return Field(**line)

    except pydantic.ValidationError as err:
        raise ValueError(
            f"Cannot interpret a string from xsv input: {line}"
        ) from err


def field_to_ysv_column(field: Field) -> list:   # type: ignore
    """Convert a Field instance to ysv column definition."""
    return [
        {'input': field.field}
    ]


def ysv_schema(stats_data: TextIO) -> str:
    """Generate template for ysv transformation file."""
    reader = csv.DictReader(stats_data)

    fields = [
        line_to_field(line)
        for line in reader
    ]

    schema = {
        'version': 1,
        'columns': {
            field.field: field_to_ysv_column(field)
            for field in fields
        }
    }

    return yaml.dump(schema, Dumper=YAMLDumper, sort_keys=False)


def main():
    sys.stdout.write(ysv_schema(sys.stdin))
    sys.stdout.flush()


if __name__ == '__main__':
    main()
