"""
Coroutines for when the user decides to close a supper jio
"""
from collections import Counter

from telegram import Update
from telegram.ext import ContextTypes

from supperbot import enums
from supperbot.db import db
from supperbot.commands.helper import update_all_jio_messages


async def close_jio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    jio_id = int(enums.parse_callback_data(query.data)[1])

    # TODO: Check if already closed. Possible if original message was duplicated
    db.update_jio_status(jio_id, db.Stage.CLOSED)
    await update_all_jio_messages(context.bot, jio_id)


async def reopen_jio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    jio_id = int(enums.parse_callback_data(query.data)[1])

    db.update_jio_status(jio_id, db.Stage.CREATED)
    await update_all_jio_messages(context.bot, jio_id)


async def create_ordering_list(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    jio_id = int(enums.parse_callback_data(query.data)[1])

    counter = Counter()
    for order in db.get_orders(jio_id).values():
        # Reduce to lower case so that we can match similar orders

        # TODO: Create a way to combine two different orders together for convenience
        #       eg so can combine "m fries" and "medium fries" together
        counter.update(map(str.lower, order))

    text = "Orders:\n\n"

    text += "\n".join(f"{k}: {v}" for k, v in counter.items())

    await query.answer()
    await update.effective_chat.send_message(text=text)
