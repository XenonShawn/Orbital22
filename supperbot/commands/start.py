"""File containing the start and help commands for the bot"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from supperbot.enums import CallbackType


async def help_command(update: Update, _) -> None:
    """Send a message when the command /help is issued."""
    await update.effective_chat.send_message(text="Use /start to use this bot!")


async def start_group(update: Update, _) -> None:
    """Send a message when the command /start is issued, but not in a DM."""
    await update.effective_chat.send_message(
        text="Please initialize me in direct messages!"
    )


async def start(update: Update, _) -> None:
    message = "Welcome to the SupperFarFetch bot! \n\nJust click the buttons below to create a supper jio!"
    keyboard = [
        [
            InlineKeyboardButton(
                "🆕 Create Supper Jio", callback_data=CallbackType.CREATE_JIO
            )
        ],
        [
            InlineKeyboardButton(
                "📖 View Ongoing Jios", callback_data=CallbackType.VIEW_JIOS
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(text=message, reply_markup=reply_markup)
