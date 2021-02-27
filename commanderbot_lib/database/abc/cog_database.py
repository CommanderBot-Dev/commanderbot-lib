from discord.ext.commands import Bot, Cog

from commanderbot_lib.logging import Logger, get_clogger
from commanderbot_lib.mixins.async_init_mixin import AsyncInitMixin


class CogDatabase(AsyncInitMixin):
    """
    This class is used to abstract away the data persistence layer from `Store` logic. It is
    responsible solely for keeping the database sycnhronized with local state, such as by:
    - reading/writing files from/to disk; or
    - invoking database commands; or
    - sending HTTP requests.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    """

    def __init__(self, bot: Bot, cog: Cog):
        self.bot: Bot = bot
        self.cog: Cog = cog
        self._log: Logger = get_clogger(self.cog)

    # @overrides AsyncInitMixin
    async def _async_init(self):
        pass
