from datetime import datetime
from typing import Dict, Generic, Iterable, Optional, Type, TypeVar

from commanderbot_lib.guild_state.abc.cog_guild_state import CogGuildState
from commanderbot_lib.logging import Logger, get_clogger
from commanderbot_lib.mixins.async_init_mixin import AsyncInitMixin
from commanderbot_lib.options.abc.cog_options import CogOptions
from commanderbot_lib.store.abc.cog_store import CogStore
from commanderbot_lib.types import GuildID, MemberOrUser
from discord import Guild, Member, Message, Reaction, TextChannel, User
from discord.abc import Messageable
from discord.ext.commands import Bot, Cog

OptionsType = TypeVar("OptionsType", bound=CogOptions)
StoreType = TypeVar("StoreType", bound=CogStore)
GuildStateType = TypeVar("GuildStateType", bound=CogGuildState)


class CogState(AsyncInitMixin, Generic[OptionsType, StoreType, GuildStateType]):
    """
    This class is used to hold state-related data for a particular cog. This data is maintained
    separately, as a component of the cog, to help keep the cog's namespace clean for other things
    like listeners and commands.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    options: :class:`OptionsType`
        A set of static configuration options for the cog. These are used to do thigs like configure
        global behaviour, populate an initial set of data, and/or initialize a database connection.
    store: :class:`StoreType`
        The store being used to manage data.
    """

    # The class responsible for creating the store object.
    # TODO Can we determine this automatically via reflection? #refactor
    store_class: Type[StoreType] = CogStore

    # The class responsible for creating guild state objects.
    # TODO Can we determine this automatically via reflection? #refactor
    guild_state_class: Type[GuildStateType] = CogGuildState

    def __init__(self, bot: Bot, cog: Cog, options: OptionsType):
        self.bot: Bot = bot
        self.cog: Cog = cog
        self.options: OptionsType = options
        self._log: Logger = get_clogger(self.cog)
        self._store: StoreType = None
        self._guild_state_by_id: Dict[GuildID, GuildStateType] = {}

    @property
    def store(self) -> StoreType:
        if not self._store:
            raise ValueError("Tried to access store before it was created")
        return self._store

    @property
    def available_guild_states(self) -> Iterable[GuildStateType]:
        yield from self._guild_state_by_id.values()

    # @implements AsyncInitMixin
    async def _async_init(self):
        self._store = self.store_class(self.bot, self.cog, self.options)
        await self._store.async_init()

    async def get_guild_state(self, guild: Optional[Guild]) -> Optional[GuildStateType]:
        if guild and self.should_ack_guild(guild):
            # Lazy-load guild states as they are accessed.
            guild_state = self._guild_state_by_id.get(guild.id)
            if not guild_state:
                guild_state = await self.init_guild_state(guild)
            return guild_state

    async def set_guild_state(self, guild: Guild, state: GuildStateType):
        if guild.id in self._guild_state_by_id:
            raise KeyError(f"Attempted to overwrite state for guild: {guild}")
        self._guild_state_by_id[guild.id] = state

    async def create_guild_state(self, guild: Guild) -> GuildStateType:
        guild_state: GuildStateType = self.guild_state_class(
            self.bot, self.cog, self.options, guild, self.store
        )
        await guild_state.async_init()
        return guild_state

    async def init_guild_state(self, guild: Guild) -> GuildStateType:
        self._log.info(f"Initializing state for guild: {guild}")
        try:
            guild_state = await self.create_guild_state(guild)
            await self.set_guild_state(guild, guild_state)
            return guild_state
        except:
            self._log.exception(f"Failed to initialize state for guild: {guild}")

    def should_ack_guild(self, guild: Guild) -> bool:
        # TODO Implement extension enable/disable on a per-guild basis. #enhance
        return True

    def should_ack_user(self, user: User) -> bool:
        # TODO Implement user ignore list. (Per-extension? Per-guild?) #enhance
        # Ignore the bot itself.
        return user != self.bot.user

    def should_ack_channel(self, channel: Messageable) -> bool:
        # TODO Implement support for DMs and group chats (private channels). #enhance
        # Ignore DMs and group chats.
        return isinstance(channel, TextChannel)

    def should_ack_message(self, message: Message) -> bool:
        return self.should_ack_user(message.author) and self.should_ack_channel(message.channel)

    # @@ HOOKS

    async def on_connect(self):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_connect """
        for guild_state in self.available_guild_states:
            guild_state.on_connect()

    async def on_disconnect(self):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_disconnect """
        for guild_state in self.available_guild_states:
            guild_state.on_disconnect()

    async def on_ready(self):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_ready """
        for guild_state in self.available_guild_states:
            guild_state.on_ready()

    async def on_resumed(self):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_resumed """
        for guild_state in self.available_guild_states:
            guild_state.on_resumed()

    async def on_typing(self, channel: Messageable, user: MemberOrUser, when: datetime):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_typing """
        if self.should_ack_user(user) and self.should_ack_channel(channel):
            if guild_state := await self.get_guild_state(channel.guild):
                await guild_state.on_typing(channel, user, when)

    async def on_message(self, message: Message):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message """
        if self.should_ack_message(message):
            if guild_state := await self.get_guild_state(message.channel.guild):
                await guild_state.on_message(message)

    async def on_message_delete(self, message: Message):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message_delete """
        if self.should_ack_message(message):
            if guild_state := await self.get_guild_state(message.guild):
                await guild_state.on_message_delete(message)

    async def on_message_edit(self, before: Message, after: Message):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message_edit """
        if self.should_ack_message(after):
            if guild_state := await self.get_guild_state(after.guild):
                await guild_state.on_message_edit(before, after)

    async def on_reaction_add(self, reaction: Reaction, user: MemberOrUser):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_reaction_add """
        if self.should_ack_user(user) and self.should_ack_channel(reaction.message.channel):
            if guild_state := await self.get_guild_state(reaction.message.channel.guild):
                await guild_state.on_reaction_add(reaction, user)

    async def on_reaction_remove(self, reaction: Reaction, user: MemberOrUser):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_reaction_remove """
        if self.should_ack_user(user) and self.should_ack_channel(reaction.message.channel):
            if guild_state := await self.get_guild_state(reaction.message.channel.guild):
                await guild_state.on_reaction_remove(reaction, user)

    async def on_member_join(self, member: Member):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_join """
        if self.should_ack_user(member):
            if guild_state := await self.get_guild_state(member.guild):
                await guild_state.on_member_join(member)

    async def on_member_remove(self, member: Member):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_remove """
        if self.should_ack_user(member):
            if guild_state := await self.get_guild_state(member.guild):
                await guild_state.on_member_remove(member)

    async def on_member_update(self, before: Member, after: Member):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_update """
        if self.should_ack_user(after):
            if guild_state := await self.get_guild_state(after.guild):
                await guild_state.on_member_update(before, after)

    async def on_user_update(self, before: Member, after: Member):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_user_update """
        if self.should_ack_user(after):
            if guild_state := await self.get_guild_state(after.guild):
                await guild_state.on_user_update(before, after)

    async def on_member_ban(self, guild: Guild, user: MemberOrUser):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_ban """
        if self.should_ack_user(user):
            if guild_state := await self.get_guild_state(guild):
                await guild_state.on_member_ban(guild, user)

    async def on_member_unban(self, guild: Guild, user: MemberOrUser):
        """ See: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_unban """
        if self.should_ack_user(user):
            if guild_state := await self.get_guild_state(guild):
                await guild_state.on_member_unban(guild, user)
