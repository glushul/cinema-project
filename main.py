from fastapi import FastAPI
from database import db_manager, Base
from endpoints import catalog, seed, subscription, processes

app = FastAPI(title="Cinema Lab System")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=db_manager._engine)

app.include_router(seed.router)
app.include_router(subscription.router)
app.include_router(catalog.router)
app.include_router(processes.router)

@app.get("/")
def read_root():
    return {"message": "Cinema API is running. Go to /seed to populate DB."}
