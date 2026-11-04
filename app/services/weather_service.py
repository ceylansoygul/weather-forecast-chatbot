"""Retrieve, select, and summarise weather forecast data from Open-Meteo."""

import requests
import pandas as pd

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

ACTIVITY_PROFILES = {
    "hiking": {
        "max_rain_probability": 60,
        "max_wind_kmh": 35,
        "low_temp_c": 0,
        "high_temp_c": 30
    },
    "cycling": {
        "max_rain_probability": 50,
        "max_wind_kmh": 30,
        "low_temp_c": 2,
        "high_temp_c": 32
    },
    "mountain biking": {
        "max_rain_probability": 45,
        "max_wind_kmh": 30,
        "low_temp_c": 0,
        "high_temp_c": 28
    },
    "running": {
        "max_rain_probability": 50,
        "max_wind_kmh": 30,
        "low_temp_c": 0,
        "high_temp_c": 30
    },
    "trail running": {
        "max_rain_probability": 45,
        "max_wind_kmh": 30,
        "low_temp_c": 0,
        "high_temp_c": 28
    },
    "camping": {
        "max_rain_probability": 50,
        "max_wind_kmh": 25,
        "low_temp_c": 5,
        "high_temp_c": 30
    },
    "outdoor tour": {
        "max_rain_probability": 50,
        "max_wind_kmh": 30,
        "low_temp_c": 2,
        "high_temp_c": 32
    },
    "swimming": {
        "max_rain_probability": 40,
        "max_wind_kmh": 25,
        "low_temp_c": 18,
        "high_temp_c": 32
    }
}

REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "activity": {"type": "string"},
        "location": {"type": "string"},
        "date": {"type": "string"},
        "date_iso": {"type": "string"},
        "time_period": {"type": "string"},
        "elevation_m": {"type": ["number", "null"]}
    },
    "required": [
        "activity",
        "location",
        "date",
        "date_iso",
        "time_period",
        "elevation_m"
    ],
    "additionalProperties": False
}

def normalize_location(location):
    """Remove common natural-language prefixes from a place name.

    Args:
        location: Location text supplied by the user.

    Returns:
        str: A cleaned location name suitable for geocoding.
    """
    cleaned = str(location).strip()

    prefixes = [
        "near ",
        "around ",
        "in ",
        "at ",
        "the "
    ]

    changed = True

    while changed:
        changed = False
        lower = cleaned.lower()

        for prefix in prefixes:
            if lower.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                changed = True
                break

    return cleaned

def geocode_location(location):
    """Resolve a place name to coordinates and timezone information.

    The full location is tried first. If it contains multiple words and
    no exact result is found, the first word is also tried as a fallback.

    Args:
        location: Place name supplied by the user.

    Returns:
        dict: Place name, latitude, longitude, country, and timezone.

    Raises:
        ValueError: If no matching location can be found.
        requests.RequestException: If the geocoding request fails.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"

    original_location = normalize_location(location)

    # Try the complete location name before using a shorter fallback.
    search_terms = [original_location]

    # A shorter place name can help resolve descriptions such as "Olpe Bigge See".
    words = original_location.split()

    if len(words) >= 2:
        search_terms.append(words[0])

    # Remove duplicate or empty search terms.
    search_terms = list(dict.fromkeys(
        term.strip()
        for term in search_terms
        if term.strip()
    ))

    for search_term in search_terms:

        params = {
            "name": search_term,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "results" in data and data["results"]:

            result = data["results"][0]

            return {
                "name": result["name"],
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "country": result.get("country"),
                "timezone": result.get(
                    "timezone",
                    "auto"
                )
            }

    raise ValueError(
        f"Location could not be found: {location}"
    )

def get_weather_forecast(
    latitude,
    longitude,
    timezone="auto",
    forecast_days=7
):
    """Retrieve hourly weather data for the specified coordinates.

    Args:
        latitude: Geographic latitude.
        longitude: Geographic longitude.
        timezone: Timezone used for forecast timestamps.
        forecast_days: Number of forecast days to request.

    Returns:
        dict: JSON response from the Open-Meteo Forecast API.

    Raises:
        requests.RequestException: If the forecast request fails.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join([
            "temperature_2m",
            "precipitation_probability",
            "precipitation",
            "weather_code",
            "cloud_cover",
            "wind_speed_10m"
        ]),
        "timezone": timezone,
        "forecast_days": forecast_days,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()
    
def weather_code_to_description(code):
    """Convert an Open-Meteo weather code into a readable description.

    Args:
        code: Numeric weather code returned by the API.

    Returns:
        str: Human-readable weather condition.
    """
    return WEATHER_CODES.get(
        int(code),
        "Unknown weather condition"
    )
def select_forecast_period(
    forecast_df,
    date_iso,
    time_period
):
    """Filter hourly forecast records by date and optional time of day.

    Supported time periods are morning, afternoon, evening, and overnight.
    An empty time period leaves all hours for the selected date.

    Args:
        forecast_df: DataFrame containing hourly forecast records.
        date_iso: Target date in YYYY-MM-DD format.
        time_period: Requested time period.

    Returns:
        pandas.DataFrame: Forecast records matching the requested period.
    """
    df = forecast_df.copy()
    df["datetime"] = pd.to_datetime(df["time"])

    target_date = pd.to_datetime(
        date_iso
    ).date()

    df = df[
        df["datetime"].dt.date == target_date
    ]

    period = time_period.lower().strip()

    if period == "morning":
        df = df[
            df["datetime"].dt.hour.between(6, 11)
        ]

    elif period == "afternoon":
        df = df[
            df["datetime"].dt.hour.between(12, 17)
        ]

    elif period == "evening":
        df = df[
            df["datetime"].dt.hour.between(18, 21)
        ]

    elif period == "overnight":
        df = df[
            (df["datetime"].dt.hour >= 22)
            | (df["datetime"].dt.hour <= 5)
        ]

    return df


def summarize_forecast(selected_df):
    """Aggregate selected hourly records into a concise forecast summary.

    Args:
        selected_df: DataFrame containing the selected forecast hours.

    Returns:
        dict | None: Temperature range, maximum wind and precipitation
        probability, total precipitation, and distinct conditions.
        Returns None when the selection contains no records.
    """
    if selected_df.empty:
        return None

    return {
        "temperature_min_c": round(
            float(selected_df["temperature_2m"].min()), 1
        ),
        "temperature_max_c": round(
            float(selected_df["temperature_2m"].max()), 1
        ),
        "wind_max_kmh": round(
            float(selected_df["wind_speed_10m"].max()), 1
        ),
        "precipitation_probability_max": round(
            float(
                selected_df[
                    "precipitation_probability"
                ].max()
            ), 1
        ),
        "precipitation_total_mm": round(
            float(
                selected_df["precipitation"].sum()
            ), 1
        ),
        "conditions": list(
            dict.fromkeys(
                weather_code_to_description(code)
                for code in selected_df[
                    "weather_code"
                ].astype(int)
            )
        )
    }

