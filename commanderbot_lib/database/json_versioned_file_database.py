from typing import IO

from commanderbot_lib.database.abc.versioned_file_database import VersionedFileDatabase
from commanderbot_lib.database.mixins.json_file_database_mixin import (
    JsonFileDatabaseMixin,
)


class JsonVersionedFileDatabase(VersionedFileDatabase, JsonFileDatabaseMixin):
    # @implements FileDatabase
    async def load(self, file: IO) -> dict:
        return await self.load_json(file)

    # @implements FileDatabase
    async def dump(self, data: dict, file: IO):
        await self.dump_json(data, file)
