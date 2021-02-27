from abc import abstractmethod
from datetime import datetime
from os import PathLike
from pathlib import Path
from shutil import copyfile
from typing import IO

from discord.ext.commands import Bot, Cog

from commanderbot_lib.database.abc.dict_database import DictDatabase
from commanderbot_lib.utils import fix_path

BACKUP_TIMESTAMP_FORMAT = "%Y-%m-%d-%H-%M-%S-%f"


class FileDatabase(DictDatabase):
    """
    A `CogDatabase` that is used to manage a simple database in the form of a file on disk.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    path: :class:`PathLike`
        The path to the file on the local filesystem.
    persistent: :class:`bool`
        Whether changes should be written back to the file on disk.
    """

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
        """ Default implementation that simply reads the entire file as data. """
        return await self._read_file()

    # @implements DictDatabase
    async def write(self, data: dict):
        """ Default implementation that simply writes the entire file as data. """
        await self._write_file(data)

    async def backup(self):
        """ Default implementation that simply copies the existing database file. """
        timestamp = datetime.utcnow().strftime(BACKUP_TIMESTAMP_FORMAT)
        source_path = self._path
        backup_path = self._path.with_suffix(f".backup.{timestamp}{self._path.suffix}")
        self._log.warning(
            f'Backing up database from "{source_path}" to "{backup_path}>"'
        )
        # TODO Use async file I/O. #enhance #async-files
        copyfile(source_path, backup_path)

    async def _read_file(self) -> dict:
        self._log.info(f"Loading database from file: {self._path}")
        with open(self._path, encoding="utf-8") as file:
            return await self.load(file)

    async def _write_file(self, data: dict):
        self._log.info(f"Saving database to file: {self._path}")
        with open(self._path, "w+", encoding="utf-8") as file:
            await self.dump(data, file)
