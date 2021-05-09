import requests

import click
import requests
from flask.cli import with_appcontext, current_app

from weatherAggregator.db import get_db
from .exceptions import *


@click.command('fetch')
@with_appcontext
def fetch_weather():
    """Fetch weather from all sources for all cities and save it to db"""
    db = get_db()
    cur = db.cursor()

    # Select all cities and their id's in sources
    city_rows = cur.execute('SELECT c.id AS city_id, s.id AS source_id, s.name AS source_name, cs.local_id '
                            'FROM city AS c '
                            'JOIN city_source AS cs on c.id = cs.city_id '
                            'JOIN weather_source AS s on cs.source_id = s.id').fetchall()
    if not city_rows:
        raise click.ClickException('No cities in the database')

    weather_data = []
    for row in city_rows:
        if row['source_name'] == 'openweathermap.org':
            func = fetch_weather_openweathermap
        elif row['source_name'] == 'weatherbit.io':
            func = fetch_weather_weatherbit
        else:
            raise SourceNotSupportedError(f"source {row['source_name']} is not supported")
        try:
            data = func(row['local_id'])
        except NoApiKeysError as err:
            raise click.ClickException('No API keys. Add keys using set-keys command.')
        except FetchError as err:
            raise click.ClickException("can't fetch weather data\n" + str(err)) from err

        weather_data.append((row['city_id'], row['source_id'], data['ob_time'], data['temp']))

    cur.executemany('INSERT OR REPLACE INTO weather_data (city_id, source_id, ob_dt, temp) '
                    'VALUES (?,?,?,?)', weather_data)
    db.commit()
    click.echo('Weather fetched')


def fetch_weather_openweathermap(local_id):
    """
    Fetch weather from openweathermap.org by city id
    :return: dict {'temp':temperature_in_C, 'ob_time': obtainment_time_in_sec}
    """
    try:
        r = requests.get('http://api.openweathermap.org/data/2.5/weather',
                         params={'id': local_id,
                                 'appid': current_app.config['API_KEYS']['openweathermap.org'],
                                 'units': 'metric'})
    except KeyError:
        raise NoApiKeysError
    if r.status_code != 200:
        raise FetchError(f'openweathermap.org response status code {r.status_code}: ' + str(r.reason))
    else:
        data = r.json()
        weather_data = {'temp': data['main']['temp'],
                        'ob_time': data['dt']}
    return weather_data


def fetch_weather_weatherbit(local_id):
    """
    Fetch weather from weatherbit.io by city id
    :return: dict {'temp':temperature_in_C, 'ob_time': obtainment_time_in_sec}
    """
    try:
        r = requests.get('http://api.weatherbit.io/v2.0/current',
                         params={'city_id': local_id,
                                 'key': current_app.config['API_KEYS']['weatherbit.io']})
    except KeyError:
        raise NoApiKeysError()
    if r.status_code != 200:
        raise FetchError(f'weatherbit.io response status code {r.status_code}: ' + str(r.reason))
    else:
        data = r.json()
        weather_data = {'temp': data['data'][0]['temp'],
                        'ob_time': data['data'][0]['ts']}
    return weather_data


