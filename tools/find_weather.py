from typing import Any, Optional
from smolagents.tools import Tool
import os

class GetWeatherTool(Tool):
    """
    Retrieves the current weather data for a given location using the OpenWeatherMap API.
    Use this to obtain information such as temperature, humidity, weather description,
    and wind speed for a specified city (optionally including country code).
    """

    name = "get_weather"
    description = (
        "Gets current weather information for a specified location. "
        "Requires an OpenWeatherMap API key set in the environment variable 'OPENWEATHER_API_KEY'. "
        "Returns a formatted string containing temperature (in °C), humidity, weather description, and wind speed."
    )
    inputs = {
        "location": {
            "type": "string",
            "description": "The name of the city (optionally with country code, e.g., 'London,UK') to fetch weather for."
        }
    }
    output_type = "string"

    def forward(self, location: str) -> str:
        try:
            import requests
            from requests.exceptions import RequestException
            from smolagents.utils import truncate_content
        except ImportError as e:
            raise ImportError(
                "You must install `requests` to run this tool (e.g., `pip install requests`)."
            ) from e

        # Retrieve API key from environment
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return (
                "Error: OpenWeatherMap API key not found. "
                "Please set the OPENWEATHER_API_KEY environment variable."
            )

        try:
            # Build request URL
            endpoint = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"
            }

            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Handle API errors (e.g., city not found)
            if data.get("cod") != 200:
                message = data.get("message", "Unknown error occurred.")
                return f"Error fetching weather data: {message}"

            # Parse relevant fields
            city_name = data.get("name", "Unknown location")
            sys_info = data.get("sys", {})
            country = sys_info.get("country", "")
            weather = data.get("weather", [{}])[0]
            description = weather.get("description", "No description")
            main_info = data.get("main", {})
            temp = main_info.get("temp")
            feels_like = main_info.get("feels_like")
            humidity = main_info.get("humidity")
            wind_info = data.get("wind", {})
            wind_speed = wind_info.get("speed")

            # Format output
            output = (
                f"**Weather in {city_name}, {country or 'N/A'}**\n\n"
                f"- Description: {description.capitalize()}\n"
                f"- Temperature: {temp}°C (feels like {feels_like}°C)\n"
                f"- Humidity: {humidity}%\n"
                f"- Wind Speed: {wind_speed} m/s"
            )

            return truncate_content(output, 10000)

        except requests.exceptions.Timeout:
            return "The request timed out. Please try again later."
        except RequestException as e:
            return f"Error fetching weather data: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    def __init__(self, *args: Any, **kwargs: Any):
        self.is_initialized = False
