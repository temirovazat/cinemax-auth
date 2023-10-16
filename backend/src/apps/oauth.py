import abc

from flask import Flask, redirect, url_for
from rauth import OAuth2Service
from werkzeug import Response

from apps.utils import decode_json
from core.config import CONFIG
from core.enums import OAuthProviders


class OAuthSignIn(abc.ABC):
    """Abstract class for implementing OAuth providers."""

    service: OAuth2Service = None

    @abc.abstractmethod
    def callback(self, code: str) -> str:
        """Complete authentication with the provider and retrieve user information.

        Args:
            code: Authorization code to retrieve user data
        """

    @property
    def callback_url(self) -> str:
        """The URL to which the provider should redirect the user after successful authentication.

        Returns:
            str: Callback URL for OAuth authentication
        """
        return url_for('sessions.sessionbyoauth', provider_name=self.service.name, _external=True)

    def authorize(self) -> Response:
        """Redirect to the provider's website where the user should authenticate.

        Returns:
            Response: Response as a redirection to the required URL
        """
        return redirect(location=self.service.get_authorize_url(
            response_type='code',
            redirect_uri=self.callback_url,
        ))


class YandexSignIn(OAuthSignIn):
    """Class for implementing the Yandex provider that uses OAuth2."""

    def __init__(self, client_id: str, client_secret: str):
        """Initialize with the client_id and client_secret assigned to the application in Yandex.

        Args:
            client_id (str): Application identifier
            client_secret (str): Secret code
        """
        self.service = OAuth2Service(
            name='yandex',
            client_id=client_id,
            client_secret=client_secret,
            authorize_url='https://oauth.yandex.com/authorize',
            access_token_url='https://oauth.yandex.com/token',
            base_url='https://login.yandex.ru/',
        )

    def callback(self, code: str) -> str:
        """Authenticate user data with Yandex and retrieve the user's ID.

        Args:
            code (str): The authorization code for accessing user data.

        Returns:
            str: The user's ID on Yandex.
        """
        data = {
            'code': code,
            'grant_type': 'authorization_code',
        }
        oauth_session = self.service.get_auth_session(data=data, decoder=decode_json)
        response = oauth_session.get('info').json()
        return response['id']


class VkSignIn(OAuthSignIn):
    """Class for implementing the VK provider that uses OAuth2."""

    def __init__(self, client_id: str, client_secret: str):
        """Initialize with the application's client_id and client_secret assigned in VK.

        Args:
            client_id: Application identifier
            client_secret: Secret code
        """
        self.service = OAuth2Service(
            name='vk',
            client_id=client_id,
            client_secret=client_secret,
            authorize_url='https://oauth.vk.com/authorize',
            access_token_url='https://oauth.vk.com/access_token',
            base_url='https://api.vk.com/method/',
        )

    def callback(self, code: str) -> str:
        """Authenticate user data with VK and return the user's VK ID.

        Args:
            code: Code to access user data

        Returns:
            str: User ID on VK
        """
        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.callback_url,
        }
        response = self.service.get_raw_access_token(data=data).json()
        return response['user_id']


def install(app: Flask):
    """Set up Flask application configuration for OAuth providers.

    Args:
        app: Flask
    """
    app.config['OAUTH_PROVIDERS'] = {
        OAuthProviders.YANDEX.value: YandexSignIn(
            client_id=CONFIG.yandex.id,
            client_secret=CONFIG.yandex.secret,
        ),
        OAuthProviders.VK.value: VkSignIn(
            client_id=CONFIG.vk.id,
            client_secret=CONFIG.vk.secret,
        ),
    }
