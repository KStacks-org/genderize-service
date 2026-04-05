import os

API_URL = "https://api.genderize.io/"
API_SOURCE_NAME = "api.genderize.io"
GENDERIZE_API_KEY = os.getenv("GENDERIZE_API_KEY")

DEFAULT_DATA_PATH = "./data/default_data.csv"
DEFAULT_DATA_SOURCE_NAME = "reviewed_dataset"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

LOAD_CSV = os.getenv("LOAD_CSV", "true").lower() == "true"