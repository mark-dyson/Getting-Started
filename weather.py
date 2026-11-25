import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10


class WeatherError(Exception):
    """Raised for user-displayable weather lookup failures."""


# WMO weather code -> (description, day icon, night icon)
_CODES = {
    0: ("Clear sky", "☀️", "🌙"),
    1: ("Mainly clear", "🌤️", "🌙"),
    2: ("Partly cloudy", "⛅", "☁️"),
    3: ("Overcast", "☁️", "☁️"),
    45: ("Fog", "🌫️", "🌫️"),
    48: ("Rime fog", "🌫️", "🌫️"),
    51: ("Light drizzle", "🌦️", "🌧️"),
    53: ("Drizzle", "🌦️", "🌧️"),
    55: ("Heavy drizzle", "🌧️", "🌧️"),
    56: ("Freezing drizzle", "🌧️", "🌧️"),
    57: ("Heavy freezing drizzle", "🌧️", "🌧️"),
    61: ("Light rain", "🌦️", "🌧️"),
    63: ("Rain", "🌧️", "🌧️"),
    65: ("Heavy rain", "🌧️", "🌧️"),
    66: ("Freezing rain", "🌧️", "🌧️"),
    67: ("Heavy freezing rain", "🌧️", "🌧️"),
    71: ("Light snow", "🌨️", "🌨️"),
    73: ("Snow", "❄️", "❄️"),
    75: ("Heavy snow", "❄️", "❄️"),
    77: ("Snow grains", "❄️", "❄️"),
    80: ("Light showers", "🌦️", "🌧️"),
    81: ("Showers", "🌧️", "🌧️"),
    82: ("Violent showers", "🌧️", "🌧️"),
    85: ("Snow showers", "🌨️", "🌨️"),
    86: ("Heavy snow showers", "🌨️", "🌨️"),
    95: ("Thunderstorm", "⛈️", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️", "⛈️"),
}


def describe(code, is_day=True):
    desc, day, night = _CODES.get(code, ("Unknown", "❓", "❓"))
    return desc, day if is_day else night


def geocode(city):
    try:
        resp = requests.get(
            GEOCODE_URL,
            params={"name": city, "count": 1, "language": "en"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        results = resp.json().get("results")
    except (requests.RequestException, ValueError):
        raise WeatherError("Could not reach the weather service. Try again.")
    if not results:
        raise WeatherError(f"City '{city}' not found.")
    return results[0]


UNITS = {
    "imperial": {"temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
                 "temp_label": "°F", "wind_label": "mph"},
    "metric": {"temperature_unit": "celsius", "wind_speed_unit": "kmh",
               "temp_label": "°C", "wind_label": "km/h"},
}


def get_weather(city, units="imperial"):
    cfg = UNITS.get(units, UNITS["imperial"])
    place = geocode(city)
    try:
        resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "wind_speed_10m,weather_code,is_day",
                "temperature_unit": cfg["temperature_unit"],
                "wind_speed_unit": cfg["wind_speed_unit"],
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        cur = resp.json()["current"]
    except (requests.RequestException, ValueError, KeyError):
        raise WeatherError("Could not fetch weather data. Try again.")

    description, icon = describe(cur["weather_code"], bool(cur["is_day"]))
    location = ", ".join(
        p for p in (place.get("name"), place.get("admin1"), place.get("country")) if p
    )
    return {
        "location": location,
        "temperature": round(cur["temperature_2m"]),
        "feels_like": round(cur["apparent_temperature"]),
        "humidity": cur["relative_humidity_2m"],
        "wind": round(cur["wind_speed_10m"]),
        "description": description,
        "icon": icon,
    }
