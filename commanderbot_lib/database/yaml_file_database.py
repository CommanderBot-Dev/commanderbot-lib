from typing import IO

import yaml

from commanderbot_lib.database.abc.file_database import FileDatabase


class YamlFileDatabase(FileDatabase):
    # @implements FileDatabase
    async def load(self, file: IO) -> dict:
        return yaml.safe_load(file)

    # @implements FileDatabase
    async def dump(self, data: dict, file: IO):
        return yaml.safe_dump(data, file)
