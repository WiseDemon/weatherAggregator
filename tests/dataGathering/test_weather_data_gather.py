import pytest
from datetime import datetime as dt

from fixtures import *
from weatherAggregator.db import get_db
from weatherAggregator.dataGathering.exceptions import *
from weatherAggregator.dataGathering.weather_data_gather import fetch_weather
from weatherAggregator.dataGathering.city_data_gather import add_city


@pytest.fixture
def weather_data(datadir):
    """Get city data from saved responses"""
    weather_data = {}

    with open(datadir.join('openweathermapCityDataResponse'), 'r') as f:
        data = json.load(f)
    weather_data['openweathermap.org'] = {'temp': data['main']['temp'],
                                          'ob_time': data['dt']}

    with open(datadir.join('weatherbitWeatherDataResponse'), 'r') as f:
        data = json.load(f)
    weather_data['weatherbit.io'] = {'temp': data['data'][0]['temp'],
                                     'ob_time': data['data'][0]['ts']}

    return weather_data


@pytest.fixture
def added_city(app):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO city VALUES(1, 'Moscow', 55.75222,37.61556, 'RU')")
        cur.execute("INSERT INTO city_source VALUES (1,1,524901), (1,2,524901)")
        db.commit()


def test_fetch_weather(app, runner, mocked_data_response, weather_data, api_keys, added_city):
    runner.invoke(fetch_weather)

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        rows = cur.execute('SELECT w.temp, w.ob_dt, s.name FROM weather_data AS w JOIN weather_source AS s '
                           'ON w.source_id = s.id').fetchall()
        sources = [row['name'] for row in rows]
        # Check if all sources are present
        assert set(weather_data.keys()).issubset(sources)
        # Check data itself
        for row in rows:
            assert row['temp'] == weather_data[row['name']]['temp']
            assert row['ob_dt'] == weather_data[row['name']]['ob_time']


def test_fetch_weather_no_cities(runner):
    r = runner.invoke(fetch_weather)
    assert 'No cities' in r.output


def test_fetch_weather_no_keys(runner, added_city):
    r = runner.invoke(fetch_weather)
    assert 'No API keys' in r.output


def test_fetch_weather_no_response(runner, monkeypatch, added_city, api_keys):
    def fail_get_request(*args, **kwargs):
        return MockResponse(503, None)

    monkeypatch.setattr(requests, 'get', fail_get_request)

    r = runner.invoke(fetch_weather)
    assert "can't fetch weather" in r.output
