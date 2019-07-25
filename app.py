from flask import Flask, jsonify, request, Response, current_app, g
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps

import config


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvalidTokenError:
                payload = None

            if payload is None: return Response(status=401)

            user_id = payload['user_id']
            g['user_id'] = user_id
            g['user'] = get_user_info(user_id) if user_id else None
        else:
            return Response(status=401)

        return f(*args, **kwargs)
    return decorated_function


def get_user_info(user_id):
    return current_app.database.execute(text("""
                SELECT
                    id, 
                    name,
                    email,
                    profile
                FROM users
                WHERE id = :user_id
            """), {
        'user_id': user_id
    }).fetchone()


def get_timeline(user_id):
    timeline = current_app.database.execute(text("""
                SELECT
                    t.user_id,
                    t.tweet
                FROM tweets t 
                LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
                WHERE t.user_id = :user_id
                OR t.user_id = ufl.follow_user_id
            """), {
        'user_id': user_id
    }).fetchall()
    return [{
        'user_id': tweet['user_id'],
        'tweet': tweet['tweet']
    } for tweet in timeline]


def create_app(test_config=None):
    print("test_config:", test_config)
    app = Flask(__name__)

    CORS(app)
    app.json_encoder = CustomJSONEncoder

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
    app.database = database

    @app.route('/sign-up', methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user['password'] = bcrypt.hashpw(new_user['password'].encode('UTF-8'), bcrypt.gensalt())

        new_user_id = app.database.execute(text("""
            INSERT INTO users(
                name, email, profile, hashed_password
            ) VALUES (
                :name,
                :email,
                :profile,
                :password
            )
        """), new_user).lastrowid

        row = get_user_info(new_user_id)

        created_user = {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'profile': row['profile']
        } if row else None

        return jsonify(created_user)

    @app.route('/login', methods=['POST'])
    def login():
        credential = request.json
        email = credential['email']
        password = credential['password']

        row = database.execute(text("""
            SELECT
                id,
                hashed_password
            FROM users
            WHERE email = :email
        """), {'email': email}).fetchone()

        if row and bcrypt.checkpw(password.encode('UTF-8'), row['hashed_password'].encode('UTF-8')):
            user_id = row['id']
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds=60*60*24)
            }

            print("secret:", app.config['JWT_SECRET_KEY'])
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')

            return jsonify({
                'access_token': token.decode('UTF-8')
            })
        else:
            return '', 401

    @app.route('/tweet', methods=['POST'])
    @login_required
    def tweet():
        user_tweet = request.json
        tweet = user_tweet['tweet']

        if len(tweet) > 300:
            return '300자를 초과했습니다', 400

        app.database.execute(text("""
            INSERT INTO tweets (
                user_id,
                tweet
            ) VALUES (
                :id,
                :tweet
            )
        """), user_tweet)

        return '', 200

    @app.route('/timeline/<int:user_id>', methods=['GET'])
    def timeline(user_id):
        return jsonify({
            'user_id': user_id,
            'timeline': get_timeline(user_id)
        })

    @app.route('/timeline', methods=['GET'])
    @login_required
    def user_timeline(user_id):
        user_id = g.user_id

        return jsonify({
            'user_id': user_id,
            'timeline': get_timeline(user_id)
        })



        return jsonify({
            'user_id': user_id,
            'timeline': timeline
        })

    @app.route('/follow', methods=['POST'])
    @login_required
    def follow():
        payload = request.json

        app.database.execute(text("""
                    INSERT INTO users_follow_list (
                        user_id,
                        follow_user_id
                    ) VALUES (
                        :id,
                        :follow
                    )
                """), payload)

        return '', 200

    @app.route('/unfollow', methods=['POST'])
    @login_required
    def unfollow():
        payload = request.json

        app.database.execute(text("""
                    DELETE FROM users_follow_list 
                    WHERE user_id = :id
                    AND follow_user_id = :unfollow
                """), payload)

        return '', 200
    return app