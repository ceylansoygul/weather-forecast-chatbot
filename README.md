# Weather Forecast Chatbot

An AI-powered chatbot that helps users understand weather conditions for outdoor activities. Users can ask questions in natural language and receive a forecast summary for a selected activity, location, date, and time period.

The application combines a language model, the Open-Meteo Geocoding and Forecast APIs, and activity-specific weather assessment rules.

## Features

- Natural-language questions about outdoor activities, locations, and dates.
- Location lookup through the Open-Meteo Geocoding API.
- Hourly forecast retrieval through the Open-Meteo Forecast API.
- Activity-based interpretation of temperature, wind, and precipitation.
- Follow-up questions that use relevant conversation context.
- Clarification requests when required information is missing.
- Streamlit chat interface.

The activity thresholds are heuristic application rules. They are not official safety standards and do not guarantee that conditions are safe for an activity. Users should consult local forecasts and official warnings when planning outdoor activities.

## Application workflow

1. The Streamlit interface receives the user's message.
2. The language model extracts the activity, location, date, time period, and optional elevation.
3. The application asks a clarification question if essential information is missing.
4. The location service resolves the place name into coordinates and timezone information.
5. The weather service retrieves hourly forecast data and selects the requested period.
6. The activity service evaluates the selected weather conditions.
7. The language model generates a concise response based on the retrieved forecast and assessment.

## Project structure

```text
weather-forecast-chatbot/
├── app/
│   ├── services/
│   │   ├── activity_service.py
│   │   ├── chatbot_service.py
│   │   ├── llm_service.py
│   │   └── weather_service.py
│   └── ui.py
├── config/
│   └── setup.py
├── docs/
│   └── architecture.md
├── notebooks/
│   ├── 00_Project_Setup.ipynb
│   ├── 01_API_Weather_Data.ipynb
│   ├── 02_Activity_Logic.ipynb
│   ├── 03_LLM_Agent.ipynb
│   ├── 04_End_to_End.ipynb
│   ├── 05_Functional_Testing.ipynb
│   └── 06_Streamlit_Interface.ipynb
├── project_evidence/
│   └── test_results/
├── main.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Requirements

- Python 3.10 or later.
- An OpenAI API key.
- Internet access for the OpenAI and Open-Meteo APIs.

Install the dependencies from the project root:

```bash
python -m pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to a new file named `.env` in the project root.
2. Add your OpenAI API key to `.env`:

   ```text
   OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
   ```

3. Keep `.env` private. It is excluded from version control by `.gitignore`.

For Google Colab, store the key in Colab Secrets under the name `OPENAI_API_KEY` instead of writing it into a notebook.

## Run the application

Activate the project's Python environment, install the requirements, and run the following command from the project root:

```bash
streamlit run main.py
```

Streamlit prints a local URL in the terminal. Open that URL in a browser to use the chatbot.

## Notebook guide

The notebooks provide focused examples of the main project components:

| Notebook | Purpose |
|---|---|
| `00_Project_Setup.ipynb` | Prepare the notebook environment and load configuration. |
| `01_API_Weather_Data.ipynb` | Retrieve, inspect, and process weather data. |
| `02_Activity_Logic.ipynb` | Explore activity-specific weather assessment rules. |
| `03_LLM_Agent.ipynb` | Extract structured information from natural-language questions. |
| `04_End_to_End.ipynb` | Demonstrate the complete request-to-response workflow. |
| `05_Functional_Testing.ipynb` | Run representative functional test scenarios. |
| `06_Streamlit_Interface.ipynb` | Review a standalone interface prototype; the maintained application is launched through `main.py`. |

Run the notebooks in order when reproducing the exploratory workflow. The Streamlit application itself does not require the notebooks to be executed.

## Testing

The functional testing notebook contains ten representative scenarios. Run the tests against the current code before reporting results. Record the test date, input, expected behaviour, observed result, and outcome. Do not treat outputs from an earlier run as evidence for the current version.

Useful behaviours to verify include:

- extraction of activity, location, date, and time period;
- clarification when essential request details are missing;
- correct handling of follow-up questions and new requests;
- location resolution;
- selection of the requested forecast period;
- consistency between forecast data, activity assessment, and generated response.

## Limitations

- Forecast availability and detail depend on the location, requested date, and API response.
- Geocoding may resolve a place description to a nearby settlement rather than an exact trail, lake, or mountain location.
- The application uses standard location forecasts and does not generate elevation-adjusted mountain forecasts.
- Activity assessments use heuristic thresholds and should not be interpreted as professional or official safety advice.
- Live functionality requires internet access and valid API credentials.

## References and documentation

- OpenAI API documentation: https://developers.openai.com/api/docs
- Open-Meteo Forecast API: https://open-meteo.com/en/docs
- Open-Meteo Geocoding API: https://open-meteo.com/en/docs/geocoding-api
- Python documentation: https://docs.python.org/3/
- Streamlit documentation: https://docs.streamlit.io/
- JupyterLab documentation: https://jupyterlab.readthedocs.io/

## Security

Never commit `.env`, API keys, or other credentials. Before sharing the project, check source files, notebooks, outputs, screenshots, and archives for sensitive information.
