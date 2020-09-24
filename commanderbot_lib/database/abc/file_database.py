from abc import abstractmethod
from os import PathLike
from pathlib import Path
from typing import IO

from discord.ext.commands import Bot, Cog

from commanderbot_lib.database.abc.cog_database import CogDatabase
from commanderbot_lib.database.abc.dict_database import DictDatabase
from commanderbot_lib.utils import fix_path


class FileDatabase(DictDatabase):
    def __init__(self, bot: Bot, cog: Cog, path: PathLike, persistent: bool = True):
        super().__init__(bot, cog)
        self._path: Path = fix_path(path)
        self._persistent: bool = persistent

    @abstractmethod
    async def load(self, file: IO) -> dict:
        """ Load and return data from the given file, such as with `json.load`. """

    @abstractmethod
    async def dump(self, data: dict, file: IO):
        """ Dump the given data to the given file, such as with `json.dump`. """

    # @implements DictDatabase
    @property
    def persistent(self) -> bool:
        return self._persistent

    # @implements DictDatabase
    async def read(self) -> dict:
        self._log.info(f"Loading database from file: {self._path}")
        with open(self._path, encoding="utf-8") as file:
            return await self.load(file)

    # @implements DictDatabase
    async def write(self, data: dict):
        self._log.info(f"Saving database to file: {self._path}")
        with open(self._path, "w+", encoding="utf-8") as file:
            await self.dump(data, file)
