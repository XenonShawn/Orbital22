import logging

from telegram import Update
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

from supperbot import enums
from supperbot.enums import CallbackType
from supperbot.commands.start import start_group, start, help_command
from supperbot.commands.creation import (
    create,
    additional_details,
    inline_query,
    shared_jio,
    finished_creation,
)
from supperbot.commands.ordering import interested_user, add_order, confirm_order
from supperbot.commands.close import close_jio, reopen_jio, create_ordering_list

from config import TOKEN


async def not_implemented_callback(update: Update, _) -> None:
    query = update.callback_query
    await query.answer("This functionality is currently not implemented!")


async def unrecognized_callback(update: Update, _) -> None:
    query = update.callback_query
    await query.answer()
    logging.error(f"Unexpected callback data received: {query.data}")


async def set_commands(context: CallbackContext) -> None:
    await context.bot.set_my_commands([("/start", "Start the bot")])


application = ApplicationBuilder().concurrent_updates(False).token(TOKEN).build()
application.job_queue.run_once(set_commands, 0)

# Handler for the creation of a supper jio
create_jio_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            create, pattern=enums.regex_pattern(CallbackType.CREATE_JIO)
        )
    ],
    states={
        CallbackType.ADDITIONAL_DETAILS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, additional_details)
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


# Handler for when a user clicks on the "Add Order" button on a jio
application.add_handler(
    CommandHandler("start", interested_user, filters.Regex(r"order\d"))
)

# Close and reopen jio handler
application.add_handler(CallbackQueryHandler(close_jio, pattern=CallbackType.CLOSE_JIO))
application.add_handler(
    CallbackQueryHandler(reopen_jio, pattern=CallbackType.REOPEN_JIO)
)

# Create ordering list handler
application.add_handler(
    CallbackQueryHandler(
        create_ordering_list, pattern=CallbackType.CREATE_ORDERING_LIST
    )
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
        CallbackType.VIEW_JIOS,
        CallbackType.DECLARE_PAYMENT,
    )
)
application.add_handler(
    CallbackQueryHandler(not_implemented_callback, unimplemented_callbacks)
)

# Fall through for any callbacks
application.add_handler(CallbackQueryHandler(unrecognized_callback))
