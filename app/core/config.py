# app/core/config.py
import os
from dotenv import load_dotenv

# as config is not where main.py, so we have to declaer the path
from pathlib import Path

env_path = Path(".") / ".env"
# print(env_path)
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_TITLE: str = "Pradipta Blog Apis"
    PROJECT_VERSION: str = "0.1.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
