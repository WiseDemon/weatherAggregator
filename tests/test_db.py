import sqlite3

import pytest

from weatherAggregator.db import get_db, init_db_command


def test_get_close_db(app):
    """Test that get_db returns the same connection and it's closed at context destruction"""
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


# TODO: remove hard-coded names (store names in a file and generate insert query instead?)
def test_init_db(app, runner):
    """Test that db creation works and weather sources are added"""
    result = runner.invoke(init_db_command)
    assert 'Initialized' in result.output

    # Check if weather sources were added
    with app.app_context():
        db = get_db()
        names = db.execute('SELECT name FROM weather_source;')
        names = [row[0] for row in names]
    real_names = ['weatherbit.io', 'openweathermap.org']
    for name in real_names:
        assert name in names
