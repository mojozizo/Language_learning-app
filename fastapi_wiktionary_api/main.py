"""
Main entry point for the FastAPI Wiktionary API application.
"""
from fastapi import FastAPI
from routes import dictionary  


app = FastAPI(
    title="Wiktionary API",
    description="API for word definitions and pronunciations using Wiktionary",
    version="1.0.0"
)

app.include_router(dictionary.router, prefix="/api/v1", tags=["dictionary"])
