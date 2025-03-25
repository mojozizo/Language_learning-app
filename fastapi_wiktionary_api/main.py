"""
Main entry point for the FastAPI Wiktionary API application.
This file initializes the FastAPI application and includes routers.
"""
from fastapi import FastAPI
from routes import dictionary  # Changed from absolute to relative import

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Wiktionary API",
    description="API for word definitions and pronunciations using Wiktionary",
    version="1.0.0"
)

# Include the dictionary router with a prefix and tag for API documentation
app.include_router(dictionary.router, prefix="/api/v1", tags=["dictionary"])
