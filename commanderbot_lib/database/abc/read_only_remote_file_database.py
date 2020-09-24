import urllib.request
from abc import abstractmethod

from discord.ext.commands import Bot, Cog

from commanderbot_lib.database.abc.dict_database import DictDatabase


class ReadOnlyRemoteFileDatabase(DictDatabase):
    def __init__(self, bot: Bot, cog: Cog, address: str):
        super().__init__(bot, cog)
        self._address: str = address

    @abstractmethod
    async def parse(self, raw: str) -> dict:
        """ Parse and return data from the given string, such as with `json.loads`. """

    # @implements DictDatabase
    @property
    def persistent(self) -> bool:
        return False

    # @implements DictDatabase
    async def read(self) -> dict:
        self._log.info(f"Downloading database from remote file: {self._address}")
        response = urllib.request.urlopen(self._address)
        raw = response.read().decode("utf8")
        return await self.parse(raw)

    # @implements DictDatabase
    async def write(self, data: dict):
        pass
