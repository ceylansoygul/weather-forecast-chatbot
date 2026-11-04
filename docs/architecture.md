# System Architecture

## Overview

The Weather Forecast Chatbot combines natural-language processing, external weather data, and activity-specific rules. The application separates the user interface, request orchestration, language-model interaction, weather retrieval, and activity assessment into distinct modules.

## Request flow

```text
User
  |
  v
Streamlit interface (app/ui.py)
  |
  v
Chatbot orchestration (app/services/chatbot_service.py)
  |
  +--> Request extraction and response generation
  |    (app/services/llm_service.py)
  |
  +--> Location lookup and forecast retrieval
  |    (app/services/weather_service.py)
  |
  +--> Activity-based weather assessment
       (app/services/activity_service.py)
  |
  v
Response displayed in the Streamlit interface
```

## Components

### Application entry point

`main.py` loads the project environment and starts the Streamlit interface.

### User interface

`app/ui.py` renders the chat interface, stores conversation messages in Streamlit session state, calls the chatbot service, and displays the response and optional technical details.

### Chatbot orchestration

`app/services/chatbot_service.py` coordinates the request lifecycle. It checks whether the request contains the information required to retrieve a forecast, requests clarification when necessary, and combines the weather and activity services with the language-model response.

### Language-model service

`app/services/llm_service.py` creates the OpenAI client, extracts structured request details from natural-language messages, and generates the final response using the retrieved forecast and activity assessment.

### Weather service

`app/services/weather_service.py` normalises location text, resolves place names through the Open-Meteo Geocoding API, retrieves hourly forecast data, selects the requested date and time period, and summarises the selected records.

### Activity assessment service

`app/services/activity_service.py` compares forecast temperature, wind speed, and precipitation probability with the thresholds defined for each supported activity. These thresholds are application heuristics and are not official safety standards.

### Configuration

`config/setup.py` loads environment variables from a project-level `.env` file. The API key is read from the environment and is not stored in the source code.

## Data sources and external services

- OpenAI API: structured request extraction and natural-language response generation.
- Open-Meteo Geocoding API: place-name resolution.
- Open-Meteo Forecast API: hourly weather forecast data.

## Important limitations

The application uses the forecast returned for the resolved geographic coordinates. A place name may resolve to a nearby settlement rather than an exact outdoor route or landmark. The current activity assessment uses general thresholds and does not provide official safety guidance or elevation-adjusted mountain forecasts.
