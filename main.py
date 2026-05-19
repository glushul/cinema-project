from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import db_manager, Base
from endpoints import auth, catalog, seed, subscription

app = FastAPI(title="Cinema Lab System")
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=db_manager._engine)

app.include_router(seed.router)
app.include_router(auth.router)
app.include_router(subscription.router)
app.include_router(catalog.router)

@app.get("/")
def read_root():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/api/status")
def api_status():
    return {"message": "Cinema API is running. Go to /seed to populate DB."}
