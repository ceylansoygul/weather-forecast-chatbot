"""Activity-specific weather thresholds used by the assessment rules."""

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

def assess_activity_weather(
    activity,
    temperature,
    wind_speed,
    precipitation_probability,
    weather_description=None
):
    """Assess forecast conditions against the selected activity profile.

    Args:
        activity: Name of the outdoor activity.
        temperature: Representative temperature in degrees Celsius.
        wind_speed: Maximum wind speed in kilometres per hour.
        precipitation_probability: Maximum precipitation probability in percent.
        weather_description: Optional summary of the forecast conditions.

    Returns:
        dict: Activity, weather values, identified concerns, and a summary.

    The thresholds are application heuristics, not official safety standards.
    """
    activity_key = activity.lower().strip()

    if activity_key not in ACTIVITY_PROFILES:
        # Generic outdoor-tour profile for an unlisted activity.
        activity_key = "outdoor tour"

    profile = ACTIVITY_PROFILES[activity_key]
    concerns = []

    if temperature < profile["low_temp_c"]:
        concerns.append("low temperature")

    if temperature > profile["high_temp_c"]:
        concerns.append("high temperature")

    if wind_speed > profile["max_wind_kmh"]:
        concerns.append("strong wind")

    if precipitation_probability > profile["max_rain_probability"]:
        concerns.append("high precipitation probability")

    return {
        "activity": activity_key,
        "temperature_c": round(temperature, 1),
        "wind_kmh": round(wind_speed, 1),
        "precipitation_probability": round(
            precipitation_probability, 1
        ),
        "weather_description": weather_description,
        "concerns": concerns,
        "summary": (
            "Main factors: " + ", ".join(concerns)
            if concerns
            else "No major weather concern identified by the prototype rules."
        )
    }

