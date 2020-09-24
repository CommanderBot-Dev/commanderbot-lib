from abc import abstractmethod
from typing import Generic, TypeVar

from discord.ext.commands import Bot, Cog

from commanderbot_lib.database.abc.dict_database import DictDatabase
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
            return InMemoryDictDatabase(self.bot, self.cog, data={})

        # If database is a dict, use it directly as the initial set of in-memory data.
        elif isinstance(db_options, dict):
            self._log.info(
                f"Creating an in-memory database with {len(db_options)} key(s) of initial data"
            )
            return InMemoryDictDatabase(self.bot, self.cog, data=db_options)

        # If database is a string, use a file database.
        elif isinstance(db_options, str):
            # If database is an HTTP address, use a read-only remote file database.
            if db_options.startswith(("http://", "https://")):
                # JSON
                if db_options.endswith(".json"):
                    self._log.info(
                        f"Creating a remote JSON file database using the file at: {db_options}"
                    )
                    return JsonReadOnlyRemoteFileDatabase(self.bot, self.cog, address=db_options)

                # YAML
                elif db_options.endswith((".yaml", ".yml")):
                    self._log.info(
                        f"Creating a remote file database using the file at: {db_options}"
                    )
                    return YamlReadOnlyRemoteFileDatabase(self.bot, self.cog, address=db_options)

                # Anything else is unsupported.
                else:
                    raise ValueError(
                        f"Unsupported file type for remote file database for cog <{self.cog.qualified_name}>: {db_options}"
                    )

            # If database is any other string, assume it is a file path and use a local file database.

            # JSON
            if db_options.endswith(".json"):
                self._log.info(f"Creating a JSON file database using the file at: {db_options}")
                return JsonFileDatabase(self.bot, self.cog, path=db_options)

            # YAML
            elif db_options.endswith((".yaml", ".yml")):
                self._log.info(f"Creating a file database using the file at: {db_options}")
                return YamlFileDatabase(self.bot, self.cog, path=db_options)

            # Anything else is unsupported.
            else:
                raise ValueError(
                    f"Unsupported file type for file database cog <{self.cog.qualified_name}>: {db_options}"
                )

        # Otherwise, we've got a problem.
        raise ValueError(
            f"Invalid database definition for cog <{self.cog.qualified_name}>: {db_options}"
        )

    # @overrides CachedStore
    async def _after_database_init(self):
        initial_data = await self._database.read()
        self._cache = await self._build_cache(initial_data)

    async def dirty(self):
        if self._database.persistent:
            serialized = await self.serialize()
            await self._database.write(serialized)
