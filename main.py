import uvicorn
import logging
from dotenv import load_dotenv
load_dotenv()
from logic.router import app


logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
