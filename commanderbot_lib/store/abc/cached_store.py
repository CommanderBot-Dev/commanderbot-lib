from abc import abstractmethod
from typing import Generic, TypeVar

from discord.ext.commands import Bot, Cog

from commanderbot_lib.database.abc.dict_database import DictDatabase
from commanderbot_lib.database.abc.file_database import FileDatabase
from commanderbot_lib.database.abc.read_only_remote_file_database import (
    ReadOnlyRemoteFileDatabase,
)
from commanderbot_lib.database.in_memory_dict_database import InMemoryDictDatabase
from commanderbot_lib.database.json_file_database import JsonFileDatabase
from commanderbot_lib.database.json_read_only_remote_file_database import (
    JsonReadOnlyRemoteFileDatabase,
)
from commanderbot_lib.database.yaml_file_database import YamlFileDatabase
from commanderbot_lib.database.yaml_read_only_remote_file_database import (
    YamlReadOnlyRemoteFileDatabase,
)
from commanderbot_lib.options.abc.options_with_database import OptionsWithDatabase
from commanderbot_lib.store.abc.cog_store import CogStore

OptionsType = TypeVar("OptionsType", bound=OptionsWithDatabase)
DatabaseType = TypeVar("DatabaseType", bound=DictDatabase)
CacheType = TypeVar("CacheType")


class CachedStore(
    CogStore[OptionsType, DatabaseType], Generic[OptionsType, DatabaseType, CacheType]
):
    """
    A partial implementation of `CogStore` that maintains an in-memory cache of data of an
    arbitrary type, which can be used to avoid accessing the underlying database for every read.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    options: :class:`OptionsType`
        A set of static configuration options for the cog.
    """

    def __init__(self, bot: Bot, cog: Cog, options: OptionsType):
        super().__init__(bot, cog, options)
        self._cache: CacheType = None

    @abstractmethod
    async def _build_cache(self, data: dict) -> CacheType:
        """ Return the initial cache constructed from the given data. """

    @abstractmethod
    async def serialize(self) -> dict:
        """ Convert the current cache into a JSON-serializable form. """

    # @implements CogStore
    async def _create_database(self) -> DatabaseType:
        db_options = self.options.database
        # If no database is given, use in-memory data.
        if db_options is None:
            self._log.info(f"No database defined; creating an empty in-memory one")
            return await self._make_in_memory_database({})
        # If database is a dict, use it directly as the initial set of in-memory data.
        elif isinstance(db_options, dict):
            return await self._make_in_memory_database(db_options)
        # If database is a string, use a file database.
        elif isinstance(db_options, str):
            return await self._make_file_database(db_options)
        # Otherwise, we've got a problem.
        raise ValueError(
            f"Invalid database definition for cog <{self.cog.qualified_name}>: {db_options}"
        )

    # @overrides CachedStore
    async def _after_database_init(self):
        initial_data = await self._database.read()
        self._cache = await self._build_cache(initial_data)

    async def _make_in_memory_database(self, data: dict) -> InMemoryDictDatabase:
        self._log.info(
            f"Creating an in-memory database with {len(data)} key(s) of initial data"
        )
        return InMemoryDictDatabase(self.bot, self.cog, data=data)

    async def _make_file_database(self, location: str) -> FileDatabase:
        # If location is an HTTP address, use a read-only remote file database.
        if location.startswith(("http://", "https://")):
            return await self._make_remote_file_database(location)
        # If the location is any other string, assume it is a file path and use a local file database.
        return await self._make_local_file_database(location)

    async def _make_remote_file_database(
        self, location: str
    ) -> ReadOnlyRemoteFileDatabase:
        # JSON
        if location.endswith(".json"):
            self._log.info(
                f"Creating a remote JSON file database using the file at: {location}"
            )
            return JsonReadOnlyRemoteFileDatabase(self.bot, self.cog, address=location)
        # YAML
        elif location.endswith((".yaml", ".yml")):
            self._log.info(
                f"Creating a remote file database using the file at: {location}"
            )
            return YamlReadOnlyRemoteFileDatabase(self.bot, self.cog, address=location)
        # Anything else is unsupported.
        else:
            raise ValueError(
                f"Unsupported file type for remote file database for cog <{self.cog.qualified_name}>: {location}"
            )

    async def _make_local_file_database(self, location: str) -> FileDatabase:
        # JSON
        if location.endswith(".json"):
            self._log.info(
                f"Creating a JSON file database using the file at: {location}"
            )
            return JsonFileDatabase(self.bot, self.cog, path=location)
        # YAML
        elif location.endswith((".yaml", ".yml")):
            self._log.info(
                f"Creating a YAML file database using the file at: {location}"
            )
            return YamlFileDatabase(self.bot, self.cog, path=location)
        # Anything else is unsupported.
        else:
            raise ValueError(
                f"Unsupported file type for file database cog <{self.cog.qualified_name}>: {location}"
            )

    async def dirty(self):
        if self._database.persistent:
            serialized = await self.serialize()
            await self._database.write(serialized)
