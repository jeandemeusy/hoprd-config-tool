from copy import deepcopy
from importlib import resources
from pathlib import Path
from typing import Any

from . import templates
import collections.abc
from jinja2 import Template


def convert(value: Any):
    if value is None:
        return None

    try:
        value = float(value)
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        integer = int(value)
        if integer == value:
            value = integer
    except ValueError:
        pass
    except TypeError:
        pass

    return value
    
def get_template(filename: Path):
    full_path: Path = resources.files(templates) / filename

    if filename.suffix in [".yaml", ".yml"]:
        return full_path
    elif filename.suffix in [".j2"]:
        with open(full_path) as file_:
            template = Template(file_.read(), trim_blocks=True, lstrip_blocks=True)
        return template
    else:
        return filename


def replace_fields(source: dict, addons: dict) -> dict:
    copy = deepcopy(source)

    for k, v in addons.items():
        if isinstance(v, collections.abc.Mapping):
            copy[k] = replace_fields(copy.get(k, {}), v)
        else:
            copy[k] = v
    return copy


def set_nested_value(d, keys, value):
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


def set_nested_attr(d, keys, attr, value):
    for key in keys:
        d = d.setdefault(key, {})
    setattr(d, attr, value)


def get_nested_value(d, keys):
    for key in keys:
        d = getattr(d, key)
    return d
