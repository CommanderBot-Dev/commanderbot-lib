from os import PathLike
from typing import Callable, Iterable

from commanderbot_lib.database.abc.file_database import FileDatabase
from discord.ext.commands import Bot, Cog

DataMigration = Callable[["VersionedFileDatabase", dict], None]
DataMigrationCollector = Callable[["VersionedFileDatabase", int, int], Iterable[DataMigration]]


class BackwardsMigrationError(Exception):
    def __init__(self, expected_version: int, actual_version: int):
        super().__init__(
            f"Cannot migrate data backwards from unrecognized future version {actual_version} down"
            f" to expected version {expected_version}."
        )
        self.expected_version: int = expected_version
        self.actual_version: int = actual_version


class FailedMigrationError(Exception):
    def __init__(self, expected_version: int, actual_version: int):
        super().__init__(
            f"Failed to migrate data from version {actual_version} to expected version {expected_version}."
        )
        self.expected_version: int = expected_version
        self.actual_version: int = actual_version


class VersionedFileDatabase(FileDatabase):
    """
    A `FileDatabase` that maintains a versioned set of data. Data is upgraded from one format to
    another automatically when necessary, through the use of pre-programmed migrations.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    path: :class:`PathLike`
        The path to the file on the local filesystem.
    version: :class:`int`
        The expected version of the data
    migrate: :class:`DataMigrationCollector`
        A callable iterator that yields migrations, in the form of `DataMigration`, in the order
        that they are to be applied. `DataMigration` are async functions that take the data and
        transform it in some way.
    persistent: :class:`bool`
        Whether changes should be written back to the file on disk.
    """

    def __init__(
        self,
        bot: Bot,
        cog: Cog,
        path: PathLike,
        version: int,
        migrate: DataMigrationCollector,
        persistent: bool = True,
    ):
        super().__init__(bot, cog, path=path, persistent=persistent)
        assert isinstance(version, int)
        self.version: int = version
        self._migrate: DataMigrationCollector = migrate

    # @overrides FileDatabase
    async def read(self) -> dict:
        # Use the usual read method, but extract and adjust the inner data.
        wrapper_data = await self._read_file()
        actual_version = wrapper_data.get("version", None)
        actual_data = wrapper_data.get("data", {})
        # If no version is defined, assume the entire file is data of the expected version. This is
        # for the convenience of migrating from unversioned data.
        if actual_version is None:
            self._log.warning(f"Data is unversioned! Assuming expected version: {self.version}")
            actual_version = self.version
            actual_data = wrapper_data
            # Create a backup of the old data just in case.
            await self.backup()
            # Immediately write the version back to file.
            await self.write(actual_data)
        # Attempt to migrate the data from one version to another, if necessary.
        elif actual_version < self.version:
            self._log.warning(f"Migrating data from version {actual_version} to {self.version}...")
            # Collect and apply migrations, in order.
            try:
                migrations = list(self._migrate(self, actual_version, self.version))
                if migrations:
                    self._log.warning(f"Applying {len(migrations)} data migrations...")
                    for migration in migrations:
                        self._log.warning(f"[->] {migration.__name__}")
                        await migration(self, actual_data)
            except Exception as ex:
                raise FailedMigrationError(self.version, actual_version) from ex
            # Create a backup of the old data just in case.
            await self.backup()
            # Immediately write the migrated data back to file.
            await self.write(actual_data)
            self._log.warning(f"Data migration complete!")
        # If the actual version is from the future, throw an error.
        elif actual_version > self.version:
            raise BackwardsMigrationError(self.version, actual_version)
        # Return the migrated data, which may or may not be any different from the original.
        return actual_data

    # @overrides FileDatabase
    async def write(self, data: dict):
        wrapper_data = {"version": self.version, "data": data}
        await self._write_file(wrapper_data)
