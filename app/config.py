import os

class Config:
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        if self.SQLALCHEMY_DATABASE_URI is None:
            raise ValueError('DATABASE_URL is not set')

        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

        if self.OPENAI_API_KEY is None:
            raise ValueError('OPENAI_API_KEY is not set')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
