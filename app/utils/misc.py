from typing import Callable

from typing_ import DictStrAny


async def result_as_dict(func: Callable, key_name: str, **kwargs) -> DictStrAny:
    result = await func(**kwargs)
    return {key_name: result}
