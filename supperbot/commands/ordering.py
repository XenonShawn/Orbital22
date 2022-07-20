"""Coroutines and helper functions relating to adding orders to existing jios."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.constants import ParseMode
from telegram.ext import ConversationHandler, ContextTypes

from supperbot.db import db
from supperbot.enums import CallbackType, parse_callback_data, join

from supperbot.commands.helper import (
    update_consolidated_orders,
    format_order_message,
    order_message_keyboard_markup,
    update_individual_order,
)


async def interested_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    await format_and_send_user_orders(
        update.effective_user.id, update.effective_chat.id, jio_id, context.bot
    )


async def interested_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Same functionality as the `interested_user` coroutine, except this is for when
    the owner of a jio wants to add in their own orders.
    """
    query = update.callback_query
    jio_id = int(parse_callback_data(query.data)[1])

    # Update user display name and chat id
    db.upsert_user(
        update.effective_user.id,
        update.effective_user.first_name,
        update.effective_chat.id,
    )

    # Create an `Order` row for the user
    db.create_order(jio_id=jio_id, user_id=update.effective_user.id)

    await format_and_send_user_orders(
        update.effective_user.id, update.effective_chat.id, jio_id, context.bot
    )
    await query.answer()


async def format_and_send_user_orders(
    user_id: int, chat_id: int, jio_id: int, bot: Bot
):
    # TODO: check if order even exists
    order = db.get_order(jio_id, user_id)

    message = format_order_message(order)
    keyboard = order_message_keyboard_markup(order)

    msg = await bot.send_message(
        chat_id=chat_id, text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML
    )
    db.update_order_message_id(order.jio.id, order.user_id, msg.message_id)


async def add_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Callback for when a user wishes to add an order to a jio.
    """
    query = update.callback_query
    jio_id = int(parse_callback_data(query.data)[1])
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


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Investigate the error that occurs here for some reason - sometimes update.message == None
    food = update.message.text
    jio_id = context.user_data["current_order"]
    db.add_food_order(jio_id, update.effective_user.id, food)
    del context.user_data["current_order"]

    await format_and_send_user_orders(
        update.effective_user.id, update.effective_chat.id, jio_id, context.bot
    )

    await update_consolidated_orders(context.bot, jio_id)
    return ConversationHandler.END


async def delete_order(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Callback for when the user wishes to delete one food order
    """
    query = update.callback_query
    jio_id = int(parse_callback_data(query.data)[1])
    jio_str = str(jio_id)

    # TODO: Check if jio is closed

    # Obtain all user orders and display in a column
    text = "Please select the which of your food orders to delete:"
    order = db.get_order(jio_id, update.effective_user.id)

    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                "↩ Cancel",
                callback_data=join(CallbackType.DELETE_ORDER_CANCEL, jio_str),
            )
        ]
        # Use a list comprehension to generate the rest of the buttons
        # TODO: Create a next page functionality? Too many buttons can cause an error
        + [
            InlineKeyboardButton(
                food,
                callback_data=join(CallbackType.DELETE_ORDER_ITEM, jio_str, str(idx)),
            )
            for idx, food in enumerate(order.food_list)
        ]
    )

    await update.effective_message.edit_text(text, reply_markup=keyboard)
    await query.answer()


async def cancel_delete_order(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    query = update.callback_query
    jio_id = int(parse_callback_data(query.data)[1])
    order = db.get_order(jio_id, update.effective_user.id)

    await update_individual_order(context.bot, order)
    await query.answer()


async def delete_order_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    _, jio_str, idx = parse_callback_data(query.data)
    order = db.get_order(int(jio_str), update.effective_user.id)

    # TODO: Low priority: Check if jio is closed. Typically message should be overriden
    #       But it's possible that someone send the message elsewhere

    db.delete_food_order(order, int(idx))

    await update_individual_order(context.bot, order)
    await query.answer()
    await update_consolidated_orders(context.bot, int(jio_str))
