from enum import IntEnum

from sqlalchemy import (
    Column as Col,
    ForeignKey,
    Integer,
    String,
    create_engine,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import declarative_base, relationship


# TODO: Make this configurable
engine = create_engine("sqlite://", future=True, echo=False)


Base = declarative_base()


class Stage(IntEnum):
    CREATED = 0
    CLOSED = 1


class PaidStatus(IntEnum):
    NOT_PAID = 0
    PAID = 1


def Column(*args, **kwargs):
    """A helper function to make `sqlalchemy.Column` nullable `False` by default."""
    kwargs["nullable"] = kwargs.get("nullable", False)
    return Col(*args, **kwargs)


class User(Base):
    """Represents a user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    display_name = Column(String)
    chat_id = Column(Integer)


class SupperJio(Base):
    """Represents a created Supper Jio."""

    __tablename__ = "supper_jios"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    restaurant = Column(String(32))
    owner_id = Column(Integer)
    status = Column(Integer)
    chat_id = Column(Integer, nullable=True)
    message_id = Column(Integer, unique=True, nullable=True)
    timestamp = Column(String)

    def is_closed(self):
        return self.status == Stage.CLOSED

    def __repr__(self):
        return f"Order {self.id}: {self.restaurant}"


class Message(Base):
    """Represents a shared jio message"""

    __tablename__ = "shared_messages"

    id = Column(Integer, primary_key=True)
    jio_id = Column(Integer, ForeignKey("supper_jios.id"))
    message_id = Column(String, unique=True)

    jio = relationship("SupperJio", backref="messages")

    def __repr__(self):
        return f"SharedMessage({self.jio_id=}, {self.message_id=})"


class Order(Base):
    """Represents an order made by a user"""

    __tablename__ = "orders"

    jio_id = Column(Integer, ForeignKey("supper_jios.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    food = Column(String)  # Tab separated
    paid = Column(Integer)
    message_id = Column(Integer, unique=True, nullable=True)

    __table_args__ = (PrimaryKeyConstraint("jio_id", "user_id"),)

    user = relationship("User", backref="orders")
    jio = relationship("SupperJio", backref="orders")

    def __repr__(self):
        return f"Order {self.jio_id}: ({self.user_id=}) {self.food}"


Base.metadata.create_all(engine)
