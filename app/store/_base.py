import abc


class BaseStore(abc.ABC):
    @abc.abstractmethod
    async def connect() -> None:
        ...

    @abc.abstractmethod
    async def disconnect() -> None:
        ...
