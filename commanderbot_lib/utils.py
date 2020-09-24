from os import PathLike
from pathlib import Path
from typing import Type

from discord.ext.commands import Bot, Cog

from commanderbot_lib.bot.abc.commander_bot_base import CommanderBotBase


def add_configured_cog(bot: Bot, cog_class: Type[Cog]):
    cog = None
    if isinstance(bot, CommanderBotBase):
        options = bot.get_extension_options(cog_class)
        if options:
            cog = cog_class(bot, **options)
    if not cog:
        cog = cog_class(bot)
    bot.add_cog(cog)


def fix_path(path: PathLike) -> Path:
    spath = str(path)
    if spath.startswith("~"):
        return Path.home() / Path("." + spath[1:])
    else:
        return Path(spath).resolve()
