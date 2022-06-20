from supperbot.db import db
from supperbot.db.models import SupperJio


def format_order_message(jio: SupperJio) -> str:
    """Helper function to format the text for the jio messages."""

    message = (
        f"Supper Jio Order #{jio.id}: <b>{jio.restaurant}</b>\n"
        f"Additional Information: \n{jio.description}\n\n"
        "Current Orders:\n"
    )

    orders = db.get_orders(jio.id)

    if not orders:
        # No orders yet
        return message + "None"

    for user_id, order in orders.items():
        user_display_name = db.get_user_name(user_id)
        message += f"{user_display_name} -- " + "; ".join(order) + "\n"

    return message
