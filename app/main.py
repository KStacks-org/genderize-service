from fastapi.responses import JSONResponse
from app import service
from . import app

@app.get("/genderize")
async def genderize(name: str, country_id: str = None):
    name = name.strip().lower()
    result = service.genderize(name, country_id=country_id)
    if "error" in result:
        return JSONResponse(status_code=result.get("status_code", 500), content=result)
    return JSONResponse(content=result)


# kubernetes liveness and readiness probes
@app.get("/health/liveness")
async def liveness():
    return JSONResponse(content={"status": "alive"})

@app.get("/health/readiness")
async def readiness():
    try:
        # Perform a simple database query to check if the database connection is healthy
        service.check_database_connection()
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unready", "error": str(e)})
    return JSONResponse(content={"status": "ready"})
