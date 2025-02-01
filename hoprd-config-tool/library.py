import collections.abc
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
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


def get_template(filename: Path, template_folder: str = "templates"):
    template_path =  Path(__file__).absolute().parent.joinpath(template_folder, filename)

    if filename.suffix in [".yaml", ".yml"]:
        with open(template_path, "r") as f:
            return yaml.safe_load(f)

    elif filename.suffix in [".j2"]:
        with open(template_path, "r") as f:
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
