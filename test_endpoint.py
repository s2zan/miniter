import config
from app import create_app

import pytest
import json
from sqlalchemy import create_engine, text


database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)


@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api


def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data


def test_tweet(api):
    # sign-up
    new_user = {
        'email': 'test@gmail.com',
        'password': 'test',
        'name': '테스트',
        'profile': 'test profile'
    }
    resp = api.post(
        '/sign-up',
        data=json.dumps(new_user),
        content_type='application/json'
    )
    assert resp.status_code == 200

    resp_json = json.loads(resp.data.decode('utf-8'))
    new_user_id = resp_json['id']

    # login
    resp = api.post(
        '/login',
        data=json.dumps({'email': 'test@gmail.com', 'password': 'test'}),
        content_type='application/json'
    )
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    # tweet
    resp = api.post(
        '/tweet',
        data=json.dumps({'tweet': 'Hello World!'}),
        content_type='application/json',
        headers={'Authorization': access_token}
    )
    assert resp.status_code == 200

    # tweet 응답 확인
    resp = api.get(f'/timeline/{new_user_id}')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': new_user_id,
        'timeline': [
            {
                'user_id': new_user_id,
                'tweet': 'Hello World!'
            }
        ]
    }
