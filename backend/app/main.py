from fastapi import FastAPI
from app.api import health, analyze, audit

app = FastAPI(title="Risk Detection API")

app.include_router(health.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
