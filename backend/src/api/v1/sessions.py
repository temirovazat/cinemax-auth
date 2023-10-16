from http import HTTPStatus
from typing import Dict, List, Optional, Tuple

from flask import Blueprint, current_app, make_response, request
from flask_apispec import marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import get_current_user, get_jwt, jwt_required
from werkzeug import Response
from werkzeug.exceptions import BadRequest, Unauthorized

from api import schemas
from apps.jwt import generate_tokens
from apps.jwt import jwt_redis_blocklist as redis
from apps.oauth import OAuthSignIn
from apps.security import user_datastore as postgres
from core.config import CONFIG

sessions = Blueprint('sessions', __name__)


class SessionView(MethodResource):
    """Class for representing user sessions."""

    @use_kwargs(schemas.UserSchema)
    @marshal_with(schemas.TokenSchema)
    def post(self, **kwargs) -> Tuple[Dict, int]:
        """User login.

        Args:
            kwargs: Request parameters

        Raises:
            Unauthorized: Error indicating invalid user authentication data.

        Returns:
            tuple[dict, int]: Tokens and status code 201
        """
        if not (user := postgres.authenticate_user(**kwargs)):
            raise Unauthorized('Failed to authenticate the user!')
        postgres.create_session(user, request.user_agent)
        postgres.commit()
        return generate_tokens(user), HTTPStatus.CREATED

    @jwt_required()
    @use_kwargs(schemas.PageSchema, location='query')
    @marshal_with(schemas.SessionSchema(many=True))
    def get(self, **kwargs) -> Tuple[List, int]:
        """Retrieve a user's login history.

        Args:
            kwargs: Query string parameters

        Returns:
            tuple[list, int]: Login history and status code 200
        """
        user = get_current_user()
        auth_history = user.sessions.paginate(error_out=False, **kwargs)
        return auth_history.items, HTTPStatus.OK

    @jwt_required(refresh=True)
    @marshal_with(schemas.TokenSchema)
    def put(self) -> Tuple[Dict, int]:
        """Refresh the access token.

        Returns:
            tuple[dict, int]: Tokens and status code 201
        """
        user = get_current_user()
        return generate_tokens(user), HTTPStatus.OK

    @jwt_required()
    def delete(self) -> Response:
        """User logout.

        Returns:
            Response: Response with status code 204
        """
        revoked_token = get_jwt()['jti']
        redis.set(revoked_token, value='', ex=CONFIG.flask.access_token_expires_by_sec)
        return make_response('', HTTPStatus.NO_CONTENT)


class SessionByOAuth(MethodResource):
    """Class for representing user authentication through social services."""

    def post(self, provider_name: str) -> Response:
        """Initiate authentication through OAuth.

        Args:
            provider_name: OAuth provider name.

        Raises:
            BadRequest: Error indicating that the provider is not supported or there are connection data missing.

        Returns:
            Response: Response as authentication on the provider's site with a redirection status code 302.
        """
        provider: Optional[OAuthSignIn] = current_app.config['OAUTH_PROVIDERS'].get(provider_name)
        if not provider:
            raise BadRequest(f'Provider {provider_name} is not supported!')
        if not (provider.service.client_id and provider.service.client_secret):
            raise BadRequest(f'Technical issues when connecting to the provider {provider_name}!')
        return provider.authorize()

    @use_kwargs(schemas.OAuthSchema, location='query')
    @marshal_with(schemas.TokenSchema)
    def get(self, provider_name: str, **kwargs) -> Tuple[Dict, int]:
        """Complete OAuth authentication.

        Args:
            provider_name: OAuth provider name.
            kwargs: Query string parameters.

        Returns:
            tuple[dict, int]: Tokens and status code 201
        """
        provider: OAuthSignIn = current_app.config['OAUTH_PROVIDERS'].get(provider_name)
        social_id = provider.callback(**kwargs)
        user = postgres.find_or_create_user(social_id, provider.service.name)
        postgres.create_session(user, request.user_agent)
        postgres.commit()
        return generate_tokens(user), HTTPStatus.CREATED
