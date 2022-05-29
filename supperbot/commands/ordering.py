"""Coroutines and helper functions relating to adding orders to existing jios."""

import logging

import telegram.error
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.helpers import create_deep_linked_url

from supperbot import db, enums
from supperbot.enums import CallbackType

from supperbot.commands.creation import format_order_message


async def interested_user(update: Update, context: CallbackContext) -> None:
    """
    Called when a user clicks "Add Order" deep link on a Supper Jio.

    TODO: Add in more details
    """
    # TODO: Refactor out the getting of order id.
    order_id = int(context.args[0][5:])

    await format_and_send_user_orders(update, order_id)


async def format_and_send_user_orders(update: Update, order_id: int) -> None:
    # TODO: check if order even exists
    restaurant, description = db.get_jio(order_id)
    restaurant = enums.restaurant_name[restaurant]

    message = f"Supper Jio Order #{order_id}: <b>{restaurant}</b>\n" \
              f"Additional Information: \n{description}\n\n" \
              "Your Orders:\n"

    food_list = db.get_user_orders(order_id, update.effective_user.id)
    message += '\n'.join(food_list) if food_list else "None"

    order_id_str = str(order_id)
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("➕ Add Order", callback_data=enums.join(CallbackType.ADD_ORDER, order_id_str)),
        InlineKeyboardButton("🤔 Modify Order", callback_data=enums.join(CallbackType.MODIFY_ORDER, order_id_str)),
        InlineKeyboardButton("❌ Delete Order", callback_data=enums.join(CallbackType.DELETE_ORDER, order_id_str))
    ]])

    await update.effective_chat.send_message(text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML)


async def add_order(update: Update, context: CallbackContext):
    query = update.callback_query

    # Update user display name
    db.upsert_user(update.effective_user.id, update.effective_user.first_name)

    order_id = int(enums.parse_callback_data(query.data)[1])

    # TODO: Maybe allow adding multiple orders at once using line breaks?
    message = f"Adding order for Order #{order_id}\n\nPlease type out your order."

    context.user_data["current_order"] = order_id  # Keep track of current order for the reply

    await update.effective_message.edit_text(text=message, reply_markup=None)
    await query.answer()
    return CallbackType.CONFIRM_ORDER


async def confirm_order(update: Update, context: CallbackContext):
    food = update.message.text
    order_id = context.user_data["current_order"]
    db.add_order(order_id, update.effective_user.id, food)
    del context.user_data["current_order"]

    await format_and_send_user_orders(update, order_id)

    await update_orders(context.bot, order_id)
    return ConversationHandler.END


async def update_orders(bot: telegram.Bot, order_id: int) -> None:
    """Updates all messages for the order with order id `order_id`."""

    text = format_order_message(order_id)
    messages_to_edit = db.get_msg(order_id)
    deep_link = create_deep_linked_url(bot.bot.username, f"order{order_id}")

    # Edit main jio message
    original_chat_id, original_msg_id = db.get_jio_main_message(order_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Share this Jio!", switch_inline_query=f"order{order_id}")],
        [InlineKeyboardButton("🗒️ Edit Description", callback_data=CallbackType.AMEND_DESCRIPTION),
         InlineKeyboardButton("🔒 Close the Jio", callback_data=CallbackType.CLOSE_JIO)]
    ])
    try:
        await bot.edit_message_text(text, chat_id=original_chat_id, message_id=original_msg_id,
                                    parse_mode=ParseMode.HTML, reply_markup=keyboard)
    except telegram.error.BadRequest:
        logging.error(f"Unable to edit original jio message for order {order_id}")

    # Edit shared jio messages
    for message_id in messages_to_edit:
        try:
            await bot.edit_message_text(text, inline_message_id=message_id, parse_mode=ParseMode.HTML,
                                        reply_markup=InlineKeyboardMarkup.from_button(
                                            InlineKeyboardButton(text="Add Order", url=deep_link)))
        except telegram.error.BadRequest:
            logging.error(f"Unable to edit message with message_id {message_id}")
