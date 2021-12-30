#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

"""
tartarskunk: 1422967494

"""
import numpy as np
import json
import logging
import copy
import util
import os

import telegram as tg
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PollHandler, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

from Sultan.Manager import SultanManager
from Sultan.State import State as GameState
from Sultan.Action import GameAction

class SultanBot:

    def __init__(self, bot):
        self.bot = bot
        self.tutorial_str = open("README.md", 'r').read()
        self.managers = {}

    def command_newgame(self, update: Update, context: CallbackContext) -> None:
        chat_id, user_id, user_name, msg_id = util.message_info(update.message)
        if chat_id not in self.managers:
            manager = SultanManager(self.bot, chat_id)
            self.managers[chat_id] = manager
            
        manager = self.managers[chat_id]
        if manager.game_state == GameState.NO_GAME \
        or manager.game_state == GameState.IDLE:
            manager.new_game(user_id, user_name)
            manager.start_register()

    def command_general(self, update: Update, context: CallbackContext) -> None:
        chat_id, _, _, _ = util.message_info(update.message)
        if chat_id not in self.managers:
            return
        manager = self.managers[chat_id]
        manager.ask_general()

    def command_tutorial(self, update: Update, context: CallbackContext) -> None:
        chat_id, user_id, _, _ = util.message_info(update.message)
        self.bot.send_message(user_id, self.tutorial_str)

    def command_visual(self, update: Update, context: CallbackContext) -> None:
        chat_id, user_id, _, _ = util.message_info(update.message)
        if chat_id not in self.managers:
            return
        manager = self.managers[chat_id]
        manager.draw_game_image()
        manager.send_visual('visual')

    def button_handlers(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        chat_id, _, _, message_id = util.message_info(query.message)
        
        if chat_id not in self.managers:
            return
        # print(query)

        manager = self.managers[chat_id]
        # print(manager.msg_history)
        if message_id == manager.msg_history.setdefault('register_button', None):
            if manager.game_state == GameState.REGISTER:
                manager.do_register(query)
        elif message_id == manager.msg_history.setdefault('general_button', None):
            if manager.game_state != GameState.NO_GAME:
                manager.do_general(query)
        elif message_id == manager.msg_history.setdefault('action_button', None):
            if manager.game_state == GameState.TURN_START:
                manager.do_action(query)
        elif message_id == manager.msg_history.setdefault('peek_button', None):
            if manager.game_state == GameState.TURN_MID:
                manager.do_peek(query)
        elif message_id == manager.msg_history.setdefault('switch_button', None):
            if manager.game_state == GameState.TURN_MID:
                manager.do_switch(query)
        elif message_id == manager.msg_history.setdefault('execute_button', None):
            if manager.game_state == GameState.TURN_MID:
                manager.do_execute(query)
        elif message_id == manager.msg_history.setdefault('detain_button', None):
            if manager.game_state == GameState.TURN_MID:
                manager.do_detain_start(query)
        elif message_id == manager.msg_history.setdefault('avoid_detain_button', None):
            if manager.game_state == GameState.AVOID_DETAIN:
                manager.do_detain_end(query)
        elif message_id == manager.msg_history.setdefault('assassinate_button', None):
            if manager.game_state == GameState.TURN_MID:
                manager.do_assassinate_start(query)
        elif message_id == manager.msg_history.setdefault('stop_assassinate_button', None):
            if manager.game_state == GameState.STOP_ASSASSINATE:
                manager.do_assassinate_end(query)
        elif message_id == manager.msg_history.setdefault('join_button', None):
            if manager.game_state == GameState.JOIN_REVOLUTION:
                manager.do_join(query)
        elif message_id == manager.msg_history.setdefault('capture_button', None):
            if manager.game_state == GameState.TURN_MID:
                manager.do_capture(query)
        elif message_id == manager.msg_history.setdefault('hunt_button', None):
            if manager.game_state == GameState.TURN_MID:
                manager.do_hunt(query)

    """ Admin function """
    def command_gamestate(self, update: Update, context: CallbackContext) -> None:
        chat_id, _, _, _ = util.message_info(update.message)
        if chat_id not in self.managers:
            return
        manager = self.managers[chat_id]
        print(manager.game_state)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    with open('test_bot.token', 'r') as f:
        updater = Updater(f.read().strip(), use_context=True)

    os.makedirs('user_pics', exist_ok=True)
    os.makedirs('game_pics', exist_ok=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    game_bot = SultanBot(bot=updater.bot)
    dispatcher.add_handler(CommandHandler("newgame", game_bot.command_newgame))
    dispatcher.add_handler(CommandHandler("general", game_bot.command_general))
    dispatcher.add_handler(CommandHandler("tutorial", game_bot.command_tutorial))
    dispatcher.add_handler(CommandHandler("visual", game_bot.command_visual))

    dispatcher.add_handler(CommandHandler("gamestate", game_bot.command_gamestate))


    dispatcher.add_handler(CallbackQueryHandler(game_bot.button_handlers))

    # on noncommand i.e message - echo the message on Telegram
    #dispatcher.add_handler(MessageHandler(Filters.photo, meow_bot.jpg2png))
    #dispatcher.add_handler(MessageHandler(Filters.all, meow_bot.jpg2png))
    #dispatcher.add_handler(MessageHandler(Filters.all, meow_bot.meow))
    #dispatcher.add_handler(MessageHandler(Filters.document.file_extension('txt'), meow_bot.meow))

    # Start the Bot
    updater.start_polling(drop_pending_updates=True)
    print('Start polling')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
