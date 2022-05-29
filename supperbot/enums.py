from enum import unique, Enum


@unique
class CallbackType(str, Enum):
    """
    Enumerations for callbacks.

    The callback system in Telegram uses a callback string. To differentiate between the different actions, the first
    three characters of the callback data will be the action (listed below). The rest of the string will then be the
    "arguments" required, delimited by colons (':') when necessary.

    For example,
    '001:mcdonalds' means selecting mcdonalds during the supper jio commands process.
    """

    # Supper Jio Creation - Starts with 0
    CREATE_JIO = "000"
    SELECT_RESTAURANT = "001"
    ADDITIONAL_DETAILS = "002"
    FINISHED_CREATION = "003"

    AMEND_DESCRIPTION = "010"

    CLOSE_JIO = "020"

    VIEW_JIOS = "030"

    # Modifying of Orders - starts with 1
    ADD_ORDER = "101"
    CONFIRM_ORDER = "102"

    MODIFY_ORDER = "111"
    DELETE_ORDER = "121"


@unique
class Restaurants(str, Enum):
    """
    Enumerations for the restaurants as part of the callbacks.

    Each string should be no longer than 9 characters.
    """
    CUSTOM = "custom"
    MCDONALDS = "mcdonalds"
    ALAMAAN = "alamaan"


restaurant_name = {
    Restaurants.CUSTOM: "Others",
    Restaurants.MCDONALDS: "McDonalds",
    Restaurants.ALAMAAN: "Al Amaan"
}


def regex_pattern(callback_data: str) -> str:
    return '^' + callback_data + '$'


def join(*args: str) -> str:
    return ":".join(args)


def parse_callback_data(callback_data: str) -> list[str]:
    return callback_data.split(":")


# Useful Regex Variables
RESTAURANTS_REGEX = '|'.join(Restaurants)
CALLBACK_REGEX = '|'.join(CallbackType)
