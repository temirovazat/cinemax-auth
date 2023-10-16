import logging

import flask_migrate
from flask import Flask, g, request
from flask_script import Command, Manager, prompt
from logstash import LogstashHandler

from apps import api, db, jaeger, jwt, limiter, oauth, security
from apps.security import user_datastore as postgres
from core.config import CONFIG


class RequestIdFilter(logging.Filter):
    """A class for an additional log message filter to add request ID information to log messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add log information to log messages.

        Args:
            record: The record being processed.

        Returns:
            bool: A non-zero value to log the record.
        """
        record.request_id = request.headers.get('X-Request-Id', g.request_id)
        return True


def create_app() -> Flask:
    """Initialize the application.

    Returns:
        Flask: The application instance.
    """
    app = Flask(__name__)
    app.logger = logging.getLogger(__name__)
    app.logger.setLevel(logging.INFO)
    app.logger.addFilter(RequestIdFilter())
    app.logger.addHandler(LogstashHandler(CONFIG.logstash.host, CONFIG.logstash.port, version=1))
    db.install(app)
    jwt.install(app)
    security.install(app)
    api.install(app)
    oauth.install(app)
    limiter.install(app)
    jaeger.install(app)
    return app


class MakeMigrations(Command):
    """Command to create migrations."""

    def run(self):
        """Script to run the command."""
        flask_migrate.migrate()


class Migrate(Command):
    """Command to apply migrations."""

    def run(self):
        """Script to run the command."""
        flask_migrate.upgrade()


class CreateSuperUser(Command):
    """Command to create a superuser."""

    def run(self):
        """Script to run the command."""
        admin = postgres.create_user(
            email=prompt('Enter email'),
            password=prompt('Enter password'),
        )
        role = postgres.find_or_create_role(CONFIG.roles.ADMIN.value)
        postgres.add_role_to_user(admin, role)
        postgres.commit()


if __name__ == '__main__':
    manager = Manager(app=create_app())
    manager.add_command('makemigrations', MakeMigrations())
    manager.add_command('migrate', Migrate())
    manager.add_command('createsuperuser', CreateSuperUser())
    manager.run()
