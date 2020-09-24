from abc import abstractmethod

from commanderbot_lib.database.abc.cog_database import CogDatabase


class DictDatabase(CogDatabase):
    @property
    @abstractmethod
    def persistent(self) -> bool:
        """ Whether the database should ever attempt to write and persist data. """

    @abstractmethod
    async def read(self) -> dict:
        """
        Read and return data, such as by:
        - reading from a file on disk; or
        - submitting a database query; or
        - sending a GET request over HTTP.
        """

    @abstractmethod
    async def write(self, data: dict):
        """
        Write and persist data, such as by:
        - writing to a file on disk; or
        - committing a database transaction; or
        - sending a POST request over HTTP.
        """
