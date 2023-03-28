import abc


class BaseStore(abc.ABC):
    @abc.abstractmethod
    async def connect(self) -> None:
        ...

    @abc.abstractmethod
    async def disconnect(self) -> None:
        ...
