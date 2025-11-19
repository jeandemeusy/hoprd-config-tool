from .baseobject import BaseObject


class NodeParams(BaseObject):
    keys = {
        "index": "index",
        "network": "network",
        "api_password": "api_password",
        "api_port": "api_port",
        "network_port": "network_port",
        "session_port": "session_port",
        "module_address": "module_address",
        "safe_address": "safe_address",
        "identity": "identity",
        "identity_password": "identity_password",
        "folder": "folder"
    }

    @property
    def network_name(self):
        return self.network.meta.name

    @property
    def api_port(self):
        return self.network.meta.api_port_base + self.index

    @property
    def network_port(self):
        return self.network.meta.network_port_base + self.index

    @property
    def session_port(self):
        return self.network.meta.session_port_base + self.index

    @property
    def filename(self):
        return f"hoprd-{self.network_name}-{self.index}"

    @property
    def config_folder(self):
        folder = self.folder.joinpath(".hopr-configs", self.network_name)
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @property
    def id_folder(self):
        folder = self.folder.joinpath(".hopr-ids", self.network_name)
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @property
    def config_file(self):
        return self.config_folder.joinpath(f"{self.filename}.cfg.toml")

    @property
    def id_file(self):
        return self.id_folder.joinpath(f"{self.filename}.id")
