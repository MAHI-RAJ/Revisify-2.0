from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from extensions import db, jwt_manager
from models import User
from services.auth_service import AuthService
from functools import wraps

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()

def token_required(f):
    """Decorator to protect routes requiring authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            if not current_user:
                return jsonify({"error": "User not found"}), 401
            request.current_user = current_user
        except Exception as e:
            return jsonify({"error": "Token is invalid", "details": str(e)}), 401
        
        return f(*args, **kwargs)
    return decorated

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """POST /api/auth/signup - Create new user account"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Create user
        user = auth_service.create_user(email=email, password=password, name=name)
        
        # Send verification email
        auth_service.send_verification_email(user)
        
        return jsonify({
            "message": "User created successfully. Please check your email for verification.",
            "user_id": user.id
        }), 201
    
    except Exception as e:
        return jsonify({"error": "Signup failed", "details": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login - Authenticate user and issue JWT"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        if not user.is_verified:
            return jsonify({"error": "Please verify your email before logging in"}), 403
        
        # Generate JWT token
        token = auth_service.generate_token(user)
        
        return jsonify({
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500

@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):
    """GET /api/auth/verify/<token> - Verify email with token"""
    try:
        user = auth_service.verify_email_token(token)
        if user:
            return jsonify({"message": "Email verified successfully"}), 200
        else:
            return jsonify({"error": "Invalid or expired verification token"}), 400
    except Exception as e:
        return jsonify({"error": "Verification failed", "details": str(e)}), 500

@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    """POST /api/auth/resend-verification - Resend verification email"""
    try:
        data = request.get_json()
        email = data.get("email")
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if user.is_verified:
            return jsonify({"message": "Email already verified"}), 200
        
        auth_service.send_verification_email(user)
        return jsonify({"message": "Verification email sent"}), 200
    
    except Exception as e:
        return jsonify({"error": "Failed to resend verification", "details": str(e)}), 500

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user():
    """GET /api/auth/me - Get current authenticated user"""
    try:
        user = request.current_user
        return jsonify({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to get user", "details": str(e)}), 500

@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    """POST /api/auth/logout - Logout (client-side token removal)"""
    # JWT is stateless, so logout is handled client-side by removing token
    return jsonify({"message": "Logged out successfully"}), 200

