from sqlalchemy import create_engine, text

USERNAME = "ottocline"
PASSWORD = "102406"
HOST = "localhost"
DBNAME = "nypl"

DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DBNAME}"

engine = create_engine(DATABASE_URL)

# Load and execute schema.sql
with engine.connect() as conn:
    with open("schema.sql", "r") as f:
        sql_commands = f.read()
    conn.execute(text(sql_commands))  # Can also use conn.exec_driver_sql(sql_commands)
    conn.commit()  # Commit to persist changes

print("Tables created successfully.")