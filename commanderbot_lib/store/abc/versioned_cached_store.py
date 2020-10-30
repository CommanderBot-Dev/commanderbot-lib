from abc import abstractmethod
from typing import Generic, Iterable, TypeVar

from commanderbot_lib.database.abc.dict_database import DictDatabase
from commanderbot_lib.database.abc.versioned_file_database import (
    DataMigration,
    VersionedFileDatabase,
)
from commanderbot_lib.database.json_versioned_file_database import JsonVersionedFileDatabase
from commanderbot_lib.database.yaml_versioned_file_database import YamlVersionedFileDatabase
from commanderbot_lib.options.abc.options_with_database import OptionsWithDatabase
from commanderbot_lib.store.abc.cached_store import CachedStore
from discord.ext.commands import Bot, Cog

OptionsType = TypeVar("OptionsType", bound=OptionsWithDatabase)
DatabaseType = TypeVar("DatabaseType", bound=DictDatabase)
CacheType = TypeVar("CacheType")


class VersionedCachedStore(
    CachedStore[OptionsType, DatabaseType, CacheType], Generic[OptionsType, DatabaseType, CacheType]
):
    """
    A variant of `CachedStore` that expects the underlying database to be versioned.
    """

    @abstractmethod
    def _collect_migrations(
        self,
        database: VersionedFileDatabase,
        actual_version: int,
        expected_version: int,
    ) -> Iterable[DataMigration]:
        """
        Yield a series of `DataMigration`, in order, to transform `data` from `actual_version` into
        `expected_version` so that it may be used to construct an instance of `CacheType` directly.
        """

    @property
    @abstractmethod
    def data_version(self) -> int:
        """ Return the expected version of the underlying database. """

    # @implements CogStore
    async def _create_database(self) -> DatabaseType:
        db_options = self.options.database
        # Currently, we only support VersionedFileDatabase.
        if isinstance(db_options, str):
            return await self._make_versioned_file_database(db_options)
        raise ValueError(
            f"Invalid database definition for cog <{self.cog.qualified_name}>: {db_options}"
        )

    async def _make_versioned_file_database(self, location: str) -> VersionedFileDatabase:
        # JSON
        if location.endswith(".json"):
            self._log.info(f"Creating a versioned JSON file database using the file at: {location}")
            return JsonVersionedFileDatabase(
                self.bot,
                self.cog,
                path=location,
                version=self.data_version,
                migrate=self._collect_migrations,
            )
        # YAML
        elif location.endswith((".yaml", ".yml")):
            self._log.info(f"Creating a versioned YAML file database using the file at: {location}")
            return YamlVersionedFileDatabase(
                self.bot,
                self.cog,
                path=location,
                version=self.data_version,
                migrate=self._collect_migrations,
            )
        # Anything else is unsupported.
        else:
            raise ValueError(
                f"Unsupported file type for versioned file database cog <{self.cog.qualified_name}>: {location}"
            )
