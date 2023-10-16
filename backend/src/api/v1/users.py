from http import HTTPStatus
from typing import Dict, List, Tuple
from uuid import UUID

from flask import Blueprint, make_response
from flask_apispec import marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import get_current_user, get_jwt_identity, jwt_required
from werkzeug import Response
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized

from api.schemas import ChangePasswordSchema, RoleSchema, UserSchema
from apps.security import user_datastore as postgres
from core.decorators import admin_required
from core.enums import AuthRoles
from models.role import Role

users = Blueprint('users', __name__)


class UserView(MethodResource):
    """Class for representing a user."""

    @property
    def user_role(self) -> Role:
        """Initial user role upon registration.

        Returns:
            Role: User role
        """
        return postgres.find_or_create_role(AuthRoles.USER.value)

    @use_kwargs(UserSchema)
    def post(self, **kwargs) -> Response:
        """User registration.

        Args:
            kwargs: Request body parameters

        Raises:
            BadRequest: Error that such a user already exists

        Returns:
            Response: Response with status code 201
        """
        if postgres.find_user(email=kwargs['email']):
            raise BadRequest('User with such email already exists!')
        new_user = postgres.create_user(**kwargs)
        postgres.add_role_to_user(new_user, self.user_role)
        postgres.commit()
        return make_response('', HTTPStatus.CREATED)

    @jwt_required()
    @marshal_with(UserSchema)
    def get(self) -> Tuple[Dict, int]:
        """Get personal data.

        Returns:
            Tuple[Dict, int]: Personal information and status code 200
        """
        return get_current_user(), HTTPStatus.OK

    @jwt_required()
    @use_kwargs(ChangePasswordSchema)
    def put(self, **kwargs) -> Response:
        """Change password.

        Args:
            kwargs: Request body parameters

        Raises:
            Unauthorized: Error that incorrect user authentication data is provided

        Returns:
            Response: Response with status code 200
        """
        email, password = get_jwt_identity(), kwargs['old_password']
        if not (user := postgres.authenticate_user(email, password)):
            raise Unauthorized('Failed to authenticate the user!')
        user.password = kwargs['new_password']
        postgres.put(user)
        postgres.commit()
        return make_response('', HTTPStatus.OK)


class SubscribeView(MethodResource):
    """Class for representing the assignment of a subscriber role to a user by user ID."""

    @property
    def subscriber_role(self) -> Role:
        """Subscriber role that grants privileges to the user.

        Returns:
            Role: Subscriber role
        """
        return postgres.find_or_create_role(AuthRoles.SUBSCRIBER.value)

    @admin_required
    def post(self, user_pk: UUID) -> Response:
        """Assign the subscriber role to a user.

        Args:
            user_pk: User ID

        Raises:
            NotFound: Error that there is no such user in the database

        Returns:
            Response: Response with status code 201
        """
        if not (user := postgres.get_user(user_pk)):
            raise NotFound('Failed to find the user!')
        postgres.add_role_to_user(user, self.subscriber_role)
        postgres.commit()
        return make_response('', HTTPStatus.CREATED)

    @admin_required
    @marshal_with(RoleSchema(many=True))
    def get(self, user_pk: UUID) -> Tuple[List, int]:
        """Get user roles.

        Args:
            user_pk: User ID

        Raises:
            NotFound: Error that there is no such user in the database

        Returns:
            Tuple[list, int]: List of user roles and status code 200
        """
        if not (user := postgres.get_user(user_pk)):
            raise NotFound('Failed to find the user!')
        return user.roles, HTTPStatus.OK

    @admin_required
    def delete(self, user_pk: UUID) -> Response:
        """Revoke the subscriber role from a user.

        Args:
            user_pk: User ID

        Raises:
            NotFound: Error that there is no such user in the database

        Returns:
            Response: Response with status code 204
        """
        if not (user := postgres.get_user(user_pk)):
            raise NotFound('Failed to find the user!')
        postgres.remove_role_from_user(user, self.subscriber_role)
        postgres.commit()
        return make_response('', HTTPStatus.NO_CONTENT)
