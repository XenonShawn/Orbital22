"""Coroutines and helper functions relating to adding orders to existing jios."""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ConversationHandler

from supperbot import enums
from supperbot.db import db
from supperbot.enums import CallbackType

from supperbot.commands.helper import (
    update_consolidated_orders,
    format_order_message,
    order_message_keyboard_markup,
)


async def interested_user(update: Update, context: CallbackContext) -> None:
    """
    Called when a user clicks "Add Order" deep link on a Supper Jio.

    This callback does a number of steps
    - Update the display name and chat id of the user so that their names will be
      displayed properly in consolidated order messages
    - Create a row in the `Order` database so they can add in their orders
    - Send a message to the user so that they can add in their orders
    """
    # TODO: Refactor out the getting of order id.
    jio_id = int(context.args[0][5:])

    # Update user display name and chat id
    db.upsert_user(
        update.effective_user.id,
        update.effective_user.first_name,
        update.effective_chat.id,
    )

    # Create an `Order` row for the user
    db.create_order(jio_id=jio_id, user_id=update.effective_user.id)

    await format_and_send_user_orders(update, jio_id)


async def format_and_send_user_orders(update: Update, jio_id: int) -> None:
    # TODO: check if order even exists
    # TODO: check if order is already closed
    order = db.get_order(jio_id, update.effective_user.id)

    message = format_order_message(order)
    keyboard = order_message_keyboard_markup(order)

    msg = await update.effective_chat.send_message(
        text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML
    )
    db.update_order_message_id(order.jio.id, order.user_id, msg.message_id)


async def add_order(update: Update, context: CallbackContext):
    """
    Callback for when a user wishes to add an order to a jio.
    """
    query = update.callback_query
    jio_id = int(enums.parse_callback_data(query.data)[1])
    jio = db.get_jio(jio_id)

    if jio.is_closed():
        await query.answer("The jio is closed!")
        return

    # TODO: Maybe allow adding multiple orders at once using line breaks?
    message = f"Adding order for Order #{jio_id}\n\nPlease type out your order."

    # Keep track of current order for the reply
    context.user_data["current_order"] = jio_id

    await update.effective_message.edit_text(text=message, reply_markup=None)
    await query.answer()
    return CallbackType.CONFIRM_ORDER


async def confirm_order(update: Update, context: CallbackContext):
    # TODO: Investigate the error that occurs here for some reason - sometimes update.message == None
    food = update.message.text
    jio_id = context.user_data["current_order"]
    db.add_food_order(jio_id, update.effective_user.id, food)
    del context.user_data["current_order"]

    await format_and_send_user_orders(update, jio_id)

    await update_consolidated_orders(context.bot, jio_id)
    return ConversationHandler.END
