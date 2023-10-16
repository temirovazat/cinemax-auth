from marshmallow import Schema, fields, validate

from core.config import CONFIG


class UserSchema(Schema):
    """Schema for user validation."""

    email = fields.Email(required=True, validate=[validate.Length(max=250)])
    password = fields.String(required=True, validate=[validate.Length(min=8, max=100)], load_only=True)
    roles = fields.List(fields.String, dump_only=True)


class ChangePasswordSchema(Schema):
    """Schema for password change form validation."""

    old_password = fields.String(required=True, load_only=True)
    new_password = fields.String(required=True, validate=[validate.Length(min=8, max=100)], load_only=True)


class TokenSchema(Schema):
    """Schema for token issuance validation."""

    access_token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)


class RoleSchema(Schema):
    """Schema for role validation."""

    name = fields.String(required=True, validate=[validate.Length(max=80)])
    description = fields.String(validate=[validate.Length(max=255)])


class SessionSchema(Schema):
    """Schema for session validation."""

    event_date = fields.DateTime(format=CONFIG.flask.date_format, dump_only=True)
    user_agent = fields.String(dump_only=True)


class PageSchema(Schema):
    """Schema for page validation."""

    page = fields.Integer(data_key='page_number', validate=[validate.Range(min=1)], load_only=True)
    per_page = fields.Integer(data_key='page_size', validate=[validate.Range(max=100)], load_only=True)


class OAuthSchema(Schema):
    """Schema for validation of the OAuth provider response."""

    code = fields.String(required=True, load_only=True)
