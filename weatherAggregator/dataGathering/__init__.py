from .city_data_gather import add_city
from .weather_data_gather import fetch_weather


def init_app(app):
    app.cli.add_command(add_city)
    app.cli.add_command(fetch_weather)
