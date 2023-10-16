from functools import lru_cache

from pydantic import BaseSettings, Field


class PostgresConfig(BaseSettings):
    """A class with PostgreSQL connection settings."""

    host: str = '127.0.0.1'
    port: int = 5432
    db: str = 'users_database'
    user: str = 'postgres'
    password: str = 'postgres'


class RedisConfig(BaseSettings):
    """A class with Redis connection settings."""

    host: str = '127.0.0.1'
    port: int = 6379


class FlaskConfig(BaseSettings):
    """A class with FastAPI connection settings."""

    host: str = '0.0.0.0'
    port: int = 5000
    docs: str = 'openapi'
    project_name: str = 'Online Cinema Authorization Service'
    url_prefix: str = '/api/v1'
    access_token_expires_by_sec: int = 60 * 60
    secret_key: str = 'secret_key'
    password_salt: str = ''
    date_format: str = '%d/%m/%Y %H:%M:%S'


class OAuthConfig(BaseSettings):
    """A class with OAuth provider connection settings."""

    id: str = ''
    secret: str = ''


class JaegerConfig(BaseSettings):
    """A class with distributed request tracing settings."""

    host: str = '127.0.0.1'
    port: int = 6831
    enabled: bool = False


class LogstashConfig(BaseSettings):
    """A class with Logstash connection settings."""

    host: str = '127.0.0.1'
    port: int = 5044


class MainSettings(BaseSettings):
    """A class with main project settings."""

    flask: FlaskConfig = Field(default_factory=FlaskConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    yandex: OAuthConfig = Field(default_factory=OAuthConfig)
    vk: OAuthConfig = Field(default_factory=OAuthConfig)
    jaeger: JaegerConfig = Field(default_factory=JaegerConfig)
    logstash: LogstashConfig = Field(default_factory=LogstashConfig)


@lru_cache()
def get_settings() -> MainSettings:
    """
    Create a settings object in a singleton pattern.

    Returns:
        MainSettings: Settings object
    """
    return MainSettings(_env_file='.env', _env_nested_delimiter='_')  # type: ignore[call-arg]


CONFIG = get_settings()
