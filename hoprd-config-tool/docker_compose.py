"""Utilities for rendering docker-compose files.

This module centralizes the logic required to prepare the context passed to the
``docker-compose.yml.j2`` template.  Previously this logic lived inside the
``__main__`` module which made it difficult to reason about and to test.  The
new structure provides small, well-named helpers that describe the intent of
each operation (parsing networks, formatting YAML, rendering/writing the
compose file, ...).  This makes the process easier to maintain and improves the
readability of ``__main__``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from textwrap import indent
from typing import Iterable, Mapping, Sequence

import yaml

from .library import get_template
from .network import Network
from .params import NodeParams


@dataclass(frozen=True)
class DockerComposeContext:
    """All of the information required by the docker-compose template."""

    services: Sequence[dict]
    version: str | None
    network: str
    envvars: Mapping[str, object] = field(default_factory=dict)
    networks: Mapping[str, object] = field(default_factory=dict)

    @classmethod
    def from_config(
        cls,
        network: Network,
        nodes: Iterable[NodeParams],
        config_content: Mapping[str, object],
    ) -> "DockerComposeContext":
        """Create a context from the parsed network and raw config data."""

        networks = dict(getattr(network, "networks", None) or {})
        return cls(
            services=[node.as_dict for node in nodes],
            version=network.meta.version,
            network=network.meta.name,
            envvars=dict(config_content.get("env", {})),
            networks=networks,
        )

    @property
    def network_names(self) -> tuple[str, ...]:
        return tuple(self.networks.keys())

    @property
    def networks_yaml(self) -> str:
        if not self.networks:
            return ""
        dumped = yaml.safe_dump(self.networks, sort_keys=False)
        return indent(dumped, "  ")

    def to_template_kwargs(self) -> dict:
        """Return a dictionary ready to be passed to the Jinja template."""

        return {
            "services": self.services,
            "version": self.version,
            "network": self.network,
            "envvars": self.envvars,
            "networks": self.networks or None,
            "networks_yaml": self.networks_yaml,
            "network_names": self.network_names,
        }


class DockerComposeGenerator:
    """Helper responsible for rendering docker-compose files."""

    def __init__(self, template: Path | str = Path("docker-compose.yml.j2")):
        self.template_path = Path(template)

    def _render_template(self, context: DockerComposeContext) -> str:
        template = get_template(self.template_path)
        return template.render(**context.to_template_kwargs())

    def render(
        self,
        network: Network,
        nodes: Sequence[NodeParams],
        config_content: Mapping[str, object],
    ) -> str:
        context = DockerComposeContext.from_config(network, nodes, config_content)
        return self._render_template(context)

    def write(
        self,
        output: Path,
        network: Network,
        nodes: Sequence[NodeParams],
        config_content: Mapping[str, object],
    ) -> Path:
        """Render the compose file and write it to ``output``."""

        content = self.render(network, nodes, config_content)
        output_path = Path(output)
        output_path.write_text(content)
        return output_path
