import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import weather  # noqa: E402
from app import app  # noqa: E402


def _resp(data):
    m = MagicMock()
    m.json.return_value = data
    m.raise_for_status.return_value = None
    return m


GEO = {"results": [{"name": "Paris", "admin1": "Ile-de-France", "country": "France",
                    "latitude": 48.8, "longitude": 2.3}]}
FORECAST = {"current": {"temperature_2m": 70.4, "apparent_temperature": 68.2,
                        "relative_humidity_2m": 55, "wind_speed_10m": 6.6,
                        "weather_code": 0, "is_day": 1}}


def test_describe_day_night_and_unknown():
    assert weather.describe(0, True) == ("Clear sky", "☀️")
    assert weather.describe(0, False) == ("Clear sky", "🌙")
    assert weather.describe(12345)[0] == "Unknown"


def test_get_weather_success():
    with patch("weather.requests.get", side_effect=[_resp(GEO), _resp(FORECAST)]):
        w = weather.get_weather("Paris")
    assert w["temperature"] == 70
    assert w["icon"] == "☀️"
    assert w["location"] == "Paris, Ile-de-France, France"


def test_metric_units_sent_and_labeled():
    with patch("weather.requests.get", side_effect=[_resp(GEO), _resp(FORECAST)]) as g:
        w = weather.get_weather("Paris", "metric")
    params = g.call_args_list[1].kwargs["params"]
    assert params["temperature_unit"] == "celsius"
    assert params["wind_speed_unit"] == "kmh"
    assert w["temperature"] == 70
    assert weather.UNITS["metric"]["temp_label"] == "°C"


def test_city_not_found():
    with patch("weather.requests.get", return_value=_resp({})):
        with pytest.raises(weather.WeatherError, match="not found"):
            weather.get_weather("Nowhereville")


def test_network_error():
    with patch("weather.requests.get", side_effect=requests.Timeout):
        with pytest.raises(weather.WeatherError):
            weather.get_weather("Paris")


def test_route_renders_weather_and_errors():
    client = app.test_client()
    with patch("weather.requests.get", side_effect=[_resp(GEO), _resp(FORECAST)]):
        html = client.get("/?city=Paris").get_data(as_text=True)
    assert "70°F" in html and "☀️" in html
    assert "Please enter a city name." in client.get("/?city=").get_data(as_text=True)
