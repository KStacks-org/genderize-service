from fastapi.responses import JSONResponse
from app import service
from . import app

@app.get("/genderize")
async def genderize(name: str):
    return JSONResponse(content=service.genderize(name))
