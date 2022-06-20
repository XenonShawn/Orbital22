from collections import defaultdict
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from supperbot.db.models import Stage, SupperJio, Order, User, engine, Message


session = Session(engine)

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

    session.add(jio)
    session.commit()
    return jio


def get_jio(jio_id: int) -> SupperJio:
    stmt = select(SupperJio).where(SupperJio.id == jio_id)
    return session.scalars(stmt).one()


def update_jio_message_id(jio_id: int, chat_id: int, message_id: int) -> None:
    session.execute(
        update(SupperJio)
        .where(SupperJio.id == jio_id)
        .values(chat_id=chat_id, message_id=message_id)
    )
    session.commit()


def update_jio_status(jio_id: int, status: Stage) -> None:
    stmt = update(SupperJio).where(User.id == jio_id).values(status=status)
    session.execute(stmt)
    session.commit()


def delete_jio(jio: SupperJio):
    raise NotImplementedError


#
# Users
#


def upsert_user(user_id: int, display_name: str) -> User:
    # Unfortunately, SQLAlchemy does not seem to support upserts directly.
    user = session.execute(select(User).where(User.id == user_id)).one_or_none()

    if user is None:
        user = User(id=user_id, display_name=display_name)
        session.add(user)
    else:
        update(User).where(User.id == user_id).values(display_name=display_name)

    session.commit()

    return user


def get_user_name(user_id: int) -> str:
    stmt = select(User.display_name).filter_by(id=user_id)
    return session.scalars(stmt).one()


#
# Orders
#


def add_order(jio_id: int, user_id: int, food: str) -> Order:
    order = Order(jio_id=jio_id, user_id=user_id, food=food)
    session.add(order)
    session.commit()
    return order


def get_orders(jio_id: int) -> dict[int, list[str]]:
    """Fetches a list of orders, tagged with the user's display name"""
    stmt = select(Order).filter_by(jio_id=jio_id)
    rows = session.scalars(stmt).fetchall()

    result = defaultdict(list)
    for order in rows:
        result[order.user_id].append(order.food)

    return result


def get_user_orders(jio_id: int, user_id: int) -> list[str]:
    stmt = select(Order.food).filter_by(jio_id=jio_id, user_id=user_id)
    return session.scalars(stmt).fetchall()


#
# Messages
#


def new_msg(jio_id: int, message_id: str) -> Message:
    msg = Message(jio_id=jio_id, message_id=message_id)
    session.add(msg)
    session.commit()
    return msg


def get_msg_id(jio_id: int) -> list[int]:
    # TODO: Add in the original message from SupperJio table as well
    stmt = select(Message.message_id).filter_by(jio_id=jio_id)
    return session.scalars(stmt).all()
