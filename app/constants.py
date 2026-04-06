import os

API_URL = "https://api.genderize.io/"
API_SOURCE_NAME = "api.genderize.io"
GENDERIZE_API_KEY = os.getenv("GENDERIZE_API_KEY")

DEFAULT_DATA_PATH = "./data/default_data.csv"
DEFAULT_DATA_SOURCE_NAME = "reviewed_dataset"

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    db_engine = os.getenv("DB_ENGINE")
    db_name = os.getenv("DB_NAME", "genderize.db")

    match db_engine:
        case "sqlite":
            DATABASE_URL = f"{db_engine}:///{db_name}"
        case "postgresql":
            db_user = os.getenv("DB_USER", "")
            db_password = os.getenv("DB_PASSWORD", "")
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            DATABASE_URL = f"{db_engine}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        case None:
            raise ValueError("DB_ENGINE is not set in the environment variables. Please set it to either 'sqlite' or 'postgresql' or set DATABASE_URL.")
        case _:
            raise ValueError(f"Unsupported DB_ENGINE: {db_engine}")

LOAD_CSV = os.getenv("LOAD_CSV", "true").lower() == "true"