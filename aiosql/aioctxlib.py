from functools import wraps


class _AioCtxMgr:
    def __init__(self, func, args, kwds):
        self.gen = func(*args, **kwds)
        self.func = func
        self.args = args
        self.kwds = kwds
        doc = getattr(func, "__doc__", None)
        if doc is None:
            doc = type(self).__doc__
        self.__doc__ = doc

    async def __aenter__(self):
        try:
            return await self.gen.__anext__()
        except StopAsyncIteration:
            raise RuntimeError("generator didn't yield") from None

    async def __aexit__(self, typ, value, traceback):
        if typ is None:
            try:
                await self.gen.__anext__()
            except StopAsyncIteration:
                return
            else:
                raise RuntimeError("generator didn't stop")
        else:
            if value is None:
                value = typ()
            # See _GeneratorContextManager.__exit__ for comments on subtleties
            # in this implementation
            try:
                await self.gen.athrow(typ, value, traceback)
                raise RuntimeError("generator didn't stop after throw()")
            except StopAsyncIteration as exc:
                return exc is not value
            except RuntimeError as exc:
                if exc is value:
                    return False
                # Avoid suppressing if a StopIteration exception
                # was passed to throw() and later wrapped into a RuntimeError
                # (see PEP 479 for sync generators; async generators also
                # have this behavior). But do this only if the exception wrapped
                # by the RuntimeError is actully Stop(Async)Iteration (see
                # issue29692).
                if isinstance(value, (StopIteration, StopAsyncIteration)):
                    if exc.__cause__ is value:
                        return False
                raise
            except BaseException as exc:
                if exc is not value:
                    raise


def aiocontextmanager(func):
    @wraps(func)
    def helper(*args, **kwds):
        return _AioCtxMgr(func, args, kwds)

    return helper
