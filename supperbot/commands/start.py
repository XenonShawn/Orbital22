"""File containing the start and help commands for the bot"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import InlineKeyboardMarkupLimit
from telegram.error import BadRequest

from supperbot.db import db
from supperbot.enums import CallbackType, join


async def help_command(update: Update, _) -> None:
    """Send a message when the command /help is issued."""
    await update.effective_chat.send_message(text="Use /start to use this bot!")


async def start_group(update: Update, _) -> None:
    """Send a message when the command /start is issued, but not in a DM."""
    await update.effective_chat.send_message(
        text="Please initialize me in direct messages!"
    )


async def start(update: Update, _) -> None:
    message = (
        "Welcome to the SupperFarFetch bot!\n\n"
        "Just click the buttons below to create a supper jio!"
    )

    reply_markup = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                "🆕 Create Supper Jio", callback_data=CallbackType.CREATE_JIO
            ),
            InlineKeyboardButton(
                "📖 View Your Jios", callback_data=CallbackType.VIEW_CREATED_JIOS
            ),
            InlineKeyboardButton(
                "📑 View Joined Jios", callback_data=CallbackType.VIEW_JOINED_JIOS
            ),
        ]
    )

    await update.effective_chat.send_message(text=message, reply_markup=reply_markup)


async def view_created_jios(update: Update, _) -> None:
    """
    Allow the user to view the jios that they have created
    """

    query = update.callback_query

    # TODO: Create a next page functionality for the buttons so that more can be viewed
    # Telegram has a limitation on how many buttons there can be. Currently, it's 100.
    # However, 100 buttons is still too many. Right now the limit is 50.
    jios = db.get_user_jios(
        update.effective_user.id,
        limit=min(50, InlineKeyboardMarkupLimit.TOTAL_BUTTON_NUMBER - 1),
        allow_closed=True,
    )

    if not jios:
        # User has not created any jios
        await update.effective_chat.send_message(text="You have not created any jios.")
        await query.answer()
        return

    text = (
        "Which of your jios do you want to view?\n"
        "Only the most recent 50 jios can be viewed."
    )

    keyboard = InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton("↩ Cancel", callback_data=CallbackType.CANCEL_VIEW)]
        # Use a list comprehension to generate the rest of the buttons
        + [
            InlineKeyboardButton(
                str(jio),
                callback_data=join(CallbackType.RESEND_MAIN_MESSAGE, str(jio.id)),
            )
            for jio in jios
        ]
    )

    await update.effective_chat.send_message(text, reply_markup=keyboard)
    await query.answer()


async def cancel_view(update: Update, _) -> None:

    # Try removing the message
    try:
        await update.effective_message.edit_reply_markup(None)
    except BadRequest as e:
        logging.error(f"Unable to cancel view past messages: {e}")

    await start(update, _)


async def view_joined_jios(update: Update, _) -> None:
    """
    Allow the user to view the jios that they have joined
    """

    query = update.callback_query

    # TODO: Create a next page functionality for the buttons so that more can be viewed
    # Telegram has a limitation on how many buttons there can be. Currently, it's 100.
    # However, 100 buttons is still too many. Right now the limit is 50.
    jios = db.get_joined_jios(
        update.effective_user.id,
        limit=min(50, InlineKeyboardMarkupLimit.TOTAL_BUTTON_NUMBER - 1),
    )

    if not jios:
        # User has not created any jios
        await update.effective_chat.send_message(text="You have not joined any jios.")
        await query.answer()
        return

    text = (
        "Which of the jios do you want to view?\n"
        "Only the most recent 50 jios can be viewed."
    )

    keyboard = InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton("↩ Cancel", callback_data=CallbackType.CANCEL_VIEW)]
        # Use a list comprehension to generate the rest of the buttons
        + [
            InlineKeyboardButton(
                str(jio),
                # TODO: `OWNER_ADD_ORDER` is correct, the function is correct.
                #       But name isn't nice, should refactor?
                callback_data=join(CallbackType.OWNER_ADD_ORDER, str(jio.id)),
            )
            for jio in jios
        ]
    )

    await update.effective_chat.send_message(text, reply_markup=keyboard)
    await query.answer()
