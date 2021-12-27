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
import imageio
import util

import telegram as tg
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PollHandler, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

"""
{'id': 225404196, 'type': 'private', 'username': 'Alyricing', 'first_name': '音', 'last_name': '抒情'}
{'id': 1483514012, 'type': 'private', 'username': 'gym7012', 'first_name': '鑫'}
1483514012 1483514012 鑫
{'id': 1496518066, 'type': 'private', 'username': 'justajunk', 'first_name': 'Island', 'last_name': 'Man'}
1496518066 1496518066 Island Man
225404196 225404196 音 抒情
{'id': 1032245229, 'type': 'private', 'username': 'DanchifromTW', 'first_name': 'PPer in TW'}


"""
from Sultan.Game import SultanGame
from Sultan.Manager import SultanManager
from Sultan.AI import SultanAI
from Sultan.State import State as GameState
from Sultan.Action import GameAction, BotAction

class SultanBot:

    def __init__(self, bot):
        self.bot = bot
        # self.tutorial_str = open("SpyTutorial.md", 'r').read()
        self.managers = {}
        self.ai_agent = SultanAI()
        # self.game_index = 0
        # self.c_id_list = []

    # def tutorial(self, update: Update, context: CallbackContext) -> None:
        # c_id, u_id, u_name, m_id = util.message_info(update.message)
        # self.bot.send_message(u_id, self.tutorial_str)

    def command_newgame(self, update: Update, context: CallbackContext) -> None:
        chat_id, user_id, user_name, msg_id = util.message_info(update.message)
        # print(update.message)
        if chat_id not in self.managers:
            manager = SultanManager(self.bot, chat_id)
            self.managers[chat_id] = manager

            keyboard = [[
                tg.InlineKeyboardButton(callback_data=0, text='加入'),
                tg.InlineKeyboardButton(callback_data=1, text='退出')],[
                tg.InlineKeyboardButton(callback_data=2, text='[admin] 增加AI'),
                tg.InlineKeyboardButton(callback_data=3, text='[admin] 減少AI'),
                tg.InlineKeyboardButton(callback_data=4, text='[admin] 開始遊戲'),
            ]]
            msg = self.bot.send_message(chat_id,
                reply_markup=tg.InlineKeyboardMarkup(keyboard),
                text=f"[公告] {game.admin_name}想要玩推翻蘇丹，你要加入嗎？")
            game.msg_id['register_button'] = msg.message_id
            
            msg = self.bot.send_message(chat_id,
                text=f"[公告] 目前報名有：{game.print_players_list()}")
            game.msg_id['register_players'] = msg.message_id
            
            game.set_state(GameState.REGISTER)

    def do_newgame(self):
        pass

    def ask_action(self, chat_id):
        game = self.games[chat_id]
        if game.winner is not None:
            self.endgame(chat_id)
            return
        user_id = game.current_player().user_id
        user_name = game.players[user_id].user_name

        legal_actions = game.legal_actions()

        keyboard = [[], [], []]

        elif self.value == 5:
            return '<通用> 查看'
        elif self.value == 6:
            return '<通用> 規則'
        
        for game_action in legal_actions:
            if '一般' in str(game_action):
                keyboard[0].append(tg.InlineKeyboardButton(
                    callback_data=str(game_action), text=str(game_action)))
            else:
                keyboard[1].append(tg.InlineKeyboardButton(
                    callback_data=str(game_action), text=str(game_action)))
        keyboard[2].append(tg.InlineKeyboardButton(
            callback_data=-1, text='遊戲教學'))
        keyboard[2].append(tg.InlineKeyboardButton(
            callback_data='skip', text='跳過'))


        ret_msg = self.bot.send_message(chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] 輪到 {user_name}，想要採取甚麼行動？")
        game.msg_id['action_button'] = ret_msg.message_id
            

    def ask_peek(self, chat_id):
        game = self.games[chat_id]

        user_id = game.current_player().user_id
        user_name = game.players[user_id].user_name

        keyboard = [[]]
        i = 0
        keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data='取消', text='<- 返回'))

        for target_id, target_player in game.players.items():
            if len(keyboard[i]) >= 4:
                keyboard.append([])
                i += 1
            if target_player.can_be_peek(user_id):
                keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data=target_id, text=target_player.status()))

        self.bot.delete_message(chat_id, game.msg_id['action_button'])

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {user_name} 想要偷看誰的身份？")
        game.msg_id['peek_button'] = ret_msg.message_id

    def ask_switch(self, chat_id):
        game = self.games[chat_id]

        user_id = game.current_player().user_id
        user_name = game.players[user_id].user_name

        keyboard = [[]]
        i = 0
        keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data='取消', text='<- 返回'))

        for target_id, target_player in game.players.items():
            if len(keyboard[i]) >= 4:
                keyboard.append([])
                i += 1
            if target_player.can_be_switch(user_id):
                keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data=target_id, text=target_player.status()))

        self.bot.delete_message(chat_id, game.msg_id['action_button'])

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {user_name} 想要跟誰交換身份？")
        game.msg_id['switch_button'] = ret_msg.message_id

    def ask_hide(self, chat_id):
        game = self.games[chat_id]

        user_id = game.current_player().user_id
        user_name = game.players[user_id].user_name

        keyboard = [[]]
        i = 0
        keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data='取消', text='<- 返回'))

        for target_id, target_player in game.players.items():
            if len(keyboard[i]) >= 4:
                keyboard.append([])
                i += 1
            if target_player.can_be_hide(user_id):
                keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data=target_id, text=target_player.status()))

        self.bot.delete_message(chat_id, game.msg_id['action_button'])

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {user_name} 想要跟誰交換身份？")
        game.msg_id['hide_button'] = ret_msg.message_id

    def ask_execute(self, chat_id):
        game = self.games[chat_id]

        user_id = game.current_player().user_id
        user_name = game.players[user_id].user_name

        keyboard = [[]]
        i = 0
        keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data='取消', text='<- 返回'))

        for target_id, target_player in game.players.items():
            if len(keyboard[i]) >= 4:
                keyboard.append([])
                i += 1
            if target_player.can_be_execute():
                keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data=target_id, text=target_player.status()))

        self.bot.delete_message(chat_id, game.msg_id['action_button'])

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {user_name} 想要處決誰？")
        game.msg_id['execute_button'] = ret_msg.message_id

    def ask_detain(self, chat_id):
        game = self.games[chat_id]

        user_id = game.current_player().user_id
        user_name = game.players[user_id].user_name

        keyboard = [[]]
        i = 0
        keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data='取消', text='<- 返回'))

        for target_id, target_player in game.players.items():
            if len(keyboard[i]) >= 4:
                keyboard.append([])
                i += 1
            if target_player.can_be_detain(user_id):
                keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data=target_id, text=target_player.status()))

        self.bot.delete_message(chat_id, game.msg_id['action_button'])

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {user_name} 想要關押誰？")
        game.msg_id['detain_button'] = ret_msg.message_id

    def ask_assassinate(self, chat_id):
        game = self.games[chat_id]

        user_id = game.current_player().user_id
        user_name = game.players[user_id].user_name

        keyboard = [[]]
        i = 0
        keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data='取消', text='<- 返回'))

        for target_id, target_player in game.players.items():
            if len(keyboard[i]) >= 4:
                keyboard.append([])
                i += 1
            if target_player.can_be_assassinate(user_id):
                keyboard[i].append(tg.InlineKeyboardButton(
                    callback_data=target_id, text=target_player.status()))

        self.bot.delete_message(chat_id, game.msg_id['action_button'])

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {user_name} 想要刺殺誰？")
        game.msg_id['assassinate_button'] = ret_msg.message_id

    def ask_avoid_detain(self, chat_id):
        game = self.games[chat_id]

        suspect = game.players[game.detain_event['suspect']]

        keyboard = [[
            tg.InlineKeyboardButton(callback_data=1, text='要'),
            tg.InlineKeyboardButton(callback_data=-1, text='不要')],[
        ]]

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {suspect.user_name} 你要公開自己的身份來避免關押嗎？")
        game.msg_id['avoid_detain_button'] = ret_msg.message_id

    def ask_stop_assassinate(self, chat_id):
        game = self.games[chat_id]

        protectors = game.assassinate_event['protector']
        protectors = ', '.join([game.players[p].user_name.strip() for p in protectors])

        keyboard = [[
            tg.InlineKeyboardButton(callback_data=1, text='要'),
            tg.InlineKeyboardButton(callback_data=-1, text='不要')],[
        ]]

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {protectors} 你要公開自己的身份來阻止刺殺嗎？")
        game.msg_id['stop_assassinate_button'] = ret_msg.message_id

    def ask_join(self, chat_id, user_id):
        game = self.games[chat_id]

        caller = game.players[user_id]
        # protectors = ', '.join([game.players[p].user_name.strip() for p in protectors])

        keyboard = [[
            tg.InlineKeyboardButton(callback_data=1, text='要'),
            tg.InlineKeyboardButton(callback_data=-1, text='不要')],[
        ]]

        ret_msg = self.bot.send_message(
            chat_id,
            reply_markup=tg.InlineKeyboardMarkup(keyboard),
            text=f"[動作] {caller.user_name} 號召了革命 你要公開自己的身份來響應嗎？")
        game.msg_id['join_button'] = ret_msg.message_id

    def button_handler(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        chat_id, user_id, user_name, message_id = util.message_info(query.message)
        
        game = self.games[chat_id]
        #print(game.wait_register_button_m_id)
        if query.message.message_id == game.msg_id.setdefault('register_button', None):
            self.button_handler_register(update)
        elif query.message.message_id == game.msg_id.setdefault('action_button', None):
            self.button_handler_action(update)
        elif query.message.message_id == game.msg_id.setdefault('peek_button', None):
            self.button_handler_peek(update)
        elif query.message.message_id == game.msg_id.setdefault('switch_button', None):
            self.button_handler_switch(update)
        elif query.message.message_id == game.msg_id.setdefault('check_button', None):
            self.button_handler_check(update)
        elif query.message.message_id == game.msg_id.setdefault('hide_button', None):
            self.button_handler_hide(update)
        elif query.message.message_id == game.msg_id.setdefault('execute_button', None):
            self.button_handler_execute(update)
        elif query.message.message_id == game.msg_id.setdefault('detain_button', None):
            self.button_handler_detain(update)
        elif query.message.message_id == game.msg_id.setdefault('avoid_detain_button', None):
            self.button_handler_avoid_detain(update)
        elif query.message.message_id == game.msg_id.setdefault('assassinate_button', None):
            self.button_handler_assassinate(update)
        elif query.message.message_id == game.msg_id.setdefault('stop_assassinate_button', None):
            self.button_handler_stop_assassinate(update)
        elif query.message.message_id == game.msg_id.setdefault('join_button', None):
            self.button_handler_join(update)

    def button_handler_register(self, update):
        query = update.callback_query
        #query.answer(text="處理中...", show_alert=True)
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.check_state(GameState.REGISTER):
                data = int(query.data)

                if data == 4:
                    if user_id == game.admin_id:
                        game.set_state(GameState.TURN_START)
                        self.bot.delete_message(chat_id, game.msg_id['register_button'])
                        self.bot.send_message(chat_id, f'[公告] 遊戲開始')
                        game.start_game()
                        self.ask_action(chat_id)

                else:
                    if data == 0:
                        game.add_player(user_id, user_name)
                    elif data == 1:
                        game.remove_player(user_id)
                    elif data == 2:
                        if user_id == game.admin_id:
                            while len(game.players) < 5:
                                game.add_player(ai=True)
                    elif data == 3:
                        if user_id == game.admin_id:
                            game.remove_player(ai=True)            
                
                    self.bot.edit_message_text(
                        f"[公告] 目前報名有：{game.print_players_list()}",
                        chat_id, game.msg_id['register_players']
                    )
                
            # else:
            #     self.bot.send_message(chat_id, f'等等啦 有人還在玩')

    def button_handler_action(self, update: Update):
        query = update.callback_query
        #query.answer(text="處理中...", show_alert=True)
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.check_state(GameState.TURN_START):
                if query.data == 'skip' and user_id == game.admin_id:
                    self.action_handler([{
                        'type': BotAction.ANNOUNCE,
                        'message': f'[動作] {game.current_player().user_name} 回合被跳過了',
                        }], chat_id=chat_id)
                    self.bot.delete_message(chat_id, game.msg_id['action_button'])
                    game.next_player()
                    self.ask_action(chat_id)
                elif query.data == str(GameAction.PEEK) and game.legal_player(GameAction.PEEK, user_id):
                    self.ask_peek(chat_id)
                elif query.data == str(GameAction.SWITCH) and game.legal_player(GameAction.SWITCH, user_id):
                    self.ask_switch(chat_id)
                elif query.data == str(GameAction.CHECK) and game.legal_player(GameAction.CHECK, user_id):
                    callback, actions = self.manager.check_character(
                        game, user_id
                    )
                    self.action_handler(actions, query=query)
                elif query.data == str(GameAction.REVEAL) and game.legal_player(GameAction.REVEAL, user_id):
                    callback, actions = self.manager.reveal_character(
                        game, game.current_player().user_id
                    )
                    self.action_handler(actions, chat_id=chat_id)
                    if callback:
                        self.bot.delete_message(chat_id, game.msg_id['action_button'])
                        self.ask_action(chat_id)
                elif query.data == str(GameAction.HIDE) and game.legal_player(GameAction.HIDE, user_id):
                    self.ask_hide(chat_id)
                elif query.data == str(GameAction.EXECUTE) and game.legal_player(GameAction.EXECUTE, user_id):
                    self.ask_execute(chat_id)
                elif query.data == str(GameAction.DETAIN) and game.legal_player(GameAction.DETAIN, user_id):
                    self.ask_detain(chat_id)
                elif query.data == str(GameAction.ASSASSINATE) and game.legal_player(GameAction.ASSASSINATE, user_id):
                    self.ask_assassinate(chat_id)
                elif query.data == str(GameAction.CALL) and game.legal_player(GameAction.CALL, user_id):
                    game.revolution_event = {
                        'joined': user_id,
                        'called': game.neighbor(user_id),
                    }
                    self.ask_join(chat_id, user_id)

    def button_handler_peek(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.PEEK, user_id):
                if query.data == '取消':
                    self.bot.delete_message(chat_id, game.msg_id['peek_button'])
                    self.ask_action(chat_id)
                else:
                    target_id = int(query.data)
                    callback, actions = self.manager.peek_character(
                        game, game.current_player().user_id, target_id)
                    self.action_handler(actions, query=query, chat_id=chat_id)
                    if callback:
                        self.bot.delete_message(chat_id, game.msg_id['peek_button'])
                        game.next_player()
                        self.ask_action(chat_id)

    def button_handler_switch(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.SWITCH, user_id):
                if query.data == '取消':
                    self.bot.delete_message(chat_id, game.msg_id['switch_button'])
                    self.ask_action(chat_id)
                else:
                    target_id = int(query.data)
                    callback, actions = self.manager.switch_character(
                        game, game.current_player().user_id, target_id)
                    self.action_handler(actions, query=query, chat_id=chat_id)
                    if callback:
                        self.bot.delete_message(chat_id, game.msg_id['switch_button'])
                        game.next_player()
                        self.ask_action(chat_id)

    def button_handler_hide(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.HIDE, user_id):
                if query.data == '取消':
                    self.bot.delete_message(chat_id, game.msg_id['hide_button'])
                    self.ask_action(chat_id)
                else:
                    target_id = int(query.data)
                    callback, actions = self.manager.switch_character(
                        game, game.current_player().user_id, target_id, hide=True
                    )
                    self.action_handler(actions, query=query, chat_id=chat_id)
                    if callback:
                        self.bot.delete_message(chat_id, game.msg_id['hide_button'])
                        game.next_player()
                        self.ask_action(chat_id)

    def button_handler_execute(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.EXECUTE, user_id):
                if query.data == '取消':
                    self.bot.delete_message(chat_id, game.msg_id['execute_button'])
                    self.ask_action(chat_id)
                else:
                    target_id = int(query.data)
                    callback, actions = self.manager.execute(
                        game, game.current_player().user_id, target_id)
                    self.action_handler(actions, query=query, chat_id=chat_id)
                    if callback:
                        self.bot.delete_message(chat_id, game.msg_id['execute_button'])
                        game.next_player()
                        self.ask_action(chat_id)

    def button_handler_detain(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.DETAIN, user_id):
                if query.data == '取消':
                    self.bot.delete_message(chat_id, game.msg_id['detain_button'])
                    self.ask_action(chat_id)
                else:
                    target_id = int(query.data)
                    game.detain_event = {
                        'guard': game.current_player().user_id, 
                        'suspect': target_id
                    }
                    print(game.detain_event)
                    self.action_handler([{
                        'type': BotAction.ANNOUNCE,
                        'message': f'[動作] {game.current_player().user_name} 嘗試關押 {game.players[target_id].user_name}',
                        }], chat_id=chat_id)
                    self.bot.delete_message(chat_id, game.msg_id['detain_button'])
                    self.ask_avoid_detain(chat_id)

    def button_handler_avoid_detain(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        print(user_id, user_name)
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.AVOID_DETAIN, user_id):
                if int(query.data) > 0:
                    callback, actions = self.manager.avoid_detain(
                        game)
                else:
                    callback, actions = self.manager.detain(
                        game)
                self.action_handler(actions, query=query, chat_id=chat_id)
                if callback:
                    self.bot.delete_message(chat_id, game.msg_id['avoid_detain_button'])
                    game.next_player()
                    self.ask_action(chat_id)

    def button_handler_assassinate(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.ASSASSINATE, user_id):
                if query.data == '取消':
                    self.bot.delete_message(chat_id, game.msg_id['assassinate_button'])
                    self.ask_action(chat_id)
                else:
                    target_id = int(query.data)
                    game.assassinate_event = {
                        'killer': game.current_player().user_id,
                        'victim': target_id,
                        'protector': game.neighbor(target_id),
                    }
                    self.action_handler([{
                        'type': BotAction.ANNOUNCE,
                        'message': f'[動作] {game.current_player().user_name} 嘗試刺殺 {game.players[target_id].user_name}',
                        }], chat_id=chat_id)
                    print(game.assassinate_event)
                    self.bot.delete_message(chat_id, game.msg_id['assassinate_button'])
                    if len(game.assassinate_event['protector']):
                        self.ask_stop_assassinate(chat_id)
                    else:
                        callback, actions = self.manager.assassinate(game)
                        self.action_handler(actions, query=query, chat_id=chat_id)
                        if callback:
                            game.next_player()
                            self.ask_action(chat_id)

    def button_handler_stop_assassinate(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        # print(user_id, user_name)
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.STOP_ASSASSINATE, user_id):
                if int(query.data) > 0:
                    callback, actions = self.manager.stop_assassinate(
                        game, user_id)
                else:
                    game.assassinate_event['protector'].remove(user_id)
                    callback, actions = self.manager.assassinate(game)
                self.action_handler(actions, query=query, chat_id=chat_id)
                if callback:
                    self.bot.delete_message(chat_id, game.msg_id['stop_assassinate_button'])
                    game.next_player()
                    self.ask_action(chat_id)

    def button_handler_join(self, update: Update):
        query = update.callback_query
        
        chat_id, _, _, _ = util.message_info(query.message)
        user_id = query.from_user.id
        user_name = query.from_user.full_name
        # print(user_id, user_name)
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.legal_player(GameAction.JOIN, user_id):
                if int(query.data) > 0:
                    callback, actions = self.manager.join(
                        game, user_id)
                else:
                    game.revolution_event['called'].remove(user_id)
                    # callback, actions = self.manager.join(
                    #     game, user_id, False)
                self.action_handler(actions, query=query, chat_id=chat_id)
                callback, actions = self.manager.check_revolution(game)
                if callback:
                    self.bot.delete_message(chat_id, game.msg_id['join_button'])
                    if game.winner is not None:
                        self.endgame(chat_id)
                    else:
                        game.next_player()
                        self.ask_action(chat_id)

    def endgame(self, chat_id):
        game = self.games[chat_id]
        if game.winner == 'loyal':
            self.action_handler([{
                'type': BotAction.ANNOUNCE,
                'message': f'[結束] 保皇黨 勝利！ 遊戲結束'
            }], chat_id=chat_id)
        elif game.winner == 'rebel':
            self.action_handler([{
                'type': BotAction.ANNOUNCE,
                'message': f'[結束] 反叛軍 勝利！ 遊戲結束'
            }], chat_id=chat_id)
        del self.games[chat_id]


    def action_handler(self, actions, **kwargs):
        for action in actions:
            if action['type'] == BotAction.PRIVATE:
                kwargs['query'].answer(text=action['message'], show_alert=True)
            elif action['type'] == BotAction.ANNOUNCE:
                self.bot.send_message(kwargs['chat_id'], action['message'])
            elif action['type'] == BotAction.ILLEGAL:
                kwargs['query'].answer(text=action['message'], show_alert=True)



            

   

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    with open('XTalkSultanBot.token', 'r') as f:
        updater = Updater(f.read(), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    game_bot = SultanBot(bot=updater.bot)
    dispatcher.add_handler(CommandHandler("newgame", game_bot.newgame))
    # dispatcher.add_handler(CommandHandler("spy", spy_bot.spy))
    # dispatcher.add_handler(CommandHandler("set_words", spy_bot.set_words))
    # dispatcher.add_handler(CommandHandler("game", spy_bot.game))
    # dispatcher.add_handler(CommandHandler("clue", spy_bot.clue))
    # dispatcher.add_handler(CommandHandler("skip", spy_bot.skip))
    # dispatcher.add_handler(CommandHandler("skip_all", spy_bot.skip_all))
    # dispatcher.add_handler(CommandHandler("set_host", spy_bot.set_host))
    # dispatcher.add_handler(CommandHandler("set_state", spy_bot.set_state))
    # dispatcher.add_handler(CommandHandler("kill", spy_bot.kill))
    # dispatcher.add_handler(CommandHandler("poll", spy_bot.poll))
    # dispatcher.add_handler(CommandHandler("remain", spy_bot.remain))
    # dispatcher.add_handler(CommandHandler("end_poll", spy_bot.end_poll))
    # dispatcher.add_handler(CommandHandler("init", spy_bot.init))
    # dispatcher.add_handler(CommandHandler("reset", spy_bot.reset))
    # dispatcher.add_handler(CommandHandler("history", spy_bot.history))
    # dispatcher.add_handler(CommandHandler("tutorial", spy_bot.tutorial))

    dispatcher.add_handler(CallbackQueryHandler(game_bot.button_handler))

    # on noncommand i.e message - echo the message on Telegram
    #dispatcher.add_handler(MessageHandler(Filters.photo, meow_bot.jpg2png))
    #dispatcher.add_handler(MessageHandler(Filters.all, meow_bot.jpg2png))
    #dispatcher.add_handler(MessageHandler(Filters.all, meow_bot.meow))
    #dispatcher.add_handler(MessageHandler(Filters.document.file_extension('txt'), meow_bot.meow))

    # Start the Bot
    updater.start_polling(drop_pending_updates=True)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
