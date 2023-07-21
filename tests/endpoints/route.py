from __future__ import annotations

from typing import Any, Generic, Optional, Tuple, Type, TypeVar

import httpx

from schemas import ApplicationResponse

T = TypeVar("T")


class Route(Generic[T]):
    __url__: str
    __method__: str
    __response__: Type[ApplicationResponse[T]]

    async def response(
        self,
        client: httpx.AsyncClient,
        *,
        files: Optional[Any] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        params: Optional[Any] = None,
        headers: Optional[Any] = None,
        cookies: Optional[Any] = None,
    ) -> Tuple[ApplicationResponse[T], httpx.Response]:
        response = await client.request(
            method=self.__method__,
            url=self.__url__,
            files=files,
            json=json,
            data=data,
            params=params,
            headers=headers,
            cookies=cookies,
        )

        return ApplicationResponse[self.__response__].parse_obj(response.json()), response
