from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base  # Importa Base do módulo isolado
from app.config import settings

# Create database engine using Transaction Pooler (IPv4)
engine = create_engine(
    settings.database_url,          # já aponta p/ Supabase pooler 6543 + sslmode=require
    pool_pre_ping=True,
    connect_args={
        "sslmode": "require",
        "prepare_threshold": None,  # Desativa prepared statements automáticos para PgBouncer
    },
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 