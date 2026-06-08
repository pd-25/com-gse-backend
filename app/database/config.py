import os
from dotenv import load_dotenv
from pathlib import Path

# as config is not where main.py, so we have to declaer the path
env_path = Path(".") / ".env"
print(env_path)
load_dotenv(dotenv_path=env_path)

class DatabaseConfig:
        MYSQL_USER: str = os.getenv('MYSQL_USER')
        MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
        MYSQL_SERVER: str = os.getenv("MYSQL_SERVER")
        MYSQL_PORT: str = os.getenv("MYSQL_PORT")
        MYSQL_DB: str = os.getenv("MYSQL_DB")
        DATABASE_URL: str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
        
        # Uncomment the following lines if you want to use PostgreSQL instead of MySQL
        # POSTGRES_USER: str = os.getenv("POSTGRES_USER")
        # POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
        # POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
        # POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
        # POSTGRES_DB: str = os.getenv("POSTGRES_DB")
        # DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
        # DATABASE_URL: str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
        
databaseconfig = DatabaseConfig()
# print(databaseconfig.DATABASE_URL)
        
        