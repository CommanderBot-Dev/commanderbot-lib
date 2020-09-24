class AsyncInitMixin:
    async def async_init(self):
        """ Call this from outside the object to initialize it asynchronously. """
        await self.before_async_init()
        await self._async_init()
        await self.after_async_init()

    async def _async_init(self):
        """
        Override this in the base class to do some asynchronous initialization, such as calling
        `async_init()` on other `AsyncInitMixin` objects.
        """

    async def before_async_init(self):
        """ Override this in a subclass to do stuff before asynchronous initialization. """

    async def after_async_init(self):
        """ Override this in a subclass to do stuff after asynchronous initialization. """
