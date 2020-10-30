import json
from typing import IO


class JsonFileDatabaseMixin:
    async def load_json(self, file: IO) -> dict:
        return json.load(file)

    async def dump_json(self, data: dict, file: IO):
        # TODO Make the indent (and other options) configurable. #enhance
        return json.dump(data, file, indent=2)
