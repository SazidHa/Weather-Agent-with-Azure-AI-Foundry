import os, json, requests
import requests
from dotenv import load_dotenv
load_dotenv()
def fetch_weather(city: str):
    api_key =os.getenv("WEATHERAPI_KEY") 
    if not api_key:
        raise ValueError("WEATHERAPI_KEY not loaded from environment")
    # Example: WeatherAPI-style endpoint
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no"
    }

    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    return {
        "city": data["location"]["name"],
        "region": data["location"]["region"],
        "country": data["location"]["country"],
        "temperature_c": data["current"]["temp_c"],
        "feels_like_c": data["current"]["feelslike_c"],
        "condition": data["current"]["condition"]["text"],
        "wind_kph": data["current"]["wind_kph"],
        "humidity": data["current"]["humidity"],
        "local_time": data["location"]["localtime"]
    }

weather_tool_definition = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for any city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, for example Melbourne or Tokyo"
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            }
        }
    }
]