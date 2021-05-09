import os
import datetime as dt

import flask
from flask import Flask
from flask.cli import with_appcontext, current_app
import click
import json

from . import db
from weatherAggregator import dataGathering as gather


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config['DATABASE'] = os.path.join(app.instance_path, 'weatherAggregator.sqlite')
        app.config['API_KEYS_PATH'] = os.path.join(app.instance_path, 'weather_api_keys.json')
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    if os.path.exists(app.config['API_KEYS_PATH']):
        with open(app.config['API_KEYS_PATH'], 'r') as f:
            try:
                app.config['API_KEYS'] = json.load(f)
            except json.decoder.JSONDecodeError:
                pass

    app.cli.add_command(set_api_keys)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    gather.init_app(app)

    # a simple page that says hello
    @app.route('/weather')
    def weather():
        city = flask.request.args.get('city')
        source = flask.request.args.get('source')
        cur = db.get_db().cursor()
        query = """SELECT w.ob_dt, w.temp, c.name AS city, c.country_code AS country, s.name AS source 
                FROM weather_data AS w 
                JOIN city AS c ON w.city_id = c.id 
                JOIN weather_source AS s ON w.source_id = s.id """
        where_conds = []
        params = []
        if city is not None:
            where_conds.append('c.name = ?')
            params.append(city)
        if source is not None:
            where_conds.append('s.name = ?')
            params.append(source)
        params = tuple(params)
        if where_conds:
            query += 'WHERE ' + ' AND '.join(where_conds)
        weather_rows = cur.execute(query, params)
        data = {'data': [dict(row) for row in weather_rows]}
        for row in data['data']:
            row['datetime'] = dt.datetime.fromtimestamp(row['ob_dt'])
        return flask.jsonify(data), 200

    return app


@click.command('set-keys')
@click.argument('args', nargs=-1)
@with_appcontext
def set_api_keys(args):
    """
    Saves supplied api keys to a json file.

    Example: flask set-keys openweathermap.org 1234 weatherbit.io 4567

        ARGS: list of sequential pairs (api_name, api_key).\n
    """
    if not args:
        raise click.ClickException('no arguments')
    elif len(args) % 2:
        raise click.ClickException('odd number of arguments')
    api_keys = dict(zip(args[::2], args[1::2]))
    keys_path = current_app.config['API_KEYS_PATH']

    # If file exists, add new keys to old keys, updating them if necessary
    if os.path.exists(keys_path):
        with open(keys_path, 'r') as f:
            try:
                old_keys = json.load(f)
            except json.decoder.JSONDecodeError:
                pass
            else:
                old_keys.update(api_keys)
                api_keys = old_keys

    with open(keys_path, 'w') as f:
        json.dump(api_keys, f)
    current_app.config['API_KEYS'] = api_keys
    click.echo('Keys saved')
