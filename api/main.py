from fastapi import FastAPI
import logging.config
import json
from prometheus_fastapi_instrumentator import Instrumentator

# Load logging configuration
try:
    with open("logging_config.json", "r") as f:
        logging_config = json.load(f)
    logging.config.dictConfig(logging_config)
except FileNotFoundError:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.warning("logging_config.json not found, using basic logging configuration.")

logger = logging.getLogger("api")

app = FastAPI(
    title="AI Artist System API",
    description="API for managing AI artists, tracks, and evolution.",
    version="0.1.0"
)

# Instrument the app with Prometheus metrics
Instrumentator().instrument(app).expose(app)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the AI Artist System API"}

# Add other endpoints here...
# Example:
# from .routers import artists, tracks
# app.include_router(artists.router)
# app.include_router(tracks.router)

logger.info("API application started.")

# To run this (assuming file is at api/main.py):
# uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

