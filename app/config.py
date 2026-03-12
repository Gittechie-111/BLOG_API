import os
from dotenv import load_dotenv

#load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Pagination
    ITEMS_PER_PAGE = 20

