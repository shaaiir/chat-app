from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()
socketio = SocketIO()

def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load config
    if isinstance(config_name, str):
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config_name)
    
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register routes
    from app.routes.auth import auth_bp
    from app.routes.friends import friends_bp
    from app.routes.chat import chat_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp)
    
    # Register SocketIO events
    from app import socketio_events
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
