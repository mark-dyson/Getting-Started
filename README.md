# Flask Weather App

Enter a city and see the current weather with an icon. Uses the free [Open-Meteo](https://open-meteo.com/) APIs, so no API key is needed.

## Features
- City search with geocoding (Open-Meteo Geocoding API)
- Current temperature, feels-like, humidity, wind, and conditions
- Emoji icons that change for day and night
- Fahrenheit/Celsius dropdown (°F/mph or °C/km/h)
- Friendly errors for unknown cities and network failures

## Project layout
```
app.py                  Flask app and index route
weather.py              Geocoding, forecast fetch, unit config, icon mapping
templates/              base.html, index.html
static/style.css        Styles
tests/test_weather.py   pytest tests (API calls are mocked)
requirements.txt        flask, requests, pytest
```

## Setup and run
```powershell
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000.

## Tests
```powershell
python -m pytest -q
```

## Corporate network / SSL errors
If the app shows "Could not reach the weather service" and requests fail with
`CERTIFICATE_VERIFY_FAILED`, a proxy is re-signing HTTPS traffic. Point `requests`
at your organization's root certificate (Base-64 `.crt`/`.pem`):

```powershell
$env:REQUESTS_CA_BUNDLE = "C:\path\to\root-ca.crt"
python app.py
```

To persist it, run `setx REQUESTS_CA_BUNDLE "C:\path\to\root-ca.crt"` and open a new terminal.
Do not disable certificate verification.