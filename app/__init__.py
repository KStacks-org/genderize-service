from fastapi import FastAPI
from .database import init_db
from .logging import setup_logging
app = FastAPI(
    title="Genderize Service",
    description="A service to determine the gender of a name using both a local dataset and an external API.",
    version="1.0.1",
)

setup_logging(app)
init_db()

