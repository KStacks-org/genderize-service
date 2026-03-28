from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.constants import DATABASE_URL

# import redis
# import fakeredis

# APP_ENV = os.getenv("APP_ENV", "dev")

# REDIS_URL = os.getenv("REDIS_URL", None)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis client setup
# if REDIS_URL is None:
#     redis_client = fakeredis.FakeStrictRedis()
# else:
#     redis_client = redis.Redis.from_url(REDIS_URL)