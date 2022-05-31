# README: NUS Orbital 2022 - Milestone 1

## Team Name

SupperFarFetch

## Proposed Level of Achievement

Vostok

## Motivation

Sometimes, consolidating supper orders is difficult. People keep changing their mind, and chain messages can cause people’s orders to be missed. Introducing: The SupperFarFetch bot! This bot will help in consolidation of orders, and help to split orders if there are promotions (eg free fries if above $20 purchase -> split orders into groups of $20).

## Aim

To make consolidation of supper orders simple.

## User Stories

1. As a user, I should be able to easily open up a supper jio.
2. As a user, I should be able to easily share my supper jio with my friends. 
3. As a user, I want to see the (estimated) total cost (with and without tax) of my supper jio.
4. As a user, I was to see a clear list of items to be purchased
5. As a supper jio-ee, I can add in my orders.
6. As a supper jio-ee, I want to be able to amend my orders.
7. As a supper jio-ee, I want to be able to delete my orders.
8. As a supper jio-ee, I want to be able to indicate that I have paid.
9. As a supper jio-ee, I want to be reminded to make payment if I had yet to declare that I have paid in the telegram bot.

## Features and Timeline

Group chats are often hosted on Telegram, and so a Telegram bot will be suitable for this function.

Features to be completed by the mid of June: 

* Supper hosts will be able to create a supper jio in the DMs with the Bot
  * Host can indicate extra information (eg minimum order, any discounts, order location, cut off timing)
  * Host can close the supper jio here as well
* The supper jio can then be shared to any group
* Individuals should be able to add, update and delete their own orders
* Produce final ordering list 
* Users can indicate that they have paid


Features to be completed by the mid of July:

* Automatic splitting of bills
* Bill calculation - GST and Service Charge (if applicable)
* Recurrent reminders for users to pay if they have yet to indicate they have paid
* User friendly features - Save previous orders/favourite orders

## Tech Stack

1. Python
2. `python-telegram-bot` to interface with the Telegram API. v20 is used despite being a pre-release, as it supports `asyncio`.
3. Heroku will be the hosting solution, using their provided Heroku Postgres for storage.
4. `sqlite3` will be used temporarily while prototyping the bot.

## Technical Proof of concept:

Please visit this link:

https://drive.google.com/file/d/1WwHLL6n0Hp4cOG9htfqiI0GriNW-8Ciw/view?usp=sharing
