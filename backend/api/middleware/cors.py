"""Middleware for setting CORS headers

This middleware sets the necessary CORS headers for cross-origin resource
sharing. This is necessary for the frontend to make requests to the backend
when hosted on a different domain.

The middleware sets the following headers:
    - Access-Control-Allow-Origin: *
    - Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
    - Access-Control-Allow-Headers: Content-Type, Authorization

The middleware also sets the CORS preflight response to 204 No Content.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI) -> None:
    """Set up CORS middleware for the application"""

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
