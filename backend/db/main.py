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
    #### A Main Performance Issue ####
    # Connections are in the QueuePool by default. Max connections are pool_size+max_overflow
    # default connections limit in postgres = 100, so I made them 40+60=100
    # for more capacity we'll need to increase postgres limit according to our needs
    # if the app needs more scalability we could use a separate connection pool like PgBouncer https://www.pgbouncer.org/
    # and make pool_size=0 and max_overflow=-1 for unlimited connections
    # Of course this will depend on the server resources & PgBouncer configuration
    # ... more learning is needed here.
    # We mostly need to audit the staging server with those config and load-test different configurations
    # based on users loads speculations and see how things go before going production
    pool_size=40,
    max_overflow=40,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Database Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
