import logging
import requests
import os
import azure.functions as func
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (for local development)
load_dotenv()

app = func.FunctionApp()

@app.route(route="GetWeatherData", auth_level=func.AuthLevel.FUNCTION)
def GetWeatherData(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the city name from the request query parameters
    city = req.params.get('city')
    if not city:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None
        if req_body:
            city = req_body.get('city')

    if not city:
        return func.HttpResponse(
            "Please pass a city name on the query string or in the request body",
            status_code=400
        )

    # Retrieve the OpenWeatherMap API key from environment variables
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        logging.error('OpenWeather API key is not configured.')
        return func.HttpResponse(
            "OpenWeather API key is not configured.",
            status_code=500
        )

    # Construct the API request URL
    weather_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    # Fetch the weather data
    try:
        response = requests.get(weather_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return func.HttpResponse(
            f"Error fetching weather data: {e}",
            status_code=500
        )

    # Return the weather data as JSON
    return func.HttpResponse(response.text, mimetype="application/json")

