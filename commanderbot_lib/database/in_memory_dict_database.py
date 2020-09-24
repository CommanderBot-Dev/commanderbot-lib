from discord.ext.commands import Bot, Cog

from commanderbot_lib.database.abc.dict_database import DictDatabase


class InMemoryDictDatabase(DictDatabase):
    def __init__(self, bot: Bot, cog: Cog, data: dict):
        super().__init__(bot, cog)
        self._data: dict = data

    # @implements DictDatabase
    @property
    def persistent(self) -> bool:
        return True

    # @implements DictDatabase
    async def read(self) -> dict:
        return self._data

    # @implements DictDatabase
    async def write(self, data: dict):
        self._data = data
