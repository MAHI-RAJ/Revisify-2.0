"""Authentication service"""
from extensions import db
from models import User
from flask_jwt_extended import create_access_token
from datetime import timedelta
from config import Config
from services.email_service import EmailService

class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def create_user(self, email, password, name=None):
        """Create a new user"""
        user = User(email=email, name=name)
        user.set_password(password)
        user.generate_verification_token()
        
        db.session.add(user)
        db.session.commit()
        return user
    
    def generate_token(self, user):
        """Generate JWT token for user"""
        expires = timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        token = create_access_token(
            identity=user.id,
            expires_delta=expires,
            additional_claims={"email": user.email}
        )
        return token
    
    def send_verification_email(self, user):
        """Send email verification"""
        verification_url = f"{Config.FRONTEND_URL}/verify/{user.verification_token}"
        self.email_service.send_verification_email(user.email, verification_url)
    
    def verify_email_token(self, token):
        """Verify email token and mark user as verified"""
        user = User.query.filter_by(verification_token=token).first()
        if user and not user.is_verified:
            user.is_verified = True
            user.verification_token = None
            db.session.commit()
            return user
        return None

