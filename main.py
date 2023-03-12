import uvicorn

from app.core.settings import uvicorn_settings


# Possible improvements: reload=CONFIG.get('RELOAD', False); debug=CONFIG.get('DEBUG', False)
# See example: https://github.com/open-genes/open-genes-api/blob/develop/api/main.py
if __name__ == "__main__":
    uvicorn.run(app="app.app:app", host="0.0.0.0", port=8000, reload=uvicorn_settings.RELOAD)
