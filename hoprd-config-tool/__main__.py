import logging
import subprocess
from pathlib import Path

import click
import tomli_w
import yaml

from .config_filling import ConfigFilling
from .docker_compose import DockerComposeGenerator
from .library import get_template, replace_fields
from .network import Network
from .params import NodeParams
from .yaml import Aggregating, AutoFunding, AutoRedeeming, ClosureFinalizer, IPv4, Token
from .yaml.parser import YAMLParser

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-8s:%(message)s", datefmt="[%X]")
logger = logging.getLogger("hoprd-config-generator")


def _to_builtin(value):
    if isinstance(value, YAMLParser):
        value = vars(value)

    if isinstance(value, dict):
        return {k: _to_builtin(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_to_builtin(v) for v in value]

    return value


def _prune_nones(value):
    if isinstance(value, dict):
        return {k: _prune_nones(v) for k, v in value.items() if v is not None}

    if isinstance(value, list):
        return [_prune_nones(v) for v in value if v is not None]

    return value


@click.command()
@click.option("--params", "params_file", type=click.Path(path_type=Path))
@click.option("--folder", "base_folder", default=Path("./.hoprd-nodes"), type=click.Path(path_type=Path))
def main(params_file: str, base_folder: Path):
    for cls in [IPv4, Token, Aggregating, AutoFunding, AutoRedeeming, ClosureFinalizer]:
        yaml.SafeLoader.add_constructor(cls.yaml_tag, cls.from_yaml)
        yaml.SafeDumper.add_multi_representer(cls, cls.to_yaml)

    node_template = get_template(Path("node.toml"))
    logger.info(f"Successfuly read node config file template")

    try:
        ip_addr = subprocess.check_output(
            "curl -s https://ipinfo.io/ip", shell=True).decode().strip()
        logger.info(f"Retrieved machine IP as '{ip_addr}'")
    except subprocess.CalledProcessError as exc:
        ip_addr = "0.0.0.0"
        logger.warning(
            "Could not retrieve public IP (defaulting to %s): %s", ip_addr, exc)

    with open(params_file, "r") as f:
        config_content: dict = yaml.safe_load(f)

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
        config = _prune_nones(_to_builtin(config))

        with open(obj.config_file, "wb") as f:
            tomli_w.dump(config, f)
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
