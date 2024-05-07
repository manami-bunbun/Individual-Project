import os
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.environ.get('ID', None)
CLIENT_SECRET = os.environ.get('SECRET', None)
