import json

from commanderbot_lib.database.abc.read_only_remote_file_database import (
    ReadOnlyRemoteFileDatabase,
)


class JsonReadOnlyRemoteFileDatabase(ReadOnlyRemoteFileDatabase):
    # @implements ReadOnlyRemoteFileDatabase
    async def parse(self, raw: str) -> dict:
        return json.loads(raw)
