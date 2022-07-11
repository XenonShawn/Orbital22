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
    resend_main_message,
)
from supperbot.commands.ordering import (
    interested_user,
    add_order,
    confirm_order,
    delete_order,
    cancel_delete_order,
    delete_order_item,
)
from supperbot.commands.close import close_jio, reopen_jio, create_ordering_list, back
from supperbot.commands.payment import declare_payment, undo_payment

from config import TOKEN


async def not_implemented_callback(update: Update, _) -> None:
    query = update.callback_query
    await query.answer("This functionality is currently not implemented!")


async def unrecognized_callback(update: Update, _) -> None:
    await not_implemented_callback(update, _)
    logging.error(f"Unexpected callback data received: {update.callback_query.data}")


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


# Handler for when a user clicks on the "Add Order" button on a jio
application.add_handler(
    CommandHandler("start", interested_user, filters.Regex(r"order\d"))
)


# Handler for adding of orders to a jio
add_order_handler = CallbackQueryHandler(add_order, pattern=CallbackType.ADD_ORDER)
add_order_conv_handler = ConversationHandler(
    entry_points=[add_order_handler],
    states={
        CallbackType.CONFIRM_ORDER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)
        ]
    },
    # Allow users to press "add order" again - otherwise it'll show them
    # "not implemented" and I'm not sure why it's happening
    fallbacks=[add_order_handler],
)
application.add_handler(add_order_conv_handler)
application.add_handler(
    CallbackQueryHandler(resend_main_message, pattern=CallbackType.RESEND_MAIN_MESSAGE)
)

# Deleting orders handlers
application.add_handler(
    CallbackQueryHandler(delete_order, pattern=CallbackType.DELETE_ORDER)
)
application.add_handler(
    CallbackQueryHandler(cancel_delete_order, pattern=CallbackType.DELETE_ORDER_CANCEL)
)
application.add_handler(
    CallbackQueryHandler(delete_order_item, pattern=CallbackType.DELETE_ORDER_ITEM)
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
application.add_handler(CallbackQueryHandler(back, pattern=CallbackType.BACK))

# Payment handlers
application.add_handler(
    CallbackQueryHandler(declare_payment, pattern=CallbackType.DECLARE_PAYMENT)
)
application.add_handler(
    CallbackQueryHandler(undo_payment, pattern=CallbackType.UNDO_PAYMENT)
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
        CallbackType.AMEND_DESCRIPTION,
        CallbackType.VIEW_JIOS,
        CallbackType.PING_ALL_UNPAID,
    )
)
application.add_handler(
    CallbackQueryHandler(not_implemented_callback, unimplemented_callbacks)
)

# Fall through for any callbacks
application.add_handler(CallbackQueryHandler(unrecognized_callback))
