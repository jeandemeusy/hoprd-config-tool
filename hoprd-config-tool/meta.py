from .baseobject import BaseObject


class Meta(BaseObject):
    keys = {
        "version": "version",
        "name": "name",
        "api_port_base": "api_port_base",
        "network_port_base": "network_port_base",
        "session_port_base": "session_port_base",
    }