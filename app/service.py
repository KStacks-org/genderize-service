import time
import requests
from app.constants import API_URL, API_SOURCE_NAME, DEFAULT_DATA_SOURCE_NAME
import app.database as db
# from .extensions import redis_client

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
    
    db.add_or_update_settings("external_api_limit_exceeded", str(reset_seconds))

def _is_limit_exceeded() -> bool:
    info = db.get_settings("external_api_limit_exceeded")
    if info:
        try:
            reset_time = int(info)
            if time.time() < reset_time:
                return True
            else:
                db.add_or_update_settings("external_api_limit_exceeded", None)
        except ValueError:
            db.add_or_update_settings("external_api_limit_exceeded", None)
            print("Invalid reset time format in database. Resetting limit exceeded flag.")
    return False # not exceeded

def genderize_by_api(name: str) -> dict:
    if _is_limit_exceeded():
        return _format_error_response(429, "API rate limit exceeded. Please try again later.")

    response = requests.get(API_URL, params={"name": name})
    headers = response.headers
    response_json = response.json()

    if response.status_code == 429:
        reset_seconds = headers.get("x-rate-limit-reset", 3600)
        
        # check if reset_seconds is correct type
        if isinstance(reset_seconds, str) and reset_seconds.isdigit():
            reset_seconds = int(reset_seconds)
        elif not isinstance(reset_seconds, int):
            reset_seconds = 3600
        
        reset_seconds = int(time.time() + reset_seconds)
        _set_limit_exceeded(reset_seconds)

        return _format_error_response(429, "API rate limit exceeded. Please try again later.")
    
    elif response.status_code != 200:
        return _format_error_response(response.status_code, f"API request failed with status code {response.status_code}")

    return _format_response(**response_json, source=API_SOURCE_NAME)

def genderize_by_database(name: str) -> dict:
    result = db.get_result_by_name(name)
    if result:
        return _format_response(**result.to_dict())
    return _format_error_response(status_code=404, error_message="Name not found in dataset.")

def genderize(name: str) -> dict:
    database_result = genderize_by_database(name)
    if "error" not in database_result:
        return database_result

    api_result = genderize_by_api(name)
    if "error" in api_result:
        if api_result["status_code"] == 429:
            return _format_error_response(503, "Service temporarily unavailable due to API rate limit. Please try again later.")
    
    db.save_result(
        name=api_result["name"],
        gender=api_result["gender"],
        probability=api_result["probability"],
        source=api_result["source"]
    )
    return api_result