# README: NUS Orbital 2022 - Milestone 2

## Team Name

SupperFarFetch

## Proposed Level of Achievement

Vostok

## Motivation

Consolidating supper orders is difficult. One common way is to send a message to a channel declaring that one is opening
up orders for supper. To add in their orders, people copy the current message, add in their own order, and then send it
back to the group.

However, this method brings about many issues. People keep changing their minds, causing long chains of messages that 
disrupt the flow of the conversation of the group. There is a high chance that someone might accidentally overwrite
another person's order, causing conflict in the end. Tracking payment is an issue as well; people can forget to pay the
supper host the cost of their meal.

Introducing: The SupperFarFetch bot! This Telegram bot will assist in creating a supper jio through a setup process in
DMs. The created jio can then be shared to as many groups as the host wishes. Users can then add in their orders through
DMing the bot. This way, chat groups will not be spammed, and people's orders can't be accidentally forgotten!

## Aim

To make consolidation of supper orders simple.

## User Stories

1. As a host, I want to be able to easily open up a supper jio.
2. As a host, I want to easily share the supper jio with multiple groups.
3. As a host, I want to have a clear list of items to be ordered.
4. As a host, I want to be able to close the jio so that no one can modify their orders.
5. As a host, I want to be able to see who have declared that they have paid.
6. As a host, I want to easily remind users to pay for their meal.
7. As a user, I want to be able to add in my food orders.
8. As a user, I want to be able to amend my food orders.
9. As a user, I want to be able to delete my food orders.
10. As a user, I want to indicate that I have paid.

## Features and Timeline

Since group chats are often hosted on Telegram, a Telegram bot is most suitable for this project.

### Milestone 1

* Research on problem statement and think of how to best solve the issue
* Research on `python-telegram-bot` Python library
* Implement skeleton (folder structure) of the Telegram Bot
* Implement proof of concept - Ability to create a supper jio and share it to groups

Technical proof of concept: https://drive.google.com/file/d/1WwHLL6n0Hp4cOG9htfqiI0GriNW-8Ciw/view?usp=sharing

### Milestone 2

* Structure changes
  * Created a `db` submodule for all the database related classes and functions
  * Refactored common functions into a separate module, `supperbot.commands.helper`
* Core features implemented
   * Supper jio creation process through DMs
     * Host can indicate extra information (eg minimum order, any discounts, order location, cut off timing)
     * Host can close the supper jio here as well
     * The supper jio can then be shared to any group
   * Individuals are able to add and delete their own orders
   * Produce final ordering list 
   * Users can indicate that they have paid
* Quality of Life features implemented
  * "Put Message Below" button - sends the order message to the bottom of the chat
  
You can test the bot here: https://t.me/supperfarfetch_bot 
  
    
Features to be by the end of Milestone 3:

* Core features
  * Allow host to ping users who have yet to pay for their food
  * Allow host to automatically ping users every day if they have yet to pay
  * Allow a user to view which supper jios they are currently participating in and are not closed

* Quality of Life features
  * Allow combination of orders in the final ordering list - eg combine "m fries" with "Medium fries" into one line item
  * Food order suggestions derived from past usage
  * Favourite orders 
  * Allow search for previous orders/supper jio
  * Edit description of the jio

* Structural, backend and miscellaneous changes
  * Hosted on Heroku
  * Database to be ported to Heroku Postgres
  * Perform mass testing for the bot
  * Perform unit testing


## Tech Stack

1. Python
2. `python-telegram-bot` to interface with the Telegram API. v20 is used despite being a pre-release, as it supports 
   `asyncio`.
3. Heroku will be the hosting solution, using their provided Heroku Postgres for storage.
4. `SQLAlchemy` ORM is used to manage the database, as it allows for a smoother transition to Heroku Postgres during
    deployment.

## Software Development Practices

### Code Style (Black)

_Black_ is a PEP 8 compliant opinionated Python code formatter, which allows for a consistent code style across
different programmers. Black is used as it is widely utilized in the community (eg `requests`, `SQLAlchemy` and 
`Django`). Furthermore, it analyzes the code it formats to ensure that the reformatted code produces the same Abstact
Syntax Tree, which ensures correctness of the code.

### Refactoring

Refactoring was frequently done to improve the quality of code after the initial writing of the code. For example,
frequently used functions were shifted to `supperbot/commands/helper.py`.

### Version Control

Git is used to track the history of all changes made and to help recover from mistakes. It also allows multiple users to
work on the same piece of code on the same time. Github is used as the Git server. Majority of the commits were made by
one the team members, while the other team member focused more on the user experience and testing, as well as the design
and creation of the posters and videos.
