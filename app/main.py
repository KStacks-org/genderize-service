from fastapi.responses import JSONResponse
from . import app

@app.get("/genderize")
async def genderize(name: str):
    return JSONResponse(content={})