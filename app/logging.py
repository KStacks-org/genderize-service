import logging
from fastapi import Request
from http import HTTPStatus
from .constants import LOGGING_EXCLUDED_PATHS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def setup_logging(app):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        if request.url.path in LOGGING_EXCLUDED_PATHS:
            return await call_next(request)

        logging.info(f"Request: {request.client.host} \"{request.method} {request.url}\"")
        response = await call_next(request)
        response_status = HTTPStatus(response.status_code)

        if response_status >= HTTPStatus.INTERNAL_SERVER_ERROR:
            logging.error(f"{request.client.host} \"{request.method} {request.url}\" {response_status.value} {response_status.phrase}")
        else:
            logging.info(f"{request.client.host} \"{request.method} {request.url}\" {response_status.value} {response_status.phrase}")
        
        return response