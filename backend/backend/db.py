"""Database initialization"""
from extensions import db

def init_db(app):
    """Initialize database"""
    with app.app_context():
        db.create_all()

