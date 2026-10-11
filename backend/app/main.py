from app.api import analyze, audit, health
from fastapi import FastAPI

app = FastAPI(title="Risk Detection API")

app.include_router(health.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
