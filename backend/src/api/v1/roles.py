from http import HTTPStatus
from typing import Dict, List, Tuple

from flask import Blueprint, make_response
from flask_apispec import marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from werkzeug import Response
from werkzeug.exceptions import BadRequest, NotFound

from api.schemas import RoleSchema
from apps.security import user_datastore as postgres
from core.decorators import admin_required

roles = Blueprint('roles', __name__)


class RoleView(MethodResource):
    """Class for role views."""

    @admin_required
    @use_kwargs(RoleSchema)
    def post(self, **kwargs) -> Response:
        """Create a role.

        Args:
            kwargs: Request parameters

        Raises:
            BadRequest: Error that such a role already exists

        Returns:
            Response: Response with status code 201
        """
        if postgres.find_role(kwargs['name']):
            raise BadRequest('A role with this name already exists!')
        postgres.create_role(**kwargs)
        postgres.commit()
        return make_response('', HTTPStatus.CREATED)

    @marshal_with(RoleSchema(many=True))
    def get(self) -> Tuple[List, int]:
        """Get a list of roles.

        Returns:
            tuple[list, int]: List of roles and status code 200
        """
        roles_list = postgres.role_model.query.all()
        return roles_list, HTTPStatus.OK


class RoleByNameView(MethodResource):
    """Class for role by name views."""

    @marshal_with(RoleSchema)
    def get(self, role_name: str) -> Tuple[Dict, int]:
        """Get a role by name.

        Args:
            role_name: Name

        Raises:
            NotFound: Error that there is no such role in the database

        Returns:
            tuple[dict, int]: Role and status code 200
        """
        if not (role := postgres.find_role(role_name)):
            raise NotFound('Failed to find the role!')
        return role, HTTPStatus.OK

    @admin_required
    @use_kwargs(RoleSchema(partial=['name']))
    def put(self, role_name: str, **kwargs) -> Response:
        """Modify a role by the specified parameters.

        Args:
            role_name: Name
            kwargs: Request parameters

        Raises:
            NotFound: Error that there is no such role in the database

        Returns:
            Response: Response with status code 200
        """
        if not (role := postgres.find_role(role_name)):
            raise NotFound('Failed to find the role!')
        for field, value in kwargs.items():
            setattr(role, field, value)
        postgres.put(role)
        postgres.commit()
        return make_response('', HTTPStatus.OK)

    @admin_required
    def delete(self, role_name: str) -> Response:
        """Delete a role.

        Args:
            role_name: Name

        Raises:
            NotFound: Error that there is no such role in the database

        Returns:
            Response: Response with status code 204
        """
        if not (role := postgres.find_role(role_name)):
            raise NotFound('Failed to find the role!')
        postgres.delete(role)
        postgres.commit()
        return make_response('', HTTPStatus.NO_CONTENT)
