"""Coordinate request processing, weather retrieval, and response generation."""

import pandas as pd

from app.services.weather_service import (
    normalize_location,
    geocode_location,
    get_weather_forecast,
    select_forecast_period,
    summarize_forecast
)

from app.services.activity_service import assess_activity_weather

from app.services.llm_service import (
    get_client,
    extract_weather_request,
    generate_weather_response
)



def run_chatbot(user_question, conversation_context=""):
    """Process a user question and return a clarification or weather result.

    The function extracts structured request details, asks for missing
    information when necessary, retrieves the forecast, assesses conditions
    for the selected activity, and generates the final response.

    Args:
        user_question: The latest message entered by the user.
        conversation_context: Recent conversation messages used to resolve
            relevant follow-up questions.

    Returns:
        dict: A result containing the response type, answer, and request
        details. Weather results also include the location, forecast,
        and activity assessment.
    """

    client = get_client()

    request = extract_weather_request(
        client,
        user_question,
        conversation_context=conversation_context
    )

    # ---------------------------------------------------------
    # Handle greetings, incomplete requests and non-weather input
    # ---------------------------------------------------------

    location_text = str(
        request.get("location", "")
    ).strip()

    date_text = str(
        request.get("date_iso", "")
    ).strip()

    activity_text = str(
        request.get("activity", "")
    ).strip()

    # No location means that the request cannot yet be sent
    # to the weather/geocoding tool.
    if not location_text:

        if activity_text and date_text:
            clarification = (
                f"I can check the weather for {activity_text}. "
                "Which location should I use?"
            )
        elif activity_text:
            clarification = (
                f"Sure — I can check the weather for {activity_text}. "
                "Which location and date should I use? For example: "
                "'in Berlin tomorrow'."
            )
        else:
            clarification = (
                "Hi! I can help you check the weather for outdoor activities. "
                "Please tell me the activity, location and date. For example: "
                "'Will it rain during my hike in Munich tomorrow?'"
            )

        return {
            "type": "clarification",
            "answer": clarification,
            "request": request
        }

    if not activity_text:
        return {
            "type": "clarification",
            "answer": (
                f"I have the location ({location_text}), but I still need "
                "to know which outdoor activity you are planning and when. "
                "For example: 'hiking tomorrow morning'."
            ),
            "request": request
        }

    # A location without a date is not enough for the
    # forecast-selection step.
    if not date_text:

        return {
            "type": "clarification",
            "answer": (
                f"I can help with the weather in {location_text}. "
                "Please also tell me when you plan to go, for "
                "example 'tomorrow' or 'Saturday morning'."
            ),
            "request": request
        }
    # Retrieve and assess the forecast for the requested period.

    original_location = request["location"]

    request["location"] = normalize_location(
        request["location"]
    )

    location = geocode_location(
        request["location"]
    )

    weather_data = get_weather_forecast(
        latitude=location["latitude"],
        longitude=location["longitude"],
        timezone=location["timezone"],
        forecast_days=7
    )

    forecast_df = pd.DataFrame(
        weather_data["hourly"]
    )

    selected_df = select_forecast_period(
        forecast_df,
        request["date_iso"],
        request["time_period"]
    )

    forecast_summary = summarize_forecast(
        selected_df
    )

    if forecast_summary is None:
        raise ValueError(
            "No forecast data is available for "
            f"{request['date_iso']}."
        )

    average_temperature = (
        forecast_summary["temperature_min_c"]
        + forecast_summary["temperature_max_c"]
    ) / 2

    assessment = assess_activity_weather(
        request["activity"],
        average_temperature,
        forecast_summary[
            "wind_max_kmh"
        ],
        forecast_summary[
            "precipitation_probability_max"
        ],
        ", ".join(
            forecast_summary["conditions"]
        )
    )

    answer = generate_weather_response(
        client,
        user_question,
        request,
        location,
        forecast_summary,
        assessment
    )

    return {
        "type": "weather",
        "answer": answer,
        "request": request,
        "original_location": original_location,
        "location": location,
        "forecast": forecast_summary,
        "assessment": assessment
    }