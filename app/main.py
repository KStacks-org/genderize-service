from fastapi.responses import JSONResponse
from app import service
from . import app
from .logging import logger

@app.get("/genderize")
async def genderize(name: str, country_id: str = None):
    name = name.strip().lower()
    logger.info(f"Received request for name: {name}, country_id: {country_id}")
    result = service.genderize(name, country_id=country_id)
    if "error" in result:
        logger.error(f"Error processing request for name: {name}, country_id: {country_id}. Error: {result['error']}")
        return JSONResponse(status_code=result.get("status_code", 500), content=result)
    logger.info(f"Returning successful response for name: {name}, country_id: {country_id}: {result}")
    return JSONResponse(content=result)


# kubernetes liveness and readiness probes
@app.get("/health/liveness")
async def liveness():
    return JSONResponse(content={"status": "alive"})

@app.get("/health/readiness")
async def readiness():
    try:
        service.check_database_connection()
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unready", "error": str(e)})
    return JSONResponse(content={"status": "ready"})
