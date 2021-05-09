import os
import tempfile
from distutils import dir_util

import pytest

from weatherAggregator import create_app, set_api_keys
from weatherAggregator.db import get_db, init_db


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    keys_fd, keys_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'API_KEYS_PATH': keys_path
    })

    with app.app_context():
        init_db()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def api_keys(runner):
    keys = {'openweathermap.org': '1234',
            'weatherbit.io': '5678'}
    args = [item for (key, value) in keys.items() for item in (key, value)]
    runner.invoke(set_api_keys, args)
    return keys


@pytest.fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir
