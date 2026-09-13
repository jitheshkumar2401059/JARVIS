import os
import requests
from dotenv import load_dotenv

from tools.location import find_location, find_location_with_context


load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(
    place: str,
    nearby: str = None,
    district: str = None,
    state: str = None,
    country: str = "India",
):
    """
    Get current weather for a location.
    """

    try:
        if nearby or district or state:
            location = find_location_with_context(
                place=place,
                nearby=nearby,
                district=district,
                state=state,
                country=country,
            )
        else:
            location = find_location(
                place=place,
                nearby=nearby,
                district=district,
                state=state,
                country=country,
            )

        if not location:
            return {
                "status": "location_not_found",
                "place": place,
                "message": (
                    f"I could not locate '{place}'. "
                    "Additional location context is required."
                ),
            }

        # Handle possible spelling match
        if location.get("source") == "Saved_Fuzzy":
            return {
                "status": "possible_match",
                "place": place,
                "suggested_location": location.get("name"),
                "similarity": location.get("similarity"),
                "district": location.get("district"),
                "state": location.get("state"),
                "country": location.get("country"),
                "message": (
                    f"Did you mean {location.get('name')}?"
                ),
            }

        latitude = location["latitude"]
        longitude = location["longitude"]

        weather_url = "https://api.openweathermap.org/data/2.5/weather"

        weather_params = {
            "lat": latitude,
            "lon": longitude,
            "appid": API_KEY,
            "units": "metric",
        }

        response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        source = location.get("source")

        should_save = source not in ("Saved", None)

        return {
            "status": "success",
            "location": location.get("name", place),
            "latitude": latitude,
            "longitude": longitude,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "location_source": source,
            "should_save": should_save,
        }

    except requests.RequestException:
        return {
            "status": "weather_error",
            "message": "The weather service is currently unavailable.",
        }

    except (KeyError, TypeError, ValueError):
        return {
            "status": "weather_error",
            "message": (
                "I received an unexpected response "
                "from the weather service."
            ),
        }


if __name__ == "__main__":

    test_locations = [
        {
            "place": "Chennai"
        },
        {
            "place": "Ooty"
        },
        {
            "place": "Coonoor"
        },
        {
            "place": "New Attuboil",
            "district": "Nilgiris",
            "state": "Tamil Nadu",
        },
        {
            "place": "Mulligoor",
            "nearby": "Ooty",
            "district": "Nilgiris",
            "state": "Tamil Nadu",
        },
    ]

    for location in test_locations:

        print(f"\n--- {location['place']} ---")

        result = get_weather(**location)

        print(result)