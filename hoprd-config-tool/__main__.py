import logging
import subprocess
from pathlib import Path

import click
import yaml

from .config_filling import ConfigFilling
from .library import get_template, replace_fields
from .network import Network
from .params import NodeParams
from .yaml import Aggregating, AutoFunding, AutoRedeeming, ClosureFinalizer, IPv4, Token

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s:%(message)s", datefmt="[%X]")
logger = logging.getLogger("hoprd-config-generator")

@click.command()
@click.option("--params", "params_file", type=click.Path(path_type=Path))
@click.option("--folder", "base_folder", default=Path("./.hoprd-nodes"), type=click.Path(path_type=Path))
@click.option("--output", default=Path("./docker-compose.yml"), type=click.Path(path_type=Path),)
def main(params_file: str, base_folder: Path, output: Path):
    for cls in [IPv4, Token, Aggregating, AutoFunding, AutoRedeeming, ClosureFinalizer]:
        yaml.SafeLoader.add_constructor(cls.yaml_tag, cls.from_yaml)
        yaml.SafeDumper.add_multi_representer(cls, cls.to_yaml)

    with open(get_template(Path("node.yaml")), "r") as f:
        node_template = yaml.safe_load(f)
        logger.info(f"Successfuly read node config file template")

    ip_addr = subprocess.check_output("curl -s https://ipinfo.io/ip", shell=True).decode()
    logger.info(f"Retrieved machine IP as '{ip_addr}'")

    with open(params_file, "r") as f:
        config_content = yaml.safe_load(f)

    networks = [Network(value, name=key) for key, value in config_content.items() if key != "env"]

    for network in networks:
        logger.info(f"Loaded {len(network.nodes)} nodes for '{network.name}' network")

    # Create list of nodes
    nodes_params = list[NodeParams]()
    for network in networks:
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
    with open(output, "w") as f:
        f.write(
            get_template(Path("./templates/docker-compose.yml.j2")).render(
                services=[p.as_dict for p in nodes_params], 
                versions={n.name: n.version for n in networks},
                envvars=config_content.get("env", {})
            )
        )
        logger.info(f"Docker compose file at '{output}'")


if __name__ == "__main__":
    main()
