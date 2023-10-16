from enum import Enum


class AuthRoles(Enum):
    """A class enumerating user roles."""

    USER = 'user'
    SUBSCRIBER = 'subscriber'
    ADMIN = 'admin'


class OAuthProviders(Enum):
    """A class enumerating OAuth providers."""

    YANDEX = 'yandex'
    VK = 'vk'
