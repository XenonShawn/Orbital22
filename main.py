"""Start the bot and set up logging."""
import logging
from supperbot.bot import application

from config import LOGGING_LEVEL


def main():
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        level=LOGGING_LEVEL,
    )
    logging.info("Hello world, initializing bot!")

    application.run_polling(stop_signals=None)


if __name__ == "__main__":
    main()
