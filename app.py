from flask import Flask
from sqlalchemy import create_engine
from flask_cors import CORS

import config

from model import UserDao, TweetDao
from service import UserService, TweetService
from view import create_endpoints


class Services:
    pass


def create_app(test_config = None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None:
        # app.config.from_pyfile("config.py")
        app.config.update({
            'DB': config.db,
            'DB_URL': config.db_url,
            'JWT_SECRET_KEY': config.jwt_secret_key
        })
    else:
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)

    user_dao = UserDao(database)
    tweet_dao = TweetDao(database)

    services = Services
    services.user_service = UserService(user_dao, app.config)
    services.tweet_service = TweetService(tweet_dao)

    create_endpoints(app, services)

    return app
