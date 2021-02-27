from datetime import datetime
from typing import Generic, TypeVar

from discord import Guild, Member, Message, Reaction
from discord.abc import Messageable
from discord.ext.commands import Bot, Cog

from commanderbot_lib.logging import Logger, get_clogger
from commanderbot_lib.mixins.async_init_mixin import AsyncInitMixin
from commanderbot_lib.options.abc.cog_options import CogOptions
from commanderbot_lib.store.abc.cog_store import CogStore
from commanderbot_lib.types import MemberOrUser

OptionsType = TypeVar("OptionsType", bound=CogOptions)
StoreType = TypeVar("StoreType", bound=CogStore)


class CogGuildState(AsyncInitMixin, Generic[OptionsType, StoreType]):
    """
    This class is used to hold state-related data not only for a particular cog, but also for a
    particular guild. This is useful in reducing the amount of boilerplate code that would
    otherwise be used to repeatedly access the guild being managed.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    options: :class:`OptionsType`
        A set of static configuration options for the cog.
    guild: :class:`Guild`
        The discord.py guild being managed.
    store: :class:`StoreType`
        The store being used to manage data.
    """

    def __init__(
        self, bot: Bot, cog: Cog, options: OptionsType, guild: Guild, store: StoreType
    ):
        self.bot: Bot = bot
        self.cog: Cog = cog
        self.options: OptionsType = options
        self.guild: Guild = guild
        self.store: StoreType = store
        self._log: Logger = get_clogger(self.cog, guild=self.guild)

    # @implements AsyncInitMixin
    async def _async_init(self):
        pass

    # @@ HANDLERS

    async def on_connect(self):
        """ Optional override to handle `on_connect` events. """

    async def on_disconnect(self):
        """ Optional override to handle `on_disconnect` events. """

    async def on_ready(self):
        """ Optional override to handle `on_ready` events. """

    async def on_resumed(self):
        """ Optional override to handle `on_resumed` events. """

    async def on_typing(self, channel: Messageable, user: MemberOrUser, when: datetime):
        """ Optional override to handle `on_typing` events. """

    async def on_message(self, message: Message):
        """ Optional override to handle `on_message` events. """

    async def on_message_delete(self, message: Message):
        """ Optional override to handle `on_message_delete` events. """

    async def on_message_edit(self, before: Message, after: Message):
        """ Optional override to handle `on_message_edit` events. """

    async def on_reaction_add(self, reaction: Reaction, user: MemberOrUser):
        """ Optional override to handle `on_reaction_add` events. """

    async def on_reaction_remove(self, reaction: Reaction, user: MemberOrUser):
        """ Optional override to handle `on_reaction_remove` events. """

    async def on_member_join(self, member: Member):
        """ Optional override to handle `on_member_join` events. """

    async def on_member_remove(self, member: Member):
        """ Optional override to handle `on_member_remove` events. """

    async def on_member_update(self, before: Member, after: Member):
        """ Optional override to handle `on_member_update` events. """

    async def on_user_update(self, before: Member, after: Member):
        """ Optional override to handle `on_user_update` events. """

    async def on_member_ban(self, guild: Guild, user: MemberOrUser):
        """ Optional override to handle `on_member_ban` events. """

    async def on_member_unban(self, guild: Guild, user: MemberOrUser):
        """ Optional override to handle `on_member_unban` events. """
