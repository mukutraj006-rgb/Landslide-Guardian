import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database.mongodb import db_manager
from .routes import alerts, environment, locations, risk, sos

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Landslide Guardian API",
    description="Software-only AI early-warning and landslide risk monitoring prototype.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations.router, prefix="/api", tags=["Locations"])
app.include_router(environment.router, prefix="/api", tags=["Environment"])
app.include_router(risk.router, prefix="/api", tags=["Risk ML Engine"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(sos.router, prefix="/api", tags=["Citizen SOS"])

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/api/health")
async def health_check():
    db_manager.client.admin.command("ping")
    return {
        "status": "healthy",
        "database": "mongodb_atlas",
        "database_connected": db_manager.is_connected,
        "system": "Landslide Guardian API",
        "mode": "Live weather + explainable prototype ML",
    }


@app.get("/", include_in_schema=False)
async def frontend_home():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
