from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

import redis
import fakeredis

APP_ENV = os.getenv("APP_ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis client setup
if APP_ENV == "development":
    redis_client = fakeredis.FakeStrictRedis()
else:
    redis_client = redis.Redis.from_url(REDIS_URL)