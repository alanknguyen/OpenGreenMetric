"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="OpenGreenMetric API",
    description="Open-source Life Cycle Assessment engine for consumer products",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "OpenGreenMetric API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": [
            "POST /api/v1/analyze",
            "GET /api/v1/benchmarks",
            "GET /api/v1/benchmarks/{category}",
            "GET /api/v1/compare?products=a,b,c",
            "GET /api/v1/factors/{type}",
        ],
    }
