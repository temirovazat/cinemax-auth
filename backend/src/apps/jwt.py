from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from redis import Redis

from apps.security import user_datastore as postgres
from core.config import CONFIG
from models.user import User


class AccessToken:
    """Token for accessing resources."""

    def __init__(self, user: User):
        """Generate a token for the user during initialization.

        Args:
            user: User
        """
        self.access_token = create_access_token(
            identity=user.email,
            additional_claims={
                'roles': [role.name for role in user.roles],
                'user_id': user.pk,
            },
        )


class RefreshToken:
    """Token for obtaining new tokens in exchange for old ones."""

    def __init__(self, user: User):
        """Generate a token for the user during initialization.

        Args:
            user: User
        """
        self.refresh_token = create_refresh_token(
            identity=user.email,
            additional_claims={
                'roles': [role.name for role in user.roles],
                'user_id': user.pk,
            },
        )


def generate_tokens(user: User) -> dict:
    """Generate a pair of user keys.

    Args:
        user: User

    Returns:
        dict: Access key and refresh key
    """
    return {**AccessToken(user).__dict__, **RefreshToken(user).__dict__}


jwt = JWTManager()
jwt_redis_blocklist = Redis(host=CONFIG.redis.host, port=CONFIG.redis.port)


def install(app: Flask):
    """Installs the Flask component for working with JWT tokens.

    Args:
        app: Flask
    """
    app.config['SECRET_KEY'] = CONFIG.flask.secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = CONFIG.flask.access_token_expires_by_sec
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload['jti']
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    @jwt.user_lookup_loader
    def user_lookup_callback(jwt_header, jwt_data):
        email = jwt_data['sub']
        return postgres.find_user(email=email)
