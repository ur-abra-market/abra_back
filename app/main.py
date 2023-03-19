import uvicorn

from app.app import app
from app.core.settings import uvicorn_settings


def main() -> None:
    uvicorn.run(
        app=app,
        host=uvicorn_settings.HOSTNAME,
        port=uvicorn_settings.PORT,
        reload=uvicorn_settings.RELOAD,
    )


if __name__ == "__main__":
    main()
