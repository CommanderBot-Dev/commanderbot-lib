from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Type

from discord.ext.commands import Bot, Cog


class CommanderBotBase(ABC, Bot):
    @property
    @abstractmethod
    def started_at(self) -> datetime:
        ...

    @property
    @abstractmethod
    def connected_since(self) -> datetime:
        ...

    @property
    @abstractmethod
    def uptime(self) -> timedelta:
        ...

    @abstractmethod
    def get_extension_options(self, cog_class: Type[Cog]) -> Optional[dict]:
        ...
