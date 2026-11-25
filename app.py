from flask import Flask, render_template, request

from weather import UNITS, WeatherError, get_weather

app = Flask(__name__)


@app.route("/")
def index():
    city = request.args.get("city", "").strip()
    units = request.args.get("units", "imperial")
    if units not in UNITS:
        units = "imperial"
    weather = error = None
    if "city" in request.args:
        if not city:
            error = "Please enter a city name."
        elif len(city) > 100:
            error = "City name is too long."
        else:
            try:
                weather = get_weather(city, units)
            except WeatherError as e:
                error = str(e)
    return render_template(
        "index.html", city=city, units=units, labels=UNITS[units],
        weather=weather, error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
