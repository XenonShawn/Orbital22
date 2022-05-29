"""Coroutines and helper functions relating to creation and sharing of a supper jio"""
import logging

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
)
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.helpers import create_deep_linked_url

from supperbot import db, enums
from supperbot.enums import CallbackType, Restaurants


async def create(update: Update, context: CallbackContext) -> CallbackType:
    """Main command for creating a new jio."""

    # TODO: Check that the user does not have a supper jio currently being created
    message = f"You are creating a supper jio order. Please select the restaurant you are ordering from:"

    # TODO: Abstract out the following to a separate method call
    keyboard = [
        [
            InlineKeyboardButton("McDonalds", callback_data=enums.join(CallbackType.SELECT_RESTAURANT,
                                                                       Restaurants.MCDONALDS)),
            InlineKeyboardButton("Al Amaan", callback_data=enums.join(CallbackType.SELECT_RESTAURANT,
                                                                      Restaurants.ALAMAAN))
        ],
        [InlineKeyboardButton("Others", callback_data=enums.join(CallbackType.SELECT_RESTAURANT, Restaurants.CUSTOM))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_chat.send_message(text=message, reply_markup=reply_markup)

    # Callback queries need to be answered, even if no notification to the user is needed.
    await update.callback_query.answer()

    return CallbackType.ADDITIONAL_DETAILS


async def additional_details(update: Update, context: CallbackContext) -> CallbackType:
    """Collection of additional details and description for the supper jio."""

    query = update.callback_query
    context.user_data["restaurant"] = enums.parse_callback_data(query.data)[1]
    restaurant = enums.restaurant_name[context.user_data["restaurant"]]

    message = f"You are creating a supper jio order for restaurant: <b>{restaurant}</b>\n\n" \
              "Please type any additional information (eg. Delivery fees, close off timing, etc)"

    await query.edit_message_text(message, reply_markup=None, parse_mode=ParseMode.HTML)
    await query.answer()
    return CallbackType.FINISHED_CREATION


async def finished_creation(update: Update, context: CallbackContext) -> int:
    """Presents the final jio text after finishing the initialisation process."""

    information = update.message.text
    order_id = db.create_jio(update.effective_user.id, context.user_data["restaurant"], information)

    context.user_data['information'] = information

    message = format_order_message(order_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Share this Jio!", switch_inline_query=f"order{order_id}")],
        [InlineKeyboardButton("🗒️ Edit Description", callback_data=CallbackType.AMEND_DESCRIPTION),
         InlineKeyboardButton("🔒 Close the Jio", callback_data=CallbackType.CLOSE_JIO)]
    ])

    msg = await update.effective_chat.send_message(text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    db.update_jio_message_id(order_id, msg.chat_id, msg.message_id)

    return ConversationHandler.END


def format_order_message(order_id: int) -> str:
    """Helper function to format the text for the jio messages."""

    restaurant, description = db.get_jio(order_id)
    restaurant = enums.restaurant_name[restaurant]

    message = f"Supper Jio Order #{order_id}: <b>{restaurant}</b>\n" \
              f"Additional Information: \n{description}\n\n" \
              "Current Orders:\n"

    orders = db.get_orders(order_id)

    if not orders:
        # No orders yet
        return message + "None"

    for user_id, order in orders.items():
        user_display_name = db.get_user_name(user_id)
        message += f"{user_display_name} -- " + "; ".join(order) + '\n'

    return message


async def inline_query(update: Update, context: CallbackContext) -> None:
    """Handles the inline queries from sharing jios."""

    query = update.inline_query.query
    logging.debug("Received an inline query: " + query)

    if query == "" or not query.startswith("order"):
        return

    # TODO: Abstract out this part
    order_id = int(query[5:])

    restaurant, description = db.get_jio(order_id)  # TODO: Check for if function returns `None`
    restaurant = enums.restaurant_name[restaurant]
    deep_link = create_deep_linked_url(context.bot.username, f"order{order_id}")

    # TODO: Check current orders
    message = f"Supper Jio Order #{order_id}: <b>{restaurant}</b>\n" \
              f"Additional Information: \n{description}\n\n" \
              "Current Orders:\nNone\n\n"

    results = [
        InlineQueryResultArticle(
            id=f"order{order_id}",
            title=f"Order {order_id}",
            description=f"Jio for {restaurant}",
            input_message_content=InputTextMessageContent(message, parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(text="➕ Add Order", url=deep_link))
        )
    ]

    await update.inline_query.answer(results)


async def shared_jio(update: Update, context: CallbackContext) -> None:
    """Updates the database with the new message id after a jio has been shared to a group."""

    chosen_result = update.chosen_inline_result

    # TODO: Abstract this part
    order_id = int(chosen_result.result_id[5:])
    msg_id = chosen_result.inline_message_id

    db.new_msg(order_id, msg_id)
