"""Flask extensions initialization"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail

# Database
db = SQLAlchemy()

# JWT
jwt_manager = JWTManager()

# Mail
mail = Mail()

