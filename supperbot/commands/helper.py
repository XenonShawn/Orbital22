import logging

from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.helpers import create_deep_linked_url

from supperbot import enums
from supperbot.enums import CallbackType, join
from supperbot.db import db
from supperbot.db.models import SupperJio


def format_jio_message(jio: SupperJio) -> str:
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

    if jio.is_closed():
        message += "\n🛑 Jio is closed! 🛑"

    return message


def main_message_keyboard_markup(jio: SupperJio) -> InlineKeyboardMarkup:
    jio_str = str(jio.id)

    if jio.is_closed():
        return InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(
                    "🔓 Reopen the jio",
                    callback_data=join(CallbackType.REOPEN_JIO, jio_str),
                ),
                InlineKeyboardButton(
                    "✍️Create Ordering List",
                    callback_data=join(CallbackType.CREATE_ORDERING_LIST, jio_str),
                ),
            ]
        )

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 Share this Jio!", switch_inline_query=f"order{jio_str}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🗒️ Edit Description",
                    callback_data=join(CallbackType.AMEND_DESCRIPTION, jio_str),
                ),
                InlineKeyboardButton(
                    "🔒 Close the Jio",
                    callback_data=join(CallbackType.CLOSE_JIO, jio_str),
                ),
            ],
        ]
    )


def shared_message_reply_markup(
    bot: Bot, jio: SupperJio
) -> InlineKeyboardMarkup | None:

    if jio.is_closed():
        return None

    return InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(
            text="Add Order",
            url=create_deep_linked_url(bot.bot.username, f"order{jio.id}"),
        )
    )


async def update_consolidated_orders(bot: Bot, jio_id: int) -> None:
    """
    Updates all messages that are used to consolidate supper orders,
    ie the one in the host DM and the group shared messages
    """

    jio = db.get_jio(jio_id)
    text = format_jio_message(jio)

    keyboard = main_message_keyboard_markup(jio)

    # Edit main jio message
    try:
        await bot.edit_message_text(
            text,
            chat_id=jio.chat_id,
            message_id=jio.message_id,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
    except BadRequest as e:
        logging.error(f"Unable to edit original jio message for order {jio.id}: {e}")

    # Edit shared jio messages
    messages_to_edit = db.get_msg_id(jio_id)
    reply_markup = shared_message_reply_markup(bot, jio)

    for message_id in messages_to_edit:
        try:
            await bot.edit_message_text(
                text,
                inline_message_id=message_id,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )
        except BadRequest as e:
            logging.error(f"Unable to edit message with message_id {message_id}: {e}")


def format_order_message(jio: SupperJio, user_id: int) -> str:
    message = (
        f"Supper Jio Order #{jio.id}: <b>{jio.restaurant}</b>\n"
        f"Additional Information: \n{jio.description}\n\n"
        "Your Orders:\n"
    )

    food_list = db.get_user_orders(jio.id, user_id)
    message += "\n".join(food_list) if food_list else "None"

    if jio.is_closed():
        message += "\n\n🛑 Jio is closed! 🛑"

    return message


def order_message_keyboard_markup(jio: SupperJio) -> InlineKeyboardMarkup:
    jio_str = str(jio.id)

    if jio.is_closed():
        return InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                "Declare Payment",
                callback_data=join(CallbackType.DECLARE_PAYMENT, jio_str),
            )
        )

    return InlineKeyboardMarkup.from_row(
        [
            InlineKeyboardButton(
                "➕ Add Order",
                callback_data=enums.join(CallbackType.ADD_ORDER, jio_str),
            ),
            InlineKeyboardButton(
                "🤔 Modify Order",
                callback_data=enums.join(CallbackType.MODIFY_ORDER, jio_str),
            ),
            InlineKeyboardButton(
                "❌ Delete Order",
                callback_data=enums.join(CallbackType.DELETE_ORDER, jio_str),
            ),
        ]
    )


async def update_individuals_order(bot: Bot, jio_id: int) -> None:
    """
    This coroutine updates all the individual message each user uses to add their
    food orders.
    """
    lst = db.get_list_orders_jio(jio_id)
    jio = db.get_jio(jio_id)

    for order in lst:
        try:
            text = format_order_message(jio, order.user_id)
            markup = order_message_keyboard_markup(jio)

            await bot.edit_message_text(
                text,
                chat_id=order.user.chat_id,
                message_id=order.message_id,
                parse_mode=ParseMode.HTML,
                reply_markup=markup,
            )
        except BadRequest as e:
            logging.error(
                f"Unable to edit individual order message for user {order.user}: {e}"
            )


async def update_all_jio_messages(bot: Bot, jio_id: int) -> None:
    await update_consolidated_orders(bot, jio_id)
    await update_individuals_order(bot, jio_id)
