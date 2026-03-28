### Genderize Service

This service provides an API to determine the gender of a given name using the Genderize.io API. It also implements rate limit handling to ensure that the service does not exceed the limits set by the external API.

## Features
- Determine gender of a name using Genderize.io API
- Handle API rate limits gracefully
- Store API limit status in the database

## Installation
1. Clone the repository:
```bash
git clone <repository-url>
```
2. Navigate to the project directory:
```bash
cd genderize-service
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Environment Variables
- `DATABASE_URL`: The URL for the database connection (e.g., `sqlite:///./genderize.db` or `postgresql://user:password`).
- `GENDERIZE_API_KEY`: (Optional) Your API key for Genderize.io if you have one. This can help increase your rate limits.

## Usage
1. Start the FastAPI server:
- test mode
```bash
fastapi dev app.main:app --reload
```
- production mode
```bash
gunicorn -w 2 \
         -k uvicorn.workers.UvicornWorker \
         app.main:app \
         --bind 0.0.0.0:8000 \
         --max-requests 1000 \
         --access-logfile - \
         --error-logfile -
```

2. Send a GET request to the endpoint with a name parameter:
```bash
curl -X GET "http://localhost:8000/genderize?name=Yasser"
```

## Response Format
The API will return a JSON response with the following format:
```json
{
    "name": "Yasser",
    "gender": "male",
    "probability": 1.0,
    "source": "api.genderize.io OR reviewed_data"
}
```

## Parameters
- `name` (required): The name for which you want to determine the gender.
- `country_id` (optional): The country code to improve accuracy (e.g., "SA", "US"). See [Genderize.io list of supported countries](https://genderize.io/our-data).

## Error Handling
### API Rate Limit Handling
If the API rate limit is exceeded, the service will return a **503** status code with a message indicating that the limit has been exceeded and when it will reset.
```json
{
    "error": "Service temporarily unavailable due to API rate limit. Please try again later."
}
```
### Can't determine gender
If the service cannot determine the gender of the name, it will return a response with the gender set to `null` and a probability of 0.0.
```json
{
    "name": "UnknownName",
    "gender": null,
    "probability": 0.0,
    "source": "api.genderize.io"
}
```

### Other errors
For other errors (e.g., invalid input, server errors), the service will return an appropriate status code and error message in the response body.
```json
{
    "error": "Detailed error message here."
}
```