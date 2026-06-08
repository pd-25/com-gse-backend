from fastapi import FastAPI
from app.core.config import settings
# from db.session import engine
# from db.base import Base
from app.routes.base import api_router

def include_router(app):
    app.include_router(api_router)
    
    
def start_application():
    app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)
    include_router(app)
    # create_tables()
    return app

app = start_application()

@app.get("/")
def hello():
    return {"msg": "Welcome to WirePy and gretings from Pradipta Bhuin, the FastAPI boilerplate for building APIs with Python."}