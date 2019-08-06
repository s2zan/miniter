import config
from app import create_app

import pytest
import json
import bcrypt
from sqlalchemy import create_engine, text


database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)
user_id = None


@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api


def setup_function():
    global user_id
    hashed_password = bcrypt.hashpw(
        b'test',
        bcrypt.gensalt()
    )
    new_user = {
        'email': 'test@gmail.com',
        'password': hashed_password,
        'name': '테스트',
        'profile': 'test profile'
    }

    user_id = database.execute(text("""
        INSERT INTO users (
            name, email, profile, hashed_password
        ) VALUE (
            :name, :email, :profile, :password
        )
    """), new_user).lastrowid


def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))


def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data


def test_tweet(api):
    global user_id

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
    resp = api.get(f'/timeline/{user_id}')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': user_id,
        'timeline': [
            {
                'user_id': user_id,
                'tweet': 'Hello World!'
            }
        ]
    }
