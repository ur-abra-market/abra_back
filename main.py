import uvicorn
import logging
from dotenv import load_dotenv
load_dotenv()
from logic.router import app


# Possible improvements: reload=CONFIG.get('RELOAD', False); debug=CONFIG.get('DEBUG', False)
# See example: https://github.com/open-genes/open-genes-api/blob/develop/api/main.py
logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
