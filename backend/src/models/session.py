import uuid
from datetime import datetime

from sqlalchemy import Table, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Connection
from sqlalchemy.orm import validates
from user_agents import parse as parse_user_agent
from werkzeug.user_agent import UserAgent

from apps.db import db


class Session(db.Model):  # type: ignore[name-defined]
    """User session model."""

    __tablename__ = 'sessions'

    pk = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
    )
    user_pk = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.pk', ondelete='CASCADE'),
        nullable=False,
    )
    user_agent = db.Column(db.String)
    user_device_type = db.Column(db.Text, primary_key=True)

    @validates('user_device_type')
    def validate_user_device_type(self, key: str, value: UserAgent) -> str:
        """Parse the User-agent data and determine the user's device type.

        Args:
            key: Field name
            value: Value with a User-Agent object

        Returns:
            str: User's device type
        """
        device = None
        user_agent = parse_user_agent(value.string)
        if user_agent.is_pc:
            device = 'pc'
        elif user_agent.is_tablet:
            device = 'tablet'
        elif user_agent.is_mobile:
            device = 'mobile'
        return device or 'other'


def create_partition(target: Table, connection: Connection, **kwargs) -> None:
    """Partition the 'sessions' table based on the user's device.

    Args:
        target: Target table
        connection: Database connection
        kwargs: Optional keyword arguments
    """
    connection.execute(statement=text(text="""
        CREATE TABLE IF NOT EXISTS "sessions_pc" PARTITION OF "sessions" FOR VALUES IN ('pc')
    """))
    connection.execute(statement=text(text="""
        CREATE TABLE IF NOT EXISTS "sessions_tablet" PARTITION OF "sessions" FOR VALUES IN ('tablet')
    """))
    connection.execute(statement=text(text="""
        CREATE TABLE IF NOT EXISTS "sessions_mobile" PARTITION OF "sessions" FOR VALUES IN ('mobile')
    """))
    connection.execute(statement=text(text="""
        CREATE TABLE IF NOT EXISTS "sessions_other" PARTITION OF "sessions" FOR VALUES IN ('other')
    """))
