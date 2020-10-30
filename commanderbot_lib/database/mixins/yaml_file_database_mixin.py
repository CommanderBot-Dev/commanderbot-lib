from typing import IO

import yaml


class YamlFileDatabaseMixin:
    async def load_yaml(self, file: IO) -> dict:
        return yaml.safe_load(file)

    async def dump_yaml(self, data: dict, file: IO):
        return yaml.safe_dump(data, file)
