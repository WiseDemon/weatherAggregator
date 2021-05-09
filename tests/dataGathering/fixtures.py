import json

import pytest
import requests

import weatherAggregator


class MockResponse:
    def __init__(self, status_code, json_data, reason=None):
        self.json_data = json_data
        self.status_code = status_code
        self.reason = reason

    def json(self):
        return self.json_data


@pytest.fixture
def mocked_data_response(datadir, monkeypatch, api_keys):
    """Mocking responses from weather APIs"""

    def mock_requests_get(url, params=None, **kwargs):
        # openweather.org mocked responses
        if url == 'http://api.openweathermap.org/data/2.5/weather':
            # Missing API key of key is wrong
            if 'appid' not in params or params['appid'] != api_keys['openweathermap.org']:
                return MockResponse(401,
                                    {'cod': 401,
                                     'message': "Invalid API key. Please see http://openweathermap.org/faq#error401 "
                                                "for more info."},
                                    'Invalid API key')
            # Missing query parameters
            elif 'q' not in params and 'id' not in params:
                return MockResponse(400,
                                    {'cod': 400,
                                     'message': "Nothing to geocode"},
                                    'Nothing to geocode')
            # Query parameters are wrong
            elif params.get('q') != 'Moscow,RU' and params.get('id') != 524901:
                return MockResponse(404,
                                    {
                                        "cod": "404",
                                        "message": "city not found"
                                    },
                                    'city not found'
                                    )
            # Default temperature units on openweathermap are kelvin
            if 'units' not in params or params['units'] != 'metric':
                with open(datadir.join('openweathermapCityDataResponse'), 'r') as f:
                    data = json.load(f)
                data['main'] = 'garbage'
                return MockResponse(200, data)
            else:
                with open(datadir.join('openweathermapCityDataResponse'), 'r') as f:
                    return MockResponse(200, json.load(f))

        # weatherbit.io mocked responses
        if 'http://api.weatherbit.io/' in url:
            # Missing API key
            if 'key' not in params:
                return MockResponse(403, {'error': "API key is required."}, 'API key is required.')
            # API key is wrong
            elif params['key'] != api_keys['weatherbit.io']:
                return MockResponse(403, {'error': "API key not valid, or not yet activated."},
                                    "API key not valid, or not yet activated.")
            # Missing query parameters
            elif ('country' not in params or 'city' not in params) and 'city_id' not in params:
                return MockResponse(400, {"error": "Invalid Parameters supplied."},
                                    "Invalid Parameters supplied.")
            # Query parameters are wrong
            elif (params.get('city') != 'Moscow' or params.get('country') != 'RU') and \
                    params.get('city_id') != 524901:
                return MockResponse(204, None, 'Internal server error')
            else:
                # History service for querying city data
                if 'http://api.weatherbit.io/v2.0/history/daily' == url:
                    if 'start_date' not in params and 'end_date' not in params:
                        return MockResponse(500, None, 'Bad request')
                    with open(datadir.join('weatherbitCityDataResponse'), 'r') as f:
                        return MockResponse(200, json.load(f))
                # Current weather service for querying city data
                elif 'http://api.weatherbit.io/v2.0/current' == url:
                    with open(datadir.join('weatherbitWeatherDataResponse'), 'r') as f:
                        return MockResponse(200, json.load(f))

    monkeypatch.setattr(requests, 'get', mock_requests_get)
