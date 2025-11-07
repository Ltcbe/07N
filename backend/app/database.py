import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DB_DSN = os.getenv("DB_DSN", "mariadb+mariadbconnector://irail:irailpwd@db:3306/irail")

# SQLAlchemy async engine via MariaDB Connector/Python doesn't support asyncio driver,
# so we will use sync engine inside threadpool via 'create_engine' if needed.
# For simplicity here, we use sync-style sessionmaker with run_in_threadpool wrappers in endpoints.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DB_DSN, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_session():
    return SessionLocal()
