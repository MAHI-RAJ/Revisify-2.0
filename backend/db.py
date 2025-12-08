"""Database initialization"""

from extensions import db

def init_db(app):
    """Initialize database and create tables."""
    # If you already call db.init_app(app) in app.py, you can remove the next line.
    db.init_app(app)

    with app.app_context():
        # IMPORTANT: ensure models are imported so tables are registered
        import models  # noqa: F401
        db.create_all()
