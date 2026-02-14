"""Creation of a SQLAlchemy Engine for the local Postgres used in docker-compose."""
from sqlalchemy import create_engine
import os

# read from environment with sensible defaults that match your docker-compose .env
DB_USER = os.getenv("POSTGRES_USER", "platform_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "platform_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "platform_db")

# explicit driver ensures compatibility with pip package we install below
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# create_engine is lazy — use `engine.begin()` when executing statements
engine = create_engine(DATABASE_URL, future=True)
