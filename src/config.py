from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST", "localhost")
PORT = os.getenv("DB_PORT", "5432")
DBNAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False