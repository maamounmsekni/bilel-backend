import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing in your .env file")

# Convert "postgresql://" to "postgresql+psycopg://"
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {}

# Supabase requires SSL
sslmode = os.getenv("DB_SSLMODE", "").strip()
if sslmode:
    connect_args["sslmode"] = sslmode

# Supabase pooler (pgbouncer) on port 6543 => disable prepared statements
if "pooler.supabase.com" in DATABASE_URL or ":6543" in DATABASE_URL:
    connect_args["prepare_threshold"] = 0

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()