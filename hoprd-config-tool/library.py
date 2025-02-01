import collections.abc
import os
from copy import deepcopy
from importlib import resources
from pathlib import Path
from typing import Any

from jinja2 import Template

from . import templates


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
    if filename.suffix in [".yaml", ".yml"]:
        return resources.files(templates) / filename
    elif filename.suffix in [".j2"]:
        this_file = os.path.abspath(__file__)
        this_dir = os.path.dirname(this_file)
        template_path = os.path.join(this_dir, filename)
        with open(template_path) as f:
            return Template(f.read(), trim_blocks=True, lstrip_blocks=True)
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
