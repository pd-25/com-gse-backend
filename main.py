from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
# from db.session import engine
# from db.base import Base
from app.routes.base import api_router

def include_router(app):
    app.include_router(api_router)
    
    
def start_application():
    app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    include_router(app)
    # create_tables()
    return app

app = start_application()

@app.get("/")
def hello():
    return {"msg": "Welcome to WirePy and gretings from Pradipta Bhuin, the FastAPI boilerplate for building APIs with Python."}
