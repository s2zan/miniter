import bcrypt
import pytest
import config

from model import UserDao, TweetDao
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)

@pytest.fixture
def user_dao():
    return UserDao(database)

def setup_function():
    hashed_password = bcrypt.hashpw(
        b"test password",
        bcrypt.gensalt()
    )
    new_users = [
        {
            'email': 'test@gmail.com',
            'password': hashed_password,
            'name': '테스트',
            'profile': 'test profile'
        }, {
           'email': 'second@naver.com',
           'password': hashed_password,
           'name': '김철수',
           'profile': 'test profile'
        }
    ]
    user_id = database.execute(text("""
        INSERT INTO users (
            name, email, profile, hashed_password
        ) VALUE (
            :name, :email, :profile, :password
        )
    """), new_users).lastrowid + 1

    database.execute(text("""
        INSERT INTO tweets (
            user_id, tweet
        ) VALUES (
            :user_id,
            "Hello World!"
        )
    """), {'user_id': user_id + 1})


def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))


def get_user(user_id):
    row = database.execute(text("""
        SELECT
            id, name, email, profile
        FROM users
        WHERE id = :user_id
    """), {
        'user_id': user_id
    }).fetchone()

    return {
        'id': row['id'],
        'name': row['name'],
        'email': row['email'],
        'profile': row['profile']
    }


def test_insert_user(user_dao):
    new_user = {
        'name': '홍길동',
        'email': 'hong@naver.com',
        'profile': '동에 번쩍 서에 번쩎',
        'password': 'honghong'
    }

    new_user_id = user_dao.insert_user(new_user)
    user = get_user(new_user_id)

    assert user == {
        'id': new_user_id,
        'name': new_user['name'],
        'email': new_user['email'],
        'profile': new_user['profile']
    }