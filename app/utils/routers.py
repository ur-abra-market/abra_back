from typing import TypeVar

from fastapi import FastAPI
from fastapi.routing import APIRoute, APIRouter

ParentT = TypeVar("ParentT", APIRouter, FastAPI)


def remove_trailing_slashes(parent: ParentT) -> ParentT:
    "Removes trailing slashes from all routes in the given router"

    for route in parent.routes:
        if isinstance(route, APIRoute):
            route.path = route.path.rstrip("/")

    return parent