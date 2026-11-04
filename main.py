"""Application entry point for the Weather Forecast Chatbot."""

from config.setup import load_project_environment
from app.ui import render_app


load_project_environment()
render_app()
