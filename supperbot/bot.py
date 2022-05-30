import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ChosenInlineResultHandler,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

from config import TOKEN
from supperbot import enums
from supperbot.enums import CallbackType

from supperbot.commands.creation import (
    create,
    additional_details,
    inline_query,
    shared_jio,
    finished_creation,
)

from supperbot.commands.ordering import interested_user, add_order, confirm_order


async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.effective_chat.send_message(text="Use /start to use this bot!")


async def start_group(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued, but not in a DM."""
    await update.effective_chat.send_message(
        text="Please initialize me in direct messages!"
    )


async def start(update: Update, context: CallbackContext) -> None:
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


async def not_implemented_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer("This functionality is currently not implemented!")


async def unrecognized_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    logging.error(f"Unexpected callback data received: {query.data}")


async def set_commands(context: CallbackContext):
    await context.bot.set_my_commands([("/start", "Starts the bot")])


application = ApplicationBuilder().concurrent_updates(False).token(TOKEN).build()
application.job_queue.run_once(set_commands, 0)

# Handler for the creation of a supper jio
# fmt: off
create_jio_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create, pattern=enums.regex_pattern(CallbackType.CREATE_JIO))],
    states={
        CallbackType.ADDITIONAL_DETAILS: [
            CallbackQueryHandler(additional_details, pattern=CallbackType.SELECT_RESTAURANT)
        ],
        CallbackType.FINISHED_CREATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, finished_creation)
        ],
    },
    fallbacks=[],
)
application.add_handler(create_jio_conv_handler)

# Handler for adding of orders to a jio
add_order_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_order, pattern=CallbackType.ADD_ORDER)],
    states={
        CallbackType.CONFIRM_ORDER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)
        ]
    },
    fallbacks=[],
)
application.add_handler(add_order_conv_handler)
# fmt: on

# Handler for when a user clicks on the "Add Order" button on a jio
application.add_handler(
    CommandHandler("start", interested_user, filters.Regex(r"order\d"))
)

# /start and /help command handler
application.add_handler(CommandHandler("start", start_group, ~filters.ChatType.PRIVATE))
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# InlineQuery and InlineQuery result handler
application.add_handler(InlineQueryHandler(inline_query))
application.add_handler(ChosenInlineResultHandler(shared_jio, pattern="order"))

# Not yet implemented callbacks
unimplemented_callbacks = "|".join(
    (
        CallbackType.MODIFY_ORDER,
        CallbackType.DELETE_ORDER,
        CallbackType.AMEND_DESCRIPTION,
        CallbackType.CLOSE_JIO,
        CallbackType.VIEW_JIOS,
    )
)
application.add_handler(
    CallbackQueryHandler(not_implemented_callback, unimplemented_callbacks)
)

# Fall through for any callbacks
application.add_handler(CallbackQueryHandler(unrecognized_callback))
