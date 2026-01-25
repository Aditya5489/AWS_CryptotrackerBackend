import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-this'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-here-change-this'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")