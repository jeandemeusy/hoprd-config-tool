from .baseobject import BaseObject


class Node(BaseObject):
    keys = {
        "safe": "safe_address",
        "module": "module_address",
        "api_password": "api_password",
        "identity_password": "identity_password",
        "identity": "identity",
        "peer_id": "node_peer_id",
        "address": "node_address",
        "surname": "surname",
    }
