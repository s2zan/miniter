from flask import Flask, jsonify, request, current_app
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
import config


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


def create_app(test_config=None):
    print("test_config:", test_config)
    app = Flask(__name__)

    app.json_encoder = CustomJSONEncoder

    if test_config is None:
        # app.config.from_pyfile("config.py")
        app.config.update({
            'DB': config.db,
            'DB_URL': config.db_url
        })
    else:
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
    app.database = database

    @app.route('/sign-up', methods=['POST'])
    def sign_up():
        new_user = request.json

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

        row = current_app.database.execute(text("""
            SELECT
                id, 
                name,
                email,
                profile
            FROM users
            WHERE id = :user_id
        """), {
            'user_id': new_user_id
        }).fetchone()

        created_user = {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'profile': row['profile']
        } if row else None

        return jsonify(created_user)

    @app.route('/tweet', methods=['POST'])
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
        rows = app.database.execute(text("""
            SELECT
                t.user_id,
                t.tweet
            FROM tweets t 
            LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
            WHERE t.user_id = :user_id
            OR t.user_id = ufl.follow_user_id
        """), {
            'user_id': user_id
        })

        timeline = [{
            'user_id': row['user_id'],
            'tweet': row['tweet']
        } for row in rows]

        return jsonify({
            'user_id': user_id,
            'timeline': timeline
        })

    @app.route('/follow', methods=['POST'])
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
    def unfollow():
        payload = request.json

        app.database.execute(text("""
                    DELETE FROM users_follow_list 
                    WHERE user_id = :id
                    AND follow_user_id = :unfollow
                """), payload)

        return '', 200
    return app