from typing import Optional

from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import verify_password
from sqlalchemy import and_
from werkzeug.user_agent import UserAgent

from apps.db import db
from apps.utils import generate_random_email, generate_random_string
from core.config import CONFIG
from models.role import Role
from models.session import Session
from models.user import SocialAccount, User


class CustomUserDatastore(SQLAlchemyUserDatastore):
    """Class for working with user database."""

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate and return a user if the provided data is correct.

        Args:
            email: Email
            password: Password

        Returns:
            Optional[User]: Authenticated user or None if verification fails.
        """
        user = self.find_user(email=email)
        return user if user and verify_password(password, user.password) else None

    def create_session(self, user: User, user_agent: UserAgent) -> Session:
        """Create and return a new user session.

        Args:
            user: User
            user_agent: User-Agent object

        Returns:
            Session: User session
        """
        session = Session(user_pk=user.pk, user_agent=user_agent.string, user_device_type=user_agent)
        return self.put(session)

    def create_social_account(self, user: User, social_id: str, social_name: str) -> SocialAccount:
        """Create a social account for the user.

        Args:
            user: User
            social_id: User ID in a social service
            social_name: Name of the social service

        Returns:
            SocialAccount: User's social account
        """
        social = SocialAccount(user_pk=user.pk, social_id=social_id, social_name=social_name)
        return self.put(social)

    def find_social_account(self, social_id: str, social_name: str) -> Optional[SocialAccount]:
        """Find a social account by the given parameters.

        Args:
            social_id: User ID in a social service
            social_name: Name of the social service

        Returns:
            Optional[SocialAccount]: Social account or None if not found
        """
        query = SocialAccount.query.filter(
            and_(SocialAccount.social_id == social_id, SocialAccount.social_name == social_name),
        )
        return query.first()

    def find_or_create_user(self, social_id: str, social_name: str) -> User:
        """Find or create a user based on the ID in a social service.

        Args:
            social_id: User ID in a social service
            social_name: Name of the social service

        Returns:
            User: User identified by their ID in the social service
        """
        social_account = self.find_social_account(social_id, social_name)
        if not social_account:
            user = self.create_user(email=generate_random_email(8), password=generate_random_string(16))
            social_account = self.create_social_account(user, social_id, social_name)
            user.social_accounts.append(social_account)
            self.put(user)
            self.commit()
        return social_account.user


security = Security()
user_datastore = CustomUserDatastore(db, User, Role)


def install(app: Flask):
    """Install the Flask component for working with user data storage.

    Args:
        app: Flask
    """
    app.config['SECURITY_PASSWORD_SALT'] = CONFIG.flask.password_salt
    security.init_app(app, user_datastore)
