import os 

class Config:
    SECRET_KEY = "os.environ.get('SECRET_KEY')"
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # In production use environment variable for SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'Config': Config
}