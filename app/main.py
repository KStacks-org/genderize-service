from fastapi.responses import JSONResponse
from app import service
from . import app

@app.get("/genderize")
async def genderize(name: str):
    name = name.strip().lower()
    result = service.genderize(name)
    if "error" in result:
        return JSONResponse(status_code=result.get("status_code", 500), content=result)
    return JSONResponse(content=result)
