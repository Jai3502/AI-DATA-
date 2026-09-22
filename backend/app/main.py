from fastapi import FastAPI
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.organizations import router as organization_router
from app.core.database import engine
from app.api.datasets import router as dataset_router
from app.api.analysis import router as analysis_router

app = FastAPI(
    title="AI Data Analyst API",
    version="0.1.0",
)


app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(dataset_router)
app.include_router(analysis_router)

@app.get("/health")
def health_check():

    database_status = "ok"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database_status = "error"

    return {
        "status": "ok",
        "service": "ai-data-analyst-api",
        "database": database_status,
    }