"""Language-model client and request/response functions for the chatbot."""

import os
import json
from openai import OpenAI

# Model used for request extraction and response generation.
MODEL_NAME = "gpt-5-mini"

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

def get_client():
    """Create an OpenAI client using the configured API key.

    Raises:
        ValueError: If OPENAI_API_KEY is not available.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not available. "
            "Set it as an environment variable before starting Streamlit."
        )

    return OpenAI(api_key=api_key)

def extract_weather_request(client, user_question, conversation_context=""):
    """Extract activity, location, date, time, and elevation from a message.

    Previous conversation context is used only to resolve relevant follow-up
    details. The result follows REQUEST_SCHEMA.

    Args:
        client: Configured OpenAI client.
        user_question: Latest user message.
        conversation_context: Recent conversation history.

    Returns:
        dict: Structured weather request fields.
    """
    from datetime import date

    today = date.today()

    instructions = f"""
You are the request-understanding component of a weather forecast chatbot.

Today's date is {today.isoformat()}.

The conversation may contain previous user and assistant messages.
Use previous messages ONLY to resolve missing context in a follow-up.
For example:
- User: "I wanna go to Olpe's lake for swimming"
- User: "today"
The second message should inherit the location and activity from the previous message.

Extract:
- activity
- location
- date as stated by the user
- date_iso as YYYY-MM-DD
- time period
- elevation in metres when explicitly provided

Supported activities:
hiking, cycling, mountain biking, running, camping,
trail running, swimming, outdoor tour.

Rules:
1. Extract only information supported by the current message or relevant previous context.
2. Do not invent missing values.
3. Resolve relative dates using today's date.
4. For Saturday or Sunday, return the next occurrence.
5. For this weekend, use the upcoming Saturday.
6. If no time period is given, return an empty string.
7. If no elevation is given, return null.
8. Distinguish a follow-up from a new request:
   - Short follow-ups such as "what about tomorrow?", "and in the afternoon?",
     or "what about there?" should inherit only the relevant missing details
     from the immediately preceding weather request.
   - If the user states a new activity (for example, "I want to go cycling")
     after a previous completed weather answer, treat it as a NEW request.
     Do not copy the old location or date just because they appeared earlier.
   - If the previous user request was incomplete and the assistant asked for
     missing details, a reply such as "in Berlin tomorrow" should complete
     that pending request and retain its activity.
   - If the user provides a new location or activity, prefer the new value.
9. Use the conversation context below as context, but prioritize the current
   message and the rules above.
10. Return only the structured data.

Conversation context (oldest to newest):
{conversation_context}

Current user message:
{user_question}
"""

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=instructions,
        input=(
            "Conversation context (oldest to newest):\\n"
            f"{conversation_context}\\n\\n"
            "Current user message:\\n"
            f"{user_question}"
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "weather_request",
                "schema": REQUEST_SCHEMA,
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)



def generate_weather_response(
    client,
    user_question,
    request,
    location,
    forecast_summary,
    activity_assessment
):
    """Generate a concise answer grounded in the retrieved forecast.

    Args:
        client: Configured OpenAI client.
        user_question: Original user message.
        request: Structured request extracted from the conversation.
        location: Geocoded location details.
        forecast_summary: Aggregated weather values for the selected period.
        activity_assessment: Rule-based assessment for the requested activity.

    Returns:
        str: Natural-language weather response.
    """
    prompt = f"""
User question:
{user_question}

Structured request:
{json.dumps(request, ensure_ascii=False)}

Location:
{json.dumps(location, ensure_ascii=False)}

Forecast:
{json.dumps(forecast_summary, ensure_ascii=False)}

Activity assessment:
{json.dumps(activity_assessment, ensure_ascii=False)}

Write a concise answer for the outdoor user.

Requirements:
- Use only supplied forecast data for factual weather values.
- Mention temperature, conditions and wind.
- Mention precipitation when relevant.
- Address the requested activity.
- Do not claim guaranteed safety.
- Do not invent missing information.
"""

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=(
            "You generate concise, factual weather answers. "
            "Ground factual weather statements in the supplied data."
        ),
        input=prompt
    )

    return response.output_text


