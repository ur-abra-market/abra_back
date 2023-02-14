import uvicorn
from dotenv import load_dotenv

load_dotenv()
from app.settings import RELOAD


# Possible improvements: reload=CONFIG.get('RELOAD', False); debug=CONFIG.get('DEBUG', False)
# See example: https://github.com/open-genes/open-genes-api/blob/develop/api/main.py
if __name__ == "__main__":
    uvicorn.run(app="app.logic.router:app", host="0.0.0.0", port=8000, reload=RELOAD)
