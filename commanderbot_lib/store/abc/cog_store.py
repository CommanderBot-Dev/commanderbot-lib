from abc import abstractmethod
from typing import Generic, TypeVar

from discord.ext.commands import Bot, Cog

from commanderbot_lib.database.abc.cog_database import CogDatabase
from commanderbot_lib.logging import Logger, get_clogger
from commanderbot_lib.mixins.async_init_mixin import AsyncInitMixin
from commanderbot_lib.options.abc.cog_options import CogOptions

OptionsType = TypeVar("OptionsType", bound=CogOptions)
DatabaseType = TypeVar("DatabaseType", bound=CogDatabase)


class CogStore(AsyncInitMixin, Generic[OptionsType, DatabaseType]):
    """
    This class is used to manage data for a particular cog, be it a simple in-memory database in
    the form of a dict or a persistent database connection.

    For any given cog it is recommended to override this class to introduce specialized methods for
    handling specific data.

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
        self.bot: Bot = bot
        self.cog: Cog = cog
        self.options: OptionsType = options
        self._log: Logger = get_clogger(self.cog)
        self._database: DatabaseType = None

    @abstractmethod
    async def _create_database(self) -> DatabaseType:
        """ Return a new instance of a `CogDatabase` based on the database options. """

    # @overrides AsyncInitMixin
    async def _async_init(self):
        await self._before_database_init()
        self._database = await self._create_database()
        await self._database.async_init()
        await self._after_database_init()

    async def _before_database_init(self):
        """ Override this to do something before database initialization. """

    async def _after_database_init(self):
        """ Override this to do something after database initialization. """
