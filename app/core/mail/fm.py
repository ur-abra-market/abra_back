from fastapi_mail import FastMail

from .config import CONNECTION_CONFIG

fm = FastMail(config=CONNECTION_CONFIG)
