from typing import Any

from .library import get_nested_value, set_nested_value


class ConfigFilling:
    keys = {
        "api/auth/token": "api_password",
        "api/host/port": "api_port",
        "hopr/chain/network": "network/meta/name",
        "hopr/host/port": "network_port",
        "hopr/safe_module/module_address": "module_address",
        "hopr/safe_module/safe_address": "safe_address",
        "identity/password": "identity_password",
        "hopr/host/address": "*ip_addr"
    }

    @classmethod
    def apply(cls, dictionary: dict, object: Any, **kwargs):
        for key, value in cls.keys.items():
            if value.startswith("*"):
                parsed_value = kwargs[value.lstrip('*')]
            else:
                parsed_value = get_nested_value(object, value.split("/"))

            path = key.split('/')
            set_nested_value(dictionary, path, parsed_value)

        return dictionary
