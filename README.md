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

1. As a user, I should be able to easily open up a supper jio and share it with my friends. They can add in their orders, helping me to keep track of the total cost as well.

2. As a supper jio-ee, I want to be able to add in whatever order I want at a price which I define. At the end, I want to be reminded to make payment if I didn’t declare that I paid in the telegram bot.

3. As the person ordering the food, I want to see a clear list of items to be purchased easily, as well as the final price after tax.

## Features and Timeline

Group chats are often hosted on Telegram, and so a Telegram bot will be suitable for this function.

Features to be completed by the mid of June: 

* Individual should be able to add in their own orders
* Allow host to indicate minimum order, any discounts, order location, cut off timing, other information
* Bill calculation - GST and Service Charge (if applicable)
* Final ordering list 


Features to be completed by the mid of July:

* Splitting of bill, recurrent reminders for users to pay
* User friendly features - Save previous orders/favourite orders

## Tech Stack

1. Telegram API
2. Python