import logging
import subprocess
from pathlib import Path

import click

try:
    import tomllib as toml_loader
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as toml_loader

import yaml

from .config_filling import ConfigFilling
from .docker_compose import DockerComposeGenerator
from .library import get_template, replace_fields
from .network import Network
from .params import NodeParams
from .yaml import Aggregating, AutoFunding, AutoRedeeming, ClosureFinalizer, IPv4, Token

YAML_OBJECTS = [IPv4, Token, Aggregating,
                AutoFunding, AutoRedeeming, ClosureFinalizer]
YAML_TAG_MAP = {cls.__name__: cls for cls in YAML_OBJECTS}

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-8s:%(message)s", datefmt="[%X]")
logger = logging.getLogger("hoprd-config-generator")


def _expand_tagged_sections(value):
    """Convert TOML dotted tables into tag-aware dictionaries.

    When the params TOML file expresses YAML tags via dotted array tables
    (for example ``[[config.hopr.strategy.strategies.ClosureFinalizer]]``), the
    parsed structure ends up as a mapping whose keys correspond to the class
    names (``{"ClosureFinalizer": [{...}]}``).  The configuration generator
    expects the previous ``{"tag": "ClosureFinalizer", ...}`` layout, so we
    normalize those mappings back into a list of dictionaries that carry the
    ``tag`` attribute.  Regular dictionaries are processed recursively without
    modification.
    """

    if isinstance(value, dict):
        normalized = {k: _expand_tagged_sections(v) for k, v in value.items()}

        if normalized and all(key in YAML_TAG_MAP for key in normalized):
            expanded = []
            for tag_name, entries in normalized.items():
                entries_list = entries if isinstance(entries, list) else [entries]
                for entry in entries_list:
                    if isinstance(entry, dict):
                        payload = dict(entry)
                    else:
                        payload = {"value": entry}
                    payload.setdefault("tag", tag_name)
                    expanded.append(payload)
            return expanded

        return normalized

    if isinstance(value, list):
        return [_expand_tagged_sections(v) for v in value]

    return value


def _normalize_nodes_section(config_content):
    """Allow ``[[nodes.<surname>]]`` tables to define per-node entries."""

    nodes = config_content.get("nodes")
    if isinstance(nodes, dict):
        normalized_nodes = []
        for surname, entries in nodes.items():
            if isinstance(entries, list):
                entries_list = entries
            else:
                entries_list = [entries]

            for entry in entries_list:
                if not isinstance(entry, dict):
                    raise TypeError(
                        "Node definitions must be tables; "
                        f"got {type(entry).__name__} for '{surname}'"
                    )

                payload = dict(entry)
                if surname not in (None, ""):
                    payload.setdefault("surname", surname)
                normalized_nodes.append(payload)

        config_content["nodes"] = normalized_nodes

    return config_content


def _instantiate_tagged_objects(value):
    if isinstance(value, dict):
        tag_name = value.get("tag")
        if isinstance(tag_name, str):
            tag_name = tag_name.lstrip("!")
            yaml_class = YAML_TAG_MAP.get(tag_name)
            if yaml_class is None:
                raise ValueError(f"Unknown tag '{tag_name}' in params file")

            payload = {
                key: _instantiate_tagged_objects(val)
                for key, val in value.items()
                if key != "tag"
            }

            annotations = list(getattr(yaml_class, "__annotations__", {}).keys())
            if "value" in payload and annotations:
                first_attr = annotations[0]
                value_payload = payload.pop("value")
                if first_attr not in payload:
                    payload[first_attr] = value_payload

            return yaml_class(**payload)

        return {k: _instantiate_tagged_objects(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_instantiate_tagged_objects(v) for v in value]

    return value


@click.command()
@click.option("--params", "params_file", type=click.Path(path_type=Path))
@click.option("--folder", "base_folder", default=Path("./.hoprd-nodes"), type=click.Path(path_type=Path))
def main(params_file: Path, base_folder: Path):
    for cls in YAML_OBJECTS:
        yaml.SafeLoader.add_constructor(cls.yaml_tag, cls.from_yaml)
        yaml.SafeDumper.add_multi_representer(cls, cls.to_yaml)

    node_template = get_template(Path("node.yaml"))
    logger.info(f"Successfuly read node config file template")

    try:
        ip_addr = subprocess.check_output(
            "curl -s https://ipinfo.io/ip", shell=True).decode().strip()
        logger.info(f"Retrieved machine IP as '{ip_addr}'")
    except subprocess.CalledProcessError as exc:
        ip_addr = "0.0.0.0"
        logger.warning(
            "Could not retrieve public IP (defaulting to %s): %s", ip_addr, exc)

    with params_file.open("rb") as f:
        config_content: dict = toml_loader.load(f)

    config_content = _expand_tagged_sections(config_content)
    config_content = _instantiate_tagged_objects(config_content)
    config_content = _normalize_nodes_section(config_content)

    network = Network(config_content)
    logger.info(f"Loaded {len(network.nodes)} nodes for '{network.meta.name}' network")

    # Create list of nodes
    nodes_params = list[NodeParams]()
    for index, node in enumerate(network.nodes, 1):
        params = {
            "index": index,
            "network": network,
            "folder": base_folder
        }
        node_param = NodeParams(params | node.as_dict)
        nodes_params.append(node_param)

    # Generate config files
    logger.info("Generating config files")
    for obj in nodes_params:
        config = replace_fields(node_template, obj.network.config)
        config = ConfigFilling.apply(config, obj, ip_addr=ip_addr)

        with open(obj.config_file, "w") as f:
            yaml.safe_dump(config, f)
            logger.debug(
                f"  Config for {obj.filename} at '{obj.config_file}'")

    # Generate identity files
    logger.info("Generating identity files")
    for obj in nodes_params:
        with open(obj.id_file, "w") as f:
            f.write(obj.identity)
            logger.debug(
                f"  Identity for {obj.filename} at '{obj.id_file}'")

    # Generate docker compose file
    logger.info("Generating docker-compose file")
    compose_output = Path(f"./docker-compose.{network.meta.name}.yml")
    compose_generator = DockerComposeGenerator()
    compose_generator.write(
        compose_output, network=network, nodes=nodes_params, config_content=config_content
    )
    logger.info(f"Docker compose file at '{compose_output}'")


if __name__ == "__main__":
    main()
