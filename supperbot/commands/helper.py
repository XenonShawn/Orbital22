from supperbot import db


def format_order_message(order_id: int) -> str:
    """Helper function to format the text for the jio messages."""

    restaurant, description = db.get_jio(order_id)

    message = (
        f"Supper Jio Order #{order_id}: <b>{restaurant}</b>\n"
        f"Additional Information: \n{description}\n\n"
        "Current Orders:\n"
    )

    orders = db.get_orders(order_id)

    if not orders:
        # No orders yet
        return message + "None"

    for user_id, order in orders.items():
        user_display_name = db.get_user_name(user_id)
        message += f"{user_display_name} -- " + "; ".join(order) + "\n"

    return message
