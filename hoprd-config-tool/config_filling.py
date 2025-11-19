from typing import Any

from .library import get_nested_value, set_nested_attr, set_nested_value


class ConfigFilling:
    keys = {
        "api/auth.token": "api_password",
        "api/host/port": "api_port",
        "hopr/chain/network": "network/meta/name",
        "hopr/host/port": "network_port",
        "hopr/safe_module/module_address": "module_address",
        "hopr/safe_module/safe_address": "safe_address",
        "identity/password": "identity_password",
        "hopr/host/address.ipv4": "*ip_addr"
    }

    @classmethod
    def apply(cls, dictionary: dict, object: Any, **kwargs):
        for key, value in cls.keys.items():
            splits = key.split('.')

            if value.startswith("*"):
                parsed_value = kwargs[value.lstrip('*')]
            else:
                parsed_value = get_nested_value(object, value.split("/"))

            path = splits[0].split('/')

            if len(splits) == 1:
                set_nested_value(dictionary, path, parsed_value)
            else:
                path = splits[0].split('/')
                set_nested_attr(dictionary, path, splits[1], parsed_value)

        return dictionary
