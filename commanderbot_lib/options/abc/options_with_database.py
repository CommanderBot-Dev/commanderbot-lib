from abc import abstractmethod
from typing import Any

from commanderbot_lib.options.abc.cog_options import CogOptions


class OptionsWithDatabase(CogOptions):
    @property
    @abstractmethod
    def database(self) -> Any:
        """ Return the options necessary to instantiate a `CogDatabase`. """
