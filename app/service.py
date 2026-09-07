import time
import requests
from app.constants import API_URL, API_SOURCE_NAME, GENDERIZE_API_KEY
import app.database as db
# from .extensions import redis_client
from sqlalchemy import text
from .logging import logger

def _format_response(name: str, gender: str="Unknown", probability: float=0.0, source: str="Unknown", **kwargs) -> dict:
    return {
        "name": name,
        "gender": gender,
        "probability": probability,
        "source": source
    }

def _format_error_response(status_code: int, error_message: str) -> dict:
    return {
        "status_code": status_code,
        "error": error_message
    }

def _set_limit_exceeded(reset_seconds: int) -> dict:
    if isinstance(reset_seconds, str) and reset_seconds.isdigit():
        reset_seconds = int(reset_seconds)
    elif not isinstance(reset_seconds, int):
        return _format_error_response(500, "Invalid reset time format from API.")

    logger.warning(f"API rate limit exceeded. Setting limit exceeded flag with reset time: {reset_seconds} seconds.")
    db.add_or_update_settings("external_api_limit_exceeded", str(reset_seconds))

def _is_limit_exceeded() -> bool:
    info = db.get_settings("external_api_limit_exceeded")
    if info:
        try:
            reset_time = int(info)
            if time.time() < reset_time:
                return True
            else:
                logger.info("API rate limit has reset. Clearing limit exceeded flag.")
                db.add_or_update_settings("external_api_limit_exceeded", None)
        except ValueError:
            logger.warning("Invalid reset time format in database. Resetting limit exceeded flag.")
            db.add_or_update_settings("external_api_limit_exceeded", None)
    return False # not exceeded

def genderize_by_api(name: str, country_id: str = None) -> dict:
    if _is_limit_exceeded():
        return _format_error_response(429, "API rate limit exceeded. Please try again later.")
    
    params = {"name": name}
    if country_id:
        params["country_id"] = country_id
    if GENDERIZE_API_KEY:
        params["apikey"] = GENDERIZE_API_KEY

    response = requests.get(API_URL, params=params)

    headers = response.headers
    response_json = response.json()

    if response.status_code == 429:
        rate_limit_remaining = headers.get("x-rate-limit-remaining")
        rate_limit_reset = headers.get("x-rate-limit-reset", 3600)
        
        if rate_limit_remaining == "0":
            # check if reset_seconds is correct type
            if isinstance(rate_limit_reset, str) and rate_limit_reset.isdigit():
                rate_limit_reset = int(rate_limit_reset)
            elif not isinstance(rate_limit_reset, int):
                rate_limit_reset = 3600
            
            rate_limit_reset = int(time.time() + rate_limit_reset)
            _set_limit_exceeded(rate_limit_reset)

        return _format_error_response(429, "API rate limit exceeded. Please try again later.")
    
    elif response.status_code != 200:
        logger.error(f"External API request failed with status code {response.status_code}: {response.text}")
        return _format_error_response(response.status_code, f"External API request failed with status code {response.status_code}")

    return _format_response(**response_json, source=API_SOURCE_NAME)

def genderize_by_database(name: str) -> dict:
    result = db.get_result_by_name(name)
    if result:
        return _format_response(**result.to_dict())
    logger.info(f"Name: {name} not found in database.")
    return _format_error_response(status_code=404, error_message="Name not found in dataset.")

def genderize(name: str, country_id: str = None) -> dict:
    database_result = genderize_by_database(name)
    if "error" not in database_result:
        logger.info(f"Returning result from database for name: {name}, country_id: {country_id}: {database_result}")
        return database_result
    logger.info(f"Name: {name} not found in database. Querying external API for country_id: {country_id}.")

    api_result = genderize_by_api(name, country_id=country_id)
    if "error" in api_result:
        if api_result["status_code"] == 429:
            if _is_limit_exceeded():
                logger.warning(f"API rate limit exceeded for name: {name}, country_id: {country_id}. Returning 503 Service Unavailable.")
                return _format_error_response(503, "Service temporarily unavailable due to API rate limit. Please try again later.")
            else:
                logger.error(f"API rate limit status is inconsistent for name: {name}, country_id: {country_id}. Returning 500 Internal Server Error.")
                return _format_error_response(500, "API rate limit status is inconsistent. Please try again later.")
        else:
            logger.error(f"Error from external API for name: {name}, country_id: {country_id}. Error: {api_result['error']}")
            return api_result
        
    logger.info(f"External API returned result for name: {name}, country_id: {country_id}: {api_result}")
    logger.info(f"Saving result to database for name: {name}, country_id: {country_id}: {api_result}")
    db.save_result(
        name=api_result["name"],
        gender=api_result["gender"],
        probability=api_result["probability"],
        source=api_result["source"]
    )
    logger.info(f"Result saved to database for name: {name}, country_id: {country_id}: {api_result}")
    return api_result


def check_database_connection():
    try:
        db.SessionLocal().execute(text("SELECT 1"))
    except Exception as e:
        raise ConnectionError(f"Database connection failed: {str(e)}")