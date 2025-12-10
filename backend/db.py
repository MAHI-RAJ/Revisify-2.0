"""
Database initialization / bootstrap.

Usage (app.py):
    from db import init_db
    init_db(app)

IMPORTANT:
- create_all() only creates tables for models that have been imported.
  So we import models inside the app_context before create_all().
"""

from extensions import db


def init_db(app):
    """Bind SQLAlchemy to Flask app and create tables (MVP-style)."""
    # Safe to call even if you already called db.init_app(app) elsewhere.
    db.init_app(app)

    with app.app_context():
        # Ensure models are registered before create_all()
        import models  # noqa: F401
        db.create_all()
