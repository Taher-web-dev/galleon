from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.settings import settings
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    # echo=True,
    # echo_pool="debug",
    pool_size=20,
    max_overflow=30,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


__all__ = ["SessionLocal", "Base"]
