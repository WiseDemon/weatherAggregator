import datetime as dt

import click
import requests
from flask.cli import with_appcontext, current_app

from weatherAggregator.db import get_db
from .exceptions import *


@click.command('add-city')
@click.argument('name')
@click.argument('country_code')
@with_appcontext
def add_city(name, country_code):
    """
    \b
    Add city to the database and fetch it's data
    :param name: city name
    :param country_code: country code as in ISO 3166-1 alpha-2 (2 char)
    """
    try:
        data = fetch_city_data(name, country_code)
    except FetchError as err:
        raise click.ClickException("can't fetch city data\n" + str(err)) from err
    except NoApiKeysError:
        raise click.ClickException('No API keys. Add keys using set-keys command.')

    coords = (data['weatherbit.io']['lat'], data['weatherbit.io']['lon'])

    db = get_db()
    cur = db.cursor()

    # Get id if city already in the table
    cur.execute('SELECT id FROM city where name = ? AND country_code = ?', (name, country_code))
    row = cur.fetchone()

    # Not using INSERT OR REPLACE because it changes id, and to mitigate this one needs to query SELECT to substitute
    # id into replaced row anyway
    if row is None:
        # Insert new row for the city
        cur.execute("INSERT INTO city (name, country_code, lat, lon) VALUES (?, ?, ?, ?);",
                    (name, country_code, coords[0], coords[1]))
        city_id = cur.lastrowid
    else:
        city_id = row['id']
        # Update existing city row
        cur.execute('UPDATE city '
                    'SET lat = ?, lon = ? '
                    'WHERE id = ?',
                    (coords[0], coords[1], city_id))

    # Insert or replace id's into many-to-many city-source relationship table
    source_rows = cur.execute('SELECT id, name FROM weather_source').fetchall()
    # Constructing list of tuples (city_id, source_id, local_id) but only for sources in data
    relationships = [(city_id, row['id'], data[row['name']]['id']) for row in source_rows
                     if row['name'] in data]
    cur.executemany('INSERT OR REPLACE INTO city_source VALUES (?, ?, ?)', relationships)

    db.commit()


def fetch_city_data(city_name, country_code):
    """
    Fetches city coordinates and id from weather sources

    :param city_name: city name
    :param country_code: country code as in ISO 3166-1 alpha-2
    :return: dict {source_1: {id:, lat:, lon:}, ...}
    """
    gather_functions = {'openweathermap.org': fetch_city_data_openweathermap,
                        'weatherbit.io': fetch_city_data_weatherbit,
                        }
    data = {}
    for source in gather_functions:
        data[source] = gather_functions[source](city_name, country_code)
    return data


def fetch_city_data_openweathermap(city_name, country_code):
    """Fetches city data from openweathermap.org"""
    try:
        r = requests.get('http://api.openweathermap.org/data/2.5/weather',
                         params={'q': ','.join([city_name, country_code]),
                                 'appid': current_app.config['API_KEYS']['openweathermap.org']}
                         )
    except KeyError:
        raise NoApiKeysError()

    if r.status_code != 200:
        raise FetchError(f'openweathermap.org response status code {r.status_code}: ' + str(r.reason))
    response_data = r.json()
    data = {'id': response_data['id'],
            'lat': response_data['coord']['lat'],
            'lon': response_data['coord']['lon'],
            }
    return data


def fetch_city_data_weatherbit(city_name, country_code):
    """Fetches city data from weatherbit.io"""
    # As strange as it can be, city_id is only included in the history service response
    try:
        r = requests.get('http://api.weatherbit.io/v2.0/history/daily',
                         params={'city': city_name,
                                 'country': country_code,
                                 'key': current_app.config['API_KEYS']['weatherbit.io'],
                                 'start_date': str(dt.date.today()),
                                 'end_date': str(dt.date.today() + dt.timedelta(1))
                                 }
                         )
    except KeyError:
        raise NoApiKeysError

    if r.status_code != 200:
        raise FetchError(f'weatherbit.io response status code {r.status_code}: ' + str(r.reason))
    response_data = r.json()
    data = {'id': int(response_data['city_id']),
            'lat': response_data['lat'],
            'lon': response_data['lon']
            }
    return data
