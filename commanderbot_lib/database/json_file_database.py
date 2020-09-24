import json
from typing import IO

from commanderbot_lib.database.abc.file_database import FileDatabase


class JsonFileDatabase(FileDatabase):
    # @implements FileDatabase
    async def load(self, file: IO) -> dict:
        return json.load(file)

    # @implements FileDatabase
    async def dump(self, data: dict, file: IO):
        return json.dump(data, file, indent=2)
