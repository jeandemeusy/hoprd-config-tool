from .baseobject import BaseObject
from .node import Node


class Network(BaseObject):
    keys = {
        "name": "name",
        "config": "config",
        "version": "version",
        "api_port_base": "api_port_base",
        "network_port_base": "network_port_base",
        "session_port_base": "session_port_base",
        "nodes": "nodes",
        "slug": "nodes_slug"
    }

    def post_init(self):
        self.nodes = [Node(subdata) for subdata in self.nodes]
