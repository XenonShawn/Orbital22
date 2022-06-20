"""Coroutines and helper functions relating to creation and sharing of a supper jio"""
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import create_deep_linked_url

from supperbot import db
from supperbot.enums import CallbackType
from supperbot.commands.helper import format_order_message


async def create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> CallbackType:
    """Main command for creating a new jio."""

    # TODO: Check that the user does not have a supper jio currently being created
    if context.user_data.get("create", True):
        pass

    # User is not currently creating an existing supper jio.
    context.user_data["create"] = True
    message = (
        "You are creating a new supper jio order."
        "Please select the restaurant you are ordering from, or type out the name of the restaurant.\n\n"
        "The name of the restaurant should not exceed 32 characters."
    )

    # TODO: Abstract out the following to a separate method call
    reply_markup = ReplyKeyboardMarkup([["McDonalds", "Al Amaan"]])

    await update.effective_chat.send_message(message, reply_markup=reply_markup)

    # Callback queries need to be answered, even if no notification to the user is needed.
    await update.callback_query.answer()

    return CallbackType.ADDITIONAL_DETAILS


async def additional_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collection of additional details and description for the supper jio."""

    text = update.message.text

    if len(text) > 32:
        await update.message.reply_text(
            "Restaurant name is too long. Please try again."
        )
        return

    restaurant = context.user_data["restaurant"] = text

    await update.effective_chat.send_message(
        f"You are creating a supper jio order for restaurant: <b>{restaurant}</b>\n\n"
        "Please type any additional information (eg. Delivery fees, close off timing, etc)",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )
    return CallbackType.FINISHED_CREATION


async def finished_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Presents the final jio text after finishing the initialisation process."""

    information = update.message.text
    order_id = db.create_jio(
        update.effective_user.id, context.user_data["restaurant"], information
    )

    message = format_order_message(order_id)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 Share this Jio!", switch_inline_query=f"order{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🗒️ Edit Description", callback_data=CallbackType.AMEND_DESCRIPTION
                ),
                InlineKeyboardButton(
                    "🔒 Close the Jio", callback_data=CallbackType.CLOSE_JIO
                ),
            ],
        ]
    )

    msg = await update.effective_chat.send_message(
        text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML
    )
    db.update_jio_message_id(order_id, msg.chat_id, msg.message_id)

    context.user_data["create"] = False

    return ConversationHandler.END


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the inline queries from sharing jios."""

    query = update.inline_query.query
    logging.debug("Received an inline query: " + query)

    if query == "" or not query.startswith("order"):
        return

    # TODO: Abstract out this part
    order_id = int(query[5:])

    # TODO: Check for if function returns `None`
    restaurant, description = db.get_jio(order_id)
    deep_link = create_deep_linked_url(context.bot.username, f"order{order_id}")

    # TODO: Check current orders
    message = (
        f"Supper Jio Order #{order_id}: <b>{restaurant}</b>\n"
        f"Additional Information: \n{description}\n\n"
        "Current Orders:\nNone\n\n"
    )

    results = [
        InlineQueryResultArticle(
            id=f"order{order_id}",
            title=f"Order {order_id}",
            description=f"Jio for {restaurant}",
            input_message_content=InputTextMessageContent(
                message, parse_mode=ParseMode.HTML
            ),
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text="➕ Add Order", url=deep_link)
            ),
        )
    ]

    await update.inline_query.answer(results)


async def shared_jio(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Updates the database with the new message id after a jio has been shared to a group."""

    chosen_result = update.chosen_inline_result

    # TODO: Abstract this part
    order_id = int(chosen_result.result_id[5:])
    msg_id = chosen_result.inline_message_id

    db.new_msg(order_id, msg_id)
