import os

from dotenv import load_dotenv

load_dotenv('.env')

SECRET_KEY: str = os.getenv('SECRET_KEY', '')
ALGORITHM: str = os.getenv('ALGORITHM', '')
DATA_SOURCE: str = os.getenv('DATA_SOURCE', '')
