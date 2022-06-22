from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from supperbot.db.models import (
    Stage,
    PaidStatus,
    SupperJio,
    Order,
    User,
    engine,
    Message,
)


_session = Session(engine)

#
# Supper Jio
#


def create_jio(owner_id: int, restaurant: str, description: str) -> SupperJio:
    jio = SupperJio(
        owner_id=owner_id,
        restaurant=restaurant,
        description=description,
        status=Stage.CREATED,
        timestamp=str(datetime.now()),
    )

    _session.add(jio)
    _session.commit()
    return jio


def get_jio(jio_id: int) -> SupperJio:
    stmt = select(SupperJio).where(SupperJio.id == jio_id)
    return _session.scalars(stmt).one()


def update_jio_message_id(jio_id: int, chat_id: int, message_id: int) -> None:
    _session.execute(
        update(SupperJio)
        .where(SupperJio.id == jio_id)
        .values(chat_id=chat_id, message_id=message_id)
    )
    _session.commit()


def update_jio_status(jio_id: int, status: Stage) -> None:
    stmt = update(SupperJio).where(SupperJio.id == jio_id).values(status=status)
    _session.execute(stmt)
    _session.commit()


def delete_jio(jio: SupperJio):
    raise NotImplementedError


#
# Users
#


def upsert_user(user_id: int, display_name: str, chat_id: int) -> User:
    # Unfortunately, SQLAlchemy does not seem to support upserts directly.
    stmt = select(User).where(User.id == user_id)
    user = _session.scalars(stmt).one_or_none()

    if user is None:
        user = User(id=user_id, display_name=display_name, chat_id=chat_id)
        _session.add(user)
    else:
        user.display_name = display_name
        user.chat_id = chat_id

    _session.commit()

    return user


def get_user_name(user_id: int) -> str:
    stmt = select(User.display_name).filter_by(id=user_id)
    return _session.scalars(stmt).one()


#
# Orders
#


def create_order(jio_id: int, user_id: int) -> Order:
    # Check if there exists an existing food order already
    stmt = select(Order).filter_by(jio_id=jio_id, user_id=user_id)
    order = _session.scalars(stmt).one_or_none()

    # If there is no existing order for this jio_io and user, then create a new one
    if order is None:
        order = Order(jio_id=jio_id, user_id=user_id, food="", paid=PaidStatus.NOT_PAID)
        _session.add(order)

    return order


def add_order(jio_id: int, user_id: int, food: str) -> Order:
    """
    Adds one food order to the jio with id `jio_id` for user with id `user_id`.

    The food orders are stored in a single row per user per jio, delimited by tabs.
    """
    stmt = select(Order).filter_by(jio_id=jio_id, user_id=user_id)
    order = _session.scalars(stmt).one()

    # If there are existing food orders. Insert a tab to delimit the food orders.
    if order.food:
        order.food += "\t"

    order.food += food
    _session.commit()
    return order


def update_order_message_id(jio_id: int, user_id: int, message_id: int) -> None:
    stmt = select(Order).filter_by(jio_id=jio_id, user_id=user_id)
    order = _session.scalars(stmt).one()

    order.message_id = message_id
    _session.commit()


def get_list_orders_jio(jio_id: int) -> list[Order]:
    stmt = select(Order).filter_by(jio_id=jio_id)
    return _session.scalars(stmt).fetchall()


def get_orders(jio_id: int) -> dict[int, list[str]]:
    """Fetches a list of orders, tagged with the user's display name"""
    rows = get_list_orders_jio(jio_id)

    # Each food order is delimited by tabs
    return {order.user_id: order.food.split("\t") for order in rows}


def get_user_orders(jio_id: int, user_id: int) -> list[str]:
    stmt = select(Order.food).filter_by(jio_id=jio_id, user_id=user_id)
    food = _session.scalars(stmt).one()
    return food.split("\t") if food else []


#
# Messages
#


def new_msg(jio_id: int, message_id: str) -> Message:
    msg = Message(jio_id=jio_id, message_id=message_id)
    _session.add(msg)
    _session.commit()
    return msg


def get_msg_id(jio_id: int) -> list[int]:
    # TODO: Add in the original message from SupperJio table as well
    stmt = select(Message.message_id).filter_by(jio_id=jio_id)
    return _session.scalars(stmt).all()
