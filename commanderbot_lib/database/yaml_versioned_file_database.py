from typing import IO

from commanderbot_lib.database.abc.versioned_file_database import VersionedFileDatabase
from commanderbot_lib.database.mixins.yaml_file_database_mixin import YamlFileDatabaseMixin


class YamlVersionedFileDatabase(VersionedFileDatabase, YamlFileDatabaseMixin):
    # @implements FileDatabase
    async def load(self, file: IO) -> dict:
        return await self.load_yaml(file)

    # @implements FileDatabase
    async def dump(self, data: dict, file: IO):
        await self.dump_yaml(data, file)
