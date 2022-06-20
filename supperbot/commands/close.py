"""
Coroutines for when the user decides to close a supper jio
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from supperbot import db, enums


async def close_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    order_id = int(enums.parse_callback_data(query.data)[1])

    pass
