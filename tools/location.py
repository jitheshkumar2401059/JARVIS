import os
import json
import requests
from dotenv import load_dotenv
from rapidfuzz import process, fuzz

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

SAVED_LOCATIONS_FILE = "data/locations.json"
def save_location(
    name: str,
    latitude: float,
    longitude: float,
    district: str = None,
    state: str = None,
    country: str = None,
):
    """Save a confirmed location to the local JSON database."""

    try:
        with open(SAVED_LOCATIONS_FILE, "r", encoding="utf-8") as file:
            locations = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        locations = {}

    locations[name] = {
        "latitude": latitude,
        "longitude": longitude,
        "district": district,
        "state": state,
        "country": country,
    }

    with open(SAVED_LOCATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(locations, file, indent=4)

    return True


def find_saved_location(place: str):
    """Find a location from our local saved locations."""

    try:
        with open(SAVED_LOCATIONS_FILE, "r", encoding="utf-8") as file:
            locations = json.load(file)

        # Case-insensitive exact match
        for name, location in locations.items():
            if name.lower() == place.strip().lower():
                return {
                    "name": name,
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "source": "Saved",
                    "district": location.get("district"),
                    "state": location.get("state"),
                    "country": location.get("country"),
                }

    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return None
def find_similar_saved_location(place: str, threshold: int = 80):
    """Find a possible spelling match from saved locations."""

    try:
        with open(SAVED_LOCATIONS_FILE, "r", encoding="utf-8") as file:
            locations = json.load(file)

        if not locations:
            return None

        names = list(locations.keys())

        match = process.extractOne(
            place.strip(),
            names,
            scorer=fuzz.WRatio,
        )

        if not match:
            return None

        matched_name, score, _ = match

        if score < threshold:
            return None

        location = locations[matched_name]

        return {
            "name": matched_name,
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "source": "Saved_Fuzzy",
            "district": location.get("district"),
            "state": location.get("state"),
            "country": location.get("country"),
            "similarity": round(score),
        }

    except (FileNotFoundError, json.JSONDecodeError):
        return None


def find_with_nominatim(place: str):
    """Find a location using Nominatim/OpenStreetMap."""

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": place,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }

    headers = {
        "User-Agent": "JARVIS-Personal-Assistant/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    result = results[0]

    return {
        "name": result.get("display_name"),
        "latitude": float(result["lat"]),
        "longitude": float(result["lon"]),
        "source": "Nominatim",
        "address": result.get("address", {}),
    }


def find_with_geoapify(place: str):
    """Find a location using Geoapify."""

    url = "https://api.geoapify.com/v1/geocode/search"

    params = {
        "text": place,
        "apiKey": GEOAPIFY_API_KEY,
        "limit": 1,
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    features = data.get("features", [])

    if not features:
        return None

    properties = features[0]["properties"]

    return {
        "name": properties.get("formatted"),
        "latitude": properties.get("lat"),
        "longitude": properties.get("lon"),
        "source": "Geoapify",
        "city": properties.get("city"),
        "district": (
            properties.get("district")
            or properties.get("county")
            or properties.get("state_district")
        ),
        "state": properties.get("state"),
        "country": properties.get("country"),
    }
def build_location_query(
    place: str,
    nearby: str = None,
    district: str = None,
    state: str = None,
    country: str = "India",
):
    """Build a location search query using available context."""

    parts = [place.strip()]

    if nearby:
        parts.append(nearby.strip())

    if district:
        parts.append(district.strip())

    if state:
        parts.append(state.strip())

    if country:
        parts.append(country.strip())

    return ", ".join(parts)


def find_location(
    place: str,
    nearby: str = None,
    district: str = None,
    state: str = None,
    country: str = "India",
):
    """
    Find a location using the three-layer system.

    1. Saved locations - exact
    2. Saved locations - fuzzy spelling
    3. Nominatim
    4. Geoapify
    """

    place = place.strip()

    if not place:
        return None

    search_place = build_location_query(
        place=place,
        nearby=nearby,
        district=district,
        state=state,
        country=country,
    )

    # 1. Saved locations - exact match
    result = find_saved_location(place)

    if result:
        return result

    # 2. Saved locations - possible spelling match
    result = find_similar_saved_location(place)

    if result:
        return result

    # 3. Nominatim
    try:
        result = find_with_nominatim(search_place)

        if result:
            return result

    except requests.RequestException:
        pass

    # 4. Geoapify
    try:
        result = find_with_geoapify(search_place)

        if result:
            return result

    except requests.RequestException:
        pass

    return None
def find_location_with_context(
    place: str,
    nearby: str = None,
    district: str = None,
    state: str = None,
    country: str = "India",
):
    """
    Find a location using additional context provided by the user.

    The returned location must match the requested district/state/country.
    This prevents unrelated places from being accepted.
    """

    search_place = build_location_query(
        place=place,
        nearby=nearby,
        district=district,
        state=state,
        country=country,
    )

    def matches_context(result):
        """Check whether a geocoder result matches the requested context."""

        if not result:
            return False

        result_district = (
            result.get("district")
            or result.get("county")
            or result.get("state_district")
            or ""
        )

        result_state = result.get("state") or ""
        result_country = result.get("country") or ""

        if district:
            requested_district = district.strip().lower()
            found_district = result_district.strip().lower()

            if (
                requested_district not in found_district
                and found_district not in requested_district
            ):
                return False

        if state:
            requested_state = state.strip().lower()
            found_state = result_state.strip().lower()

            if (
                requested_state not in found_state
                and found_state not in requested_state
            ):
                return False

        if country:
            requested_country = country.strip().lower()
            found_country = result_country.strip().lower()

            if (
                requested_country not in found_country
                and found_country not in requested_country
            ):
                return False

        return True

    # First try Nominatim
    try:
        result = find_with_nominatim(search_place)

        if result and matches_context(result):
            return result

    except requests.RequestException:
        pass

    # Then try Geoapify
    try:
        result = find_with_geoapify(search_place)

        if result and matches_context(result):
            return result

    except requests.RequestException:
        pass

    return None


if __name__ == "__main__":

    test_locations = [
        "Chennai",
        "Ooty",
        "Coonoor",
        "Nilgiris",
        "Gandhipuram, Coimbatore",
        "New Attuboil, Nilgiris",
        "Mulligoor, Ooty, Nilgiris",
    ]

    for place in test_locations:

        print(f"\n--- {place} ---")

        try:
            result = find_location(place)
            print(result)

        except Exception as e:
            print(f"Error: {e}")