from .baseobject import BaseObject
from .meta import Meta
from .node import Node


class Network(BaseObject):
    keys = {
        "meta": "meta",
        "config": "config",
        "nodes": "nodes",
        "slug": "nodes_slug",
        "networks": "networks",
    }

    def post_init(self):
        self.nodes = [Node(subdata) for subdata in self.nodes]
        self.meta = Meta(self.meta)
