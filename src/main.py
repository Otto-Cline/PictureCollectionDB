from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()  # This loads variables from .env into environment

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
DBNAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DBNAME}"

engine = create_engine(DATABASE_URL)

# Load and execute schema.sql
with engine.connect() as conn:
    with open("schema.sql", "r") as f:
        sql_commands = f.read()
    conn.execute(text(sql_commands))  # Can also use conn.exec_driver_sql(sql_commands)
    conn.commit()  # Commit to persist changes

print("Tables created successfully.")