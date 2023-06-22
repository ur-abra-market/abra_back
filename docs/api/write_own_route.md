# Routers in our application

At the moment we have routers such as categories, common and others. Routers are always called `router`, routers have
their own operating scopes, for example, for `app/api/routers/register.py:router` only works with those actions that are
needed to register (adding a new user, confirming email).

## Write router

We have the task of creating a companies router, first of all we will create a router in `app/api/routers/company.py`:

```python
# app/api/routers/company.py

from fastapi import APIRouter

router = APIRouter()
```

Importing it in the module `app/api/routers/__init__.py`:

```python
# app/api/routers/__init__.py

from .categories import router as categories_router
...
from .company import router as company_router

__all__ = (
    "categories_router",
    ...,
    "company_router",
)
```

Connect it in the main router:

```python
# app/api/api.py

from fastapi import APIRouter

from .routers import (
    categories_router,
    ...,
    company_router,
)

def create_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(categories_router, tags=["categories"], prefix="/categories")
    ...
    api_router.include_router(company_router, tags=["companies"], prefix="/company")

    return api_router
```

Congratulations! You have written your router, to add routes go to `app/api/routers/company.py`.
