from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.settings import settings
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
