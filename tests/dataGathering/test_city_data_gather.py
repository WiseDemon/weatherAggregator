from fixtures import *
from weatherAggregator.db import get_db
from weatherAggregator.dataGathering.city_data_gather import add_city, fetch_city_data
from weatherAggregator.dataGathering.exceptions import *


@pytest.fixture
def city_data(datadir):
    """Get city data from saved responses"""
    city_data = {}

    with open(datadir.join('openweathermapCityDataResponse'), 'r') as f:
        data = json.load(f)
    city_data['openweathermap.org'] = {'id': data['id'],
                                       'lat': data['coord']['lat'],
                                       'lon': data['coord']['lon']}

    with open(datadir.join('weatherbitCityDataResponse'), 'r') as f:
        data = json.load(f)
    city_data['weatherbit.io'] = {'id': int(data['city_id']),
                                  'lat': data['lat'],
                                  'lon': data['lon']}

    return city_data


@pytest.fixture
def mocked_city_data(city_data, monkeypatch):
    """Mock fetch_city_data function to return saved data"""
    def mock_fetch_city_data(city_name, country_code):
        return city_data

    monkeypatch.setattr(weatherAggregator.dataGathering.city_data_gather, 'fetch_city_data', mock_fetch_city_data)

    return city_data


def check_city_in_db(city, city_data, app):
    """
    Function to test if a city is in a table and corresponding data is correct
    :param city: list [name, country_code]
    :param city_data: dict with gathered data from sources
    :return:
    """
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        city_row = cur.execute("SELECT * FROM city WHERE name = 'Moscow'").fetchone()

        # Check if city is in the table and coordinates are there too (choosing one coords from many is not important)
        assert city[0] == city_row['name'] and city[1] == city_row['country_code']
        weatherbit_coords = (city_data['weatherbit.io']['lat'], city_data['weatherbit.io']['lon'])
        openweathermap_coords = (city_data['openweathermap.org']['lat'], city_data['openweathermap.org']['lon'])
        assert ((city_row['lat'] == weatherbit_coords[0] and city_row['lon'] == weatherbit_coords[1]) or
                (city_row['lat'] == openweathermap_coords[0] and city_row['lon'] == openweathermap_coords[1]))

        # Check relationships
        relationship_rows = cur.execute('SELECT source_id, local_id FROM city_source WHERE city_id = ?',
                                        (city_row['id'],)).fetchall()
        source_rows = cur.execute('SELECT * FROM weather_source').fetchall()
        sources = {row['id']: row['name'] for row in source_rows}
        relationships = {sources[row['source_id']]: row['local_id'] for row in relationship_rows}
        for key in city_data:
            assert city_data[key]['id'] == relationships[key]


def test_add_city(app, runner, mocked_city_data):
    """Test add-city command. Command supposed to fetch city data from somewhere"""
    city = ['Moscow', 'RU']
    city_data = mocked_city_data

    runner.invoke(add_city, city)

    check_city_in_db(city, city_data, app)


def test_add_existing_city(app, runner, mocked_city_data):
    """Test add-city command when city is already in db (same city and country). Supposed to rewrite it's coordinates"""
    city = ['Moscow', 'RU']
    city_data = mocked_city_data

    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO city (id, name, country_code, lat, lon) VALUES'
                   '(1, ?, ?, 100, 200);', tuple(city))
        db.execute('INSERT INTO city_source VALUES (1, 1, 42)')
        db.commit()

    runner.invoke(add_city, city)

    check_city_in_db(city, city_data, app)


def test_add_city_wrong_args(runner):
    r = runner.invoke(add_city, [])
    assert 'Error' in r.output
    r = runner.invoke(add_city, ['Moscow'])
    assert 'Error' in r.output


def test_mocked_response(mocked_data_response, api_keys):
    """Test if mocked response performs it's function"""
    r = requests.get('http://api.openweathermap.org/data/2.5/weather',
                     params={'q': 'Moscow,RU', 'appid': api_keys['openweathermap.org']})
    assert 'id' in r.json()
    r = requests.get('http://api.weatherbit.io/v2.0/history/daily',
                     params={'city': 'Moscow',
                             'country': 'RU',
                             'key': api_keys['weatherbit.io'],
                             'start_date': '2021-05-04',
                             'end_date': '2021-05-05',
                            }
                     )
    assert 'city_id' in r.json()


def test_fetch_city_data(app, mocked_data_response, city_data):
    with app.app_context():
        data = fetch_city_data('Moscow', 'RU')
    assert data == city_data


def test_fetch_city_data_failure(app, mocked_data_response):
    with app.app_context():
        with pytest.raises(FetchError):
            data = fetch_city_data('Moscew', 'RU')


def test_fetch_city_data_no_keys(app):
    with app.app_context():
        with pytest.raises(NoApiKeysError):
            data = fetch_city_data('Moscew', 'RU')


def test_add_city_fetch_city_data_failure(runner, mocked_data_response):
    """Test add_city together with fetch_city_data to check add_city reaction on FetchError"""
    r = runner.invoke(add_city, ['Moscew', 'RU'])
    assert 'Error' in r.output


def test_add_city_fetch_city_no_keys(runner):
    """Test add_city together with fetch_city_data to check add_city reaction on FetchError"""
    r = runner.invoke(add_city, ['Moscow', 'RU'])
    assert 'No API keys. Add keys using set-keys command.' in r.output
