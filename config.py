import ssl
import os

# Get absolute path to project root
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration with intentionally weak security settings"""
    
    # Flask secret key (weak)
    SECRET_KEY = 'supersecret123'
    
    # Database - use absolute path
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "database", "chat.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SSL/TLS Configuration (VULNERABLE)
    SSL_CERT = 'ssl/weak-cert.pem'
    SSL_KEY = 'ssl/weak-key.pem'
    
    # Weak cipher suites
    SSL_CIPHERS = ':'.join([
        'DES-CBC3-SHA',
        'RC4-SHA',
        'RC4-MD5',
        'NULL-MD5',
        'NULL-SHA',
        'EXPORT',
        'DES-CBC-SHA',
        'EDH-RSA-DES-CBC-SHA'
    ])
    
    SSL_PROTOCOL = ssl.PROTOCOL_SSLv23
    SSL_VERIFY_MODE = ssl.CERT_NONE
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = None
    CORS_ORIGINS = '*'
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
