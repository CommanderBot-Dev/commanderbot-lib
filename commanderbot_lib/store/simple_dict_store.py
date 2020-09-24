from commanderbot_lib.database.abc.dict_database import DictDatabase
from commanderbot_lib.options.abc.options_with_database import OptionsWithDatabase
from commanderbot_lib.store.abc.cached_store import CachedStore


class SimpleDictStore(CachedStore[OptionsWithDatabase, DictDatabase, dict]):
    # @implements CachedStore
    async def _build_cache(self, data: dict) -> dict:
        return data

    # @implements CachedStore
    async def serialize(self) -> dict:
        return self._cache
