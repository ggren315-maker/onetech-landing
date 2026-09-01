"""Production entry point (gunicorn / Render)."""
from server import app, start_price_updater

start_price_updater()
