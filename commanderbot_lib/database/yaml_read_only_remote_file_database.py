import yaml
from commanderbot_lib.database.abc.read_only_remote_file_database import ReadOnlyRemoteFileDatabase


class YamlReadOnlyRemoteFileDatabase(ReadOnlyRemoteFileDatabase):
    # @implements ReadOnlyRemoteFileDatabase
    async def parse(self, raw: str) -> dict:
        return yaml.safe_load(raw)
