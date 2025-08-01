# hoprd-config-tool


Tool to generate HOPRd identity, configuration, and docker-compose files from a single input where all required data is specified.

## Installation
```bash
➜ pip(3) install (-U) hoprd-config-tool
```

## Usage
To generate the required ressources (identities, configurations and docker-compose files) from a [config file](./.config/network_1.yml), run the following command:

```sh
➜ python -m hoprd-config-tool --params .config/network_1.yml
```

You can specify the root folder where identity and configuration files will be generated by appending the optional parameter `--folder <FOLDER>` which by default is set to `./.hoprd-nodes/`.

The generated docker compose file follows the default naming: `docker-compose.yml`