import requests
from app.constants import API_URL, API_SOURCE_NAME
from .database import get_result_by_name, save_result

def format_response(name: str, gender: str="Unknown", probability: float=0.0, source: str="Unknown", **kwargs) -> dict:
    return {
        "name": name,
        "gender": gender,
        "probability": probability,
        "source": source
    }

def genderize_by_api(name: str) -> dict:
    response = requests.get(API_URL, params={"name": name})
    if response.status_code != 200:
        return {"error": f"API request failed with status code {response.status_code}"}
    
    response_json = response.json()
    return format_response(**response_json, source=API_SOURCE_NAME)

def genderize_by_dataset(name: str) -> dict:

    result = get_result_by_name(name)
    if result:
        return format_response(**result.to_dict())
    return format_response(name=name, source="dataset")

def genderize(name: str) -> dict:
    dataset_result = genderize_by_dataset(name)
    if dataset_result["gender"] != "Unknown":
        return dataset_result
    api_result = genderize_by_api(name)
    if "error" not in api_result:
        save_result(
            name=api_result["name"],
            gender=api_result["gender"],
            probability=api_result["probability"],
            source=api_result["source"]
        )
    return api_result