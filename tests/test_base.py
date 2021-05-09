import os
import json

import pytest

from weatherAggregator import set_api_keys


def test_set_keys(app, runner):
    """Test set-keys command for successful execution"""
    # Add keys and values to one list
    api_keys = {'openweathermap.org': '1234',
            'weatherbit.io': '5678'}
    args = [item for (key, value) in api_keys.items() for item in (key,value)]
    runner.invoke(set_api_keys, args)
    keys_path = app.config['API_KEYS_PATH']

    # Check if file was created
    assert os.path.exists(keys_path)

    # Check if saved keys are right
    with open(keys_path, 'r') as f:
        assert api_keys == json.load(f)

    # Check if keys in config are right
    assert api_keys == app.config['API_KEYS']


@pytest.mark.parametrize('args, message', [('', 'Error: no arguments\n'),
                                           ('weatherbit.io', 'Error: odd number of arguments\n')])
def test_set_keys_wrong_args(runner, args, message):
    """Test set-keys command for failure with wrong arguments"""
    result = runner.invoke(set_api_keys, args)
    assert message == result.output
