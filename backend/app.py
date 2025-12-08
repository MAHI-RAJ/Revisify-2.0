from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, jwt_manager, mail
import os

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt_manager.init_app(app)
    mail.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    
    # Initialize config (create directories)
    config_class.init_app(app)
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.docs_routes import docs_bp
    from routes.pipeline_routes import pipeline_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(docs_bp, url_prefix="/api/docs")
    app.register_blueprint(pipeline_bp, url_prefix="/api/pipeline")
    
    # Health check endpoint
    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "Revisify 2.0 API is running"}
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)

