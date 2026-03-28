from fastapi import FastAPI
from .database import init_db

app = FastAPI(
    title="Genderize Service",
    description="A service to determine the gender of a name using both a local dataset and an external API.",
    version="1.0.0",
)

init_db()

