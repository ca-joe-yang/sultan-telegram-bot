from .Action import GameAction
from .State import State as GameState
from .Game import SultanGame

import numpy as np
import telegram as tg
import time
import os

from PIL import Image

GAME_COUNT = 0

class SultanManager:

    def __init__(self, bot, chat_id, debug=True):
        ### DEBUG MODE
        self.debug = debug
        ###

        self.game_state = GameState.NO_GAME
        self.bot = bot
        self.chat_id = chat_id

        self.sleep = 10

        with open('README.md', 'r') as f:
            self.tutorial_str  = f.read()

        global GAME_COUNT
        GAME_COUNT += 1
        self.game_id = GAME_COUNT

        self.send_announce(f'[初始] {self.game_id} 號房已建立')

    def new_game(self, user_id, user_name=None, debug=True):
        self.game = SultanGame(debug=debug)
        self.game_image_fname = f'game_pics/{self.chat_id}.jpg'

        self.game_state = GameState.IDLE
        self.admin_id = user_id
        self.admin_name = user_name
        self.msg_history = {}
        self.button_id2name = {}

        self.send_announce(
            f'[公告] 目前主持人為 {user_name}')

    def start_register(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Start register')
        ###
        keyboard = [[
            tg.InlineKeyboardButton(
                callback_data='join', text='加入'),
            tg.InlineKeyboardButton(
                callback_data='exit', text='退出')
        ],[
            tg.InlineKeyboardButton(
                callback_data='add_ai', text='[管理] 增加AI'),
            tg.InlineKeyboardButton(
                callback_data='remove_ai', text='[管理] 減少AI')
        ],[
            tg.InlineKeyboardButton(
                callback_data='start', text='[管理] 開始遊戲'),
        ]]
        self.send_buttons(
            f"[公告] {self.admin_name} 想要玩 推翻蘇丹，你要加入嗎？",
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='register_button'
        )
        self.send_announce(
            f"[公告] 目前報名有：{self.game.print_players_list()}",
            name='register_players'
        )
        self.game_state = GameState.REGISTER

    def do_register(self, query):
        ### DEBUG MODE
        if self.debug:
            print(f'Do register: {query.data}')
        ###
        data = query.data
        user_id = query.from_user.id
        user_name = query.from_user.full_name.strip()

        if data == 'start' and self.is_admin(user_id):
            ### DEBUG MODE
            if self.debug:
                print(f'Start')
            ###
            if 5 <= len(self.game.players) <= 15:
                self.start_game()
                return
            else:
                message = '[通知] 玩家人數必須介於 5 到 15 人'
                self.send_pop_up(message, query)
        
        elif data == 'join':
            ### DEBUG MODE
            if self.debug:
                print(f'Join {user_name} {user_id}')
            ###
            if user_id in self.game.players:
                message = f'[通知] 你已經加入遊戲了'
            else:
                try:
                    user_photo_fname = f'user_pics/{user_id}.jpg'
                    if not os.path.isfile(user_photo_fname):
                        photo_json = self.bot.get_user_profile_photos(user_id)
                        photo_id = photo_json.photos[0][-1].file_id
                        # print(profile_photo)
                        # profile_photo = profile_photo[0][0].get_file()
                        file = self.bot.get_file(photo_id)
                        file.download(user_photo_fname)
                    profile_photo = Image.open(user_photo_fname)
                except:
                    print(photo_json)
                    profile_photo = None
                self.game.add_player(user_id, user_name, 
                    profile_photo)
                message = f'[通知] 成功加入遊戲'
            self.send_pop_up(message, query)
        elif data == 'exit':
            ### DEBUG MODE
            if self.debug:
                print(f'Exit {user_name} {user_id}')
            ###
            if user_id in self.game.players:
                self.game.remove_player(user_id, user_name)
                message = f'[通知] 成功退出遊戲'
            else:
                message = f'[通知] 你不在遊戲中'
            self.send_pop_up(message, query)
        elif data == 'add_ai' and self.is_admin(user_id):
            ### DEBUG MODE
            if self.debug:
                print(f'Add ai')
            ###
            for _ in range(3):
                # print(self.game.players)
                self.game.add_player(ai=True)
        elif data == 'remove_ai' and self.is_admin(user_id):
            ### DEBUG MODE
            if self.debug:
                print(f'Remove ai')
            ###
            self.game.remove_player(ai=True)
        self.send_announce(
            f"[公告] 目前報名有：{self.game.print_players_list()}",
            name='register_players',
            refresh=True
        )

    def send_announce(self, text, name=None, refresh=False):
        ### DEBUG MODE
        if self.debug:
            print(f'[Announce] {name}: {text}')
        ###
        if name is not None:
            if name == 'turn':
                name = self.game.turn_id
            if name in self.msg_history:
                if not refresh:
                    text = self.msg_history[name]['text'] + '\n' + text
                msg = self.bot.edit_message_text(
                    text,
                    self.chat_id, self.msg_history[name]['id']
                )
            else:
                msg = self.bot.send_message(self.chat_id, text)
            
            self.msg_history[name] = {
                'type': 'announce',
                'id': msg.message_id,
                'text': text
            } 
        else:
            self.bot.send_message(self.chat_id, text)

    def send_pop_up(self, text, query):
        ### DEBUG MODE
        if self.debug:
            print(f'[Popup] {text}')
        ###
        query.answer(text=text, show_alert=True)

    def send_private(self, text, user_id, name=None):
        ### DEBUG MODE
        if self.debug:
            print(f'[private] {user_id}: {text}')
        ###
        msg = self.bot.send_message(user_id, text)
        # if name is not None:
        # self.msg_history[name] = {
        #     'type': 'private',
        #     'user_id': user_id,
        #     'id': msg.message_id,
        #     'text': text
        # }

    def send_buttons(self, text, markup, legal_ids=None, name=None):
        ### DEBUG MODE
        if self.debug:
            print(f'[Button] {name} {text}')
        ###        
        msg = self.bot.send_message(
            self.chat_id,
            reply_markup=markup,
            text=text)

        if name is not None:
            self.msg_history[name] = {
                'type': 'button',
                'id': msg.message_id,
                'markup': markup,
                'text': text,
                'legal_ids': legal_ids
            }
            self.button_id2name[msg.message_id] = name

    def delete_message(self, name):
        if name in self.msg_history:
            ### DEBUG MODE
            if self.debug:
                print(f'Delete {name}: {self.msg_history[name]}')
            ###
            try:
                self.bot.delete_message(
                    self.chat_id, self.msg_history[name]['id'])
            except:
                print(f'Message {name} not found')
                print(self.msg_history)
            del self.msg_history[name]

    def send_visual(self, name=None):
        p = open(self.game_image_fname, 'rb')
        if name is not None and name in self.msg_history:
            self.delete_message(name)
        msg = self.bot.send_photo(self.chat_id, p)
        if name is not None:
            self.msg_history[name] = {
                'type': 'image',
                'id': msg.message_id
            }

    def draw_game_image(self):
        self.game.draw_game_image()
        self.game.game_image.save(self.game_image_fname)

    def start_game(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Start game')
        ###
        self.delete_message('register_button')
        self.send_announce(
            f'[開始] 遊戲開始 請大家查看自己的身份', name='start')
        self.game.start_game()
        player_order_str = ', '.join([ 
            f'({self.game.players[p].order+1}) {self.game.players[p].user_name}'\
            for p in self.game.player_orders ])
        self.send_announce(
            f'[開始] 玩家順序為 {player_order_str}', name='start')
        self.draw_game_image()
        self.send_visual('visual')
        self.ask_general(first=True)

    def end_game(self):
        ### DEBUG MODE
        if self.debug:
            print(f'End game')
        ###
        if self.game.winner == 'loyal':
            self.send_announce(
                f'[結束] {self.game.win_condition} 保皇黨 勝利！', name='end')
            player_str = ', '.join([
                f'{self.game.players[p].user_name}'\
                for p in self.game.players  \
                if self.game.players[p].is_winner('loyal', self.game)])
            self.send_announce(
                f'[結束] 勝利玩家： {player_str}', name='end')
        elif self.game.winner == 'rebel':
            self.send_announce(
                f'[結束] {self.game.win_condition} 反叛軍 勝利！', name='end')
            player_str = ', '.join([ 
                f'{self.game.players[p].user_name}'\
                for p in self.game.players \
                if self.game.players[p].is_winner('rebel', self.game)])
            self.send_announce(
                f'[結束] 勝利玩家： {player_str}', name='end')
        else:
            raise
        self.draw_game_image()
        self.send_visual('visual')
        # self.send_announce(f'[公告] 遊戲結束')
        self.game_state = GameState.IDLE

    def start_turn(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Start turn')
        ###
        self.game_state = GameState.TURN_START
        cur_player = self.game.current_player()
        self.send_announce(
            f'[回合{self.game.turn_id+1}] {cur_player.user_name}' ,
            name='turn')

        self.draw_game_image()
        self.send_visual('visual')
        self.ask_general()

        
        if cur_player.throne_countdown is not None:
            cur_player.throne_countdown -= 1
        
        if self.game.check_win_condition(turn_start=True):
            self.end_game()
            return

        if cur_player.is_jail():
            self.send_announce(
                f'[公告] {cur_player.user_name} 出獄',
                name='turn'
            )
            cur_player.jail = False
            self.end_turn()
            return
        if cur_player.is_captured():
            self.send_announce(
                f'[公告] {cur_player.user_name} 被捕中',
                name='turn'
            )
            self.end_turn()
            return

        if cur_player.is_ai():
            time.sleep(self.sleep)
        
        self.ask_action()

    def end_turn(self):
        ### DEBUG MODE
        if self.debug:
            print(f'End turn')
        ###
        self.game_state = GameState.TURN_END
        if self.game.check_win_condition():
            self.end_game()
            return
        cur_player = self.game.current_player()
        print(self.game.current_player().user_name)
        if cur_player.is_exhaust():
            cur_player.exhaust = False

        self.game.next_player()
        print(self.game.current_player().user_name)

        self.start_turn()

    def ask_general(self, first=False):
        if 'general_button' in self.msg_history:
            try:
                self.delete_message('general_button')
            except:
                pass

        keyboard = [[], []]

        keyboard[0].append(tg.InlineKeyboardButton(
            callback_data=GameAction.CHECK.value, text=str(GameAction.CHECK)))        
        keyboard[0].append(tg.InlineKeyboardButton(
            callback_data=GameAction.TUTORIAL.value, text=str(GameAction.TUTORIAL)))
        keyboard[1].append(tg.InlineKeyboardButton(
            callback_data=GameAction.SKIP.value, text=str(GameAction.SKIP)))
        keyboard[1].append(tg.InlineKeyboardButton(
            callback_data=GameAction.RESTART.value, text=str(GameAction.RESTART)))

        if first:
            self.game_state = GameState.CHECK
            self.checked_players = [ p \
            for p in self.game.player_orders if self.game.players[p].is_ai() ]
            if len(self.checked_players) == len(self.game.player_orders):
                self.start_turn()
                return

        self.send_buttons(
            text='[通用按鈕]',
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='general_button'
        )

    def do_general(self, query):
        ### DEBUG MODE
        if self.debug:
            print(f'Do general: {query.data}')
        ###
        user_id = query.from_user.id
        user_name = query.from_user.full_name.strip()

        action = GameAction(int(query.data))

        if action == GameAction.SKIP and self.is_admin(user_id) \
        and self.game_state.in_turn():
            self.send_announce(
                f'[管理] {self.game.current_player().user_name} 回合被管理者跳過了',
                name='turn')
            self.end_turn()

        elif action == GameAction.RESTART and self.is_admin(user_id) \
        and self.game_state.in_turn():
            self.send_announce(
                f'[管理] {self.game.current_player().user_name} 回合被管理者重啟了',
                name='turn')
            self.start_turn()

        elif action == GameAction.CHECK:
            info = self.game.get_player_information(
                user_id, self.game_state == GameState.IDLE)
            message = '\n'.join(info)
            self.send_pop_up(f'[查看]\n{message}', query)
            if self.game_state == GameState.CHECK \
            and user_id in self.game.player_orders \
            and user_id not in self.checked_players:
                self.checked_players.append(user_id)
                if len(self.checked_players) == len(self.game.player_orders):
                    self.start_turn()

        elif action == GameAction.TUTORIAL:
            self.send_tutorial(user_id)

    def send_tutorial(self, user_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Send tutorial')
        ###
        self.send_private(self.tutorial_str, user_id)

    def ask_action(self, user_id=None, just_reveal=False, manipulate=False):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask action')
        ###
        self.game_state = GameState.TURN_START

        if user_id is None:
            cur_player = self.game.current_player()
        else:
            cur_player = self.game.players[user_id]
        

        if cur_player.is_ai():
            action, target_ids = cur_player.ai_action(
                self.game, manipulate=manipulate)
            self.do_action(
                action=action,
                from_id=cur_player.user_id,
                target_ids=target_ids)
        else:
            action_choices = cur_player.action_choices(
                just_reveal, manipulate)

            keyboard = self.generate_keyboard_action(
                action_choices, max_len=2)
            self.send_buttons(
                f"[詢問] 輪到 {cur_player.user_name}，想要採取甚麼行動？",
                markup=tg.InlineKeyboardMarkup(keyboard),
                name='action_button',
                legal_ids=[cur_player.user_id]
            )

    def do_action(self, query=None, action=None, from_id=None, target_ids=[None]):
        ### DEBUG MODE
        if self.debug:
            print(f'Do action {query}')
        ###
        if query is not None:
            action = GameAction(int(query.data))
            from_id = query.from_user.id
            # print(action, self.msg_history['action_button'], from_id)
            if not (from_id in self.msg_history['action_button']['legal_ids'] \
            or (action == GameAction.THRONE \
            and self.game.players[from_id].is_sultan())):
                return                
            ### DEBUG MODE
            if self.debug:
                print(f'{query.data} {action}')
            ###
        from_player = self.game.players[from_id]

        self.game_state = GameState.TURN_MID
        self.delete_message('action_button')

        if action == GameAction.REVEAL:
            self.do_reveal(from_id)
            self.ask_action(just_reveal=True)

        elif action == GameAction.PEEK:
            if from_player.is_ai():
                self.do_peek(from_id=from_id, target_id=target_ids[0])
            else:
                self.ask_peek(from_id=from_id)
        
        elif action == GameAction.SWITCH:
            if from_player.is_ai():
                self.do_switch(from_id=from_id, target_id=target_ids[0])
            else:
                self.ask_switch(from_id=from_id)
        
        elif action == GameAction.EXECUTE:
            if from_player.is_ai():
                self.do_execute(from_id=from_id, target_id=target_ids[0])
            else:
                self.ask_execute(from_id=from_id)

        elif action == GameAction.DETAIN:
            if from_player.is_ai():
                self.do_detain(from_id=from_id, target_id=target_ids[0])
            else:
                self.ask_detain(from_id=from_id)
            
        elif action == GameAction.ASSASSINATE:
            if from_player.is_ai():
                self.do_assassinate(from_id=from_id, target_id=target_ids[0])
            else:
                self.ask_assassinate(from_id=from_id)

        elif action == GameAction.CALL:
            self.do_call(from_id=from_id)

        elif action == GameAction.THRONE:
            if query is not None \
            and self.game.players[from_id].is_sultan():
                self.do_reveal(from_id)
                self.ask_action()

        elif action == GameAction.CAPTURE:
            if from_player.is_ai():
                self.do_capture(from_id=from_id, target_id=target_ids[0])
            else:
                self.ask_capture(from_id=from_id)

        elif action == GameAction.DANCE:
            self.do_dance(from_id=from_id)

        elif action == GameAction.MANIPULATE:
            if from_player.is_ai():
                self.do_support(from_id=from_id, support_team=target_ids[0])
            else:
                if not hasattr(self.game, 'manipulate_event'):
                    self.ask_support(from_id=from_id)
                else:
                    self.ask_manipulate(from_id=from_id)

        elif action == GameAction.PREDICT:
            if not hasattr(self.game, 'predict_event'):
                self.game.predict_event = {
                    'peeked': [],
                    'predict_team': None,
                    'choices': None,
                }
            if from_player.is_ai():
                if from_player.is_hidden():
                    self.do_reveal(from_id)
                for i in target_ids:
                    self.do_peek(
                        from_id=from_id, target_id=i, end=False)
                predict_team = from_player.ai_predict(self.game)
                self.do_predict(
                    from_id=from_id, predict_team=predict_team)
            else:
                self.ask_predict_peek(from_id=from_id)

    def do_reveal(self, player_id, verbose=True):
        ### DEBUG MODE
        if self.debug:
            print(f'Do reveal')
        ###
        player = self.game.players[player_id]
        if player.is_hidden():
            player.hidden = False
            if verbose:
                self.send_announce(
                    f'[動作] {player.user_name} 公開了他的身份為 {player.character}',
                    name='turn')
            
            if player.is_sultan():
                self.game.sultan_id = player_id
                self.game.current_player().throne_countdown = 1
                self.send_announce(
                    f'[公告] 登基程序開始 到下一次 {self.game.current_player().user_name} 的回合',
                    name='turn')

    def do_hide(self, player_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Do hide')
        ###
        player = self.game.players[player_id]
        if player.is_known():
            if player.character == Character.VIZIER:
                if hasattr(self.game, 'manipulate_event'):
                    delattr(self.game, 'manipulate_event')
            elif player.character == Character.PROPHET:
                if hasattr(self.game, 'predict_event'):
                    delattr(self.game, 'predict_event')
            elif player.character == Character.SLAVEDRIVER:
                self.do_release_slaves(user_id)
            elif player.character == Character.SULTAN:
                for _, player in self.game.players.items():
                    player.throne_countdown = None

        player.hidden = True
        
    def ask_peek(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask peek')
        ###
        from_player = self.game.players[from_id]

        choices = self.game.can_be_peek_by(from_player.user_id)
        keyboard = self.generate_keyboard_player(choices, cancel=True)

        self.send_buttons(
            f"[詢問] {from_player.user_name} 想要偷看誰的身份？",
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='peek_button', legal_ids=[from_id]
        )

    def do_peek(self, query=None, from_id=None, target_id=None, end=True):
        ### DEBUG MODE
        if self.debug:
            print(f'Do peek')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['peek_button']['legal_ids']:
                return
            self.delete_message('peek_button')
            if query.data == str(GameAction.CANCEL):
                self.ask_action()
                return
            else:
                target_id = int(query.data)

        player_1 = self.game.players[from_id]
        player_2 = self.game.players[target_id]

        if query is not None:
            peek_message = f'[通知] {player_2.user_name} 目前的身份是 {player_2.character}'
            self.send_pop_up(
                peek_message,
                query=query
            )
            player_1.memo = peek_message
        self.send_announce(
            f'[動作] {player_1.user_name} 偷看了 {player_2.user_name} 的身份',
            name='turn'
        )
        if end:
            self.end_turn()

    def ask_switch(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask switch')
        ###
        from_player = self.game.players[from_id]
        hide = from_player.is_known()
            
        choices = self.game.can_be_switch_by(from_player.user_id, hide=hide)
        keyboard = self.generate_keyboard_player(choices, cancel=True)

        if hide:
            message = f"[詢問] {from_player.user_name} 隱藏身份後 想要偷偷和誰的身份交換？"
        else:
            message = f"[詢問] {from_player.user_name} 想要和誰的身份交換？"
        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='switch_button', legal_ids=[from_id]
        )

    def do_switch(self, query=None, from_id=None, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do switch')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['switch_button']['legal_ids']:
                return
            self.delete_message('switch_button')
            if query.data == str(GameAction.CANCEL):
                self.ask_action()
                return
            else:
                target_id = int(query.data)

        player_1 = self.game.players[from_id]
        player_2 = self.game.players[target_id]
        hide = player_1.is_known()
    
        if hide:
            self.game.do_hide(from_id)
            message = f'[動作] {player_1.user_name} 隱藏了身份 並偷偷和某人交換了身份'
        else:
            message = f'[動作] {player_1.user_name} 和 {player_2.user_name} 交換了身份'

        self.game.do_switch(from_id, target_id)
        self.send_announce(message, name='turn')
        
        if query is not None:
            peek_message = f'[通知] 你 目前的身份是 {player_1.character}'
            self.send_pop_up(
                peek_message,
                query=query
            )
            player_1.memo = peek_message

        if player_1.must_switch:
            player_1.must_switch = False

        self.end_turn()

    def ask_execute(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask execute')
        ###
        from_player = self.game.players[from_id]
            
        choices = self.game.can_be_execute_by(from_player.user_id)
        keyboard = self.generate_keyboard_player(
            choices, cancel=True)

        message = f"[詢問] {from_player.user_name} 你想要處決誰？"
        name = 'execute_button'
        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name, legal_ids=[from_id]
        )

    def do_execute(self, query=None, from_id=None, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do execute')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['execute_button']['legal_ids']:
                return
            self.delete_message('execute_button')
            if query.data == str(GameAction.CANCEL):
                self.ask_action()
                return
            elif query.data == str(GameAction.GIVEUP):
                target_id = None
            else:
                target_id = int(query.data)

        player_1 = self.game.players[from_id]
        if player_1.is_hidden():
            self.do_reveal(from_id)

        if target_id is not None:
            
            player_2 = self.game.players[target_id]
        
            self.game.do_kill(target_id)
            
            message = f'[動作] {player_1.user_name} 處決了 {player_2.user_name}'
        else:
            message = f'[動作] 沒有人可以處決，{player_1.user_name} 放棄了行動'

        self.send_announce(message, name='turn')
        self.end_turn()

    def ask_detain(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask detain')
        ###
        from_player = self.game.players[from_id]

        choices = self.game.can_be_detain_by(from_player.user_id)
        keyboard = self.generate_keyboard_player(choices, cancel=True)

        message = f"[詢問] {from_player.user_name} 你想要關押誰？"
        name = 'detain_button'
        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name, legal_ids=[from_id]
        )

    def do_detain(self, query=None, from_id=None, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do detain')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['detain_button']['legal_ids']:
                return
            self.delete_message('detain_button')
            if query.data == str(GameAction.CANCEL):
                self.ask_action()
                return
            elif query.data == str(GameAction.GIVEUP):
                target_id = None
            else:
                target_id = int(query.data)

        player_1 = self.game.players[from_id]

        if player_1.neighbor_is_dancing(self.game):
            self.send_pop_up(
                f'[通知] 附近有舞孃 無法關押',
                query=query)
            self.ask_detain(from_id=from_id)


        if target_id is not None:
            player_2 = self.game.players[target_id]

            if player_1.is_hidden():
                self.do_reveal(from_id)

            self.game.detain_event = {
                'guard': from_id,
                'suspect': target_id
            }

            message = f'[動作] {player_1.user_name} 嘗試關押 {player_2.user_name}'
            self.send_announce(message, name='turn')

            suspect = self.game.players[target_id]
            if suspect.is_ai():
                self.do_detain_reaction(avoid_detain=suspect.ai_avoid_detain())
            elif suspect.is_known() and not suspect.can_avoid_detain():
                self.do_detain_reaction(avoid_detain=False)
            else:
                self.ask_detain_reaction()
        else:
            message = f'[動作] 沒有人可以關押，{player_1.user_name} 放棄了行動'
            self.send_announce(message, name='turn')

    def ask_detain_reaction(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask avoid detain')
        ###
        guard = self.game.players[self.game.detain_event['guard']]
        suspect = self.game.players[self.game.detain_event['suspect']]

        keyboard = [[
            tg.InlineKeyboardButton(callback_data=1, text='要'),
            tg.InlineKeyboardButton(callback_data=-1, text='不要'),
        ]]

        message = f"[詢問] {suspect.user_name} 你要公開自己的身份來避免關押嗎？"
        name = 'avoid_detain_button'
        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name, legal_ids=[suspect.user_id]
        )
        self.game_state = GameState.AVOID_DETAIN

    def do_detain_reaction(self, query=None, avoid_detain=False):
        ### DEBUG MODE
        if self.debug:
            print(f'Do avoid detain')
        ###
        if not hasattr(self.game, 'detain_event'):
            return
       
        if query is not None:
            if query.from_user.id not in self.msg_history['avoid_detain_button']['legal_ids']:
                return
            avoid_detain = int(query.data) > 0

        guard = self.game.players[self.game.detain_event['guard']]
        suspect = self.game.players[self.game.detain_event['suspect']]
        
        if avoid_detain:
            if suspect.can_avoid_detain():
                self.delete_message('avoid_detain_button')
                if suspect.is_hidden():
                    self.do_reveal(suspect.user_id)
                self.send_announce(
                    f'[動作] {suspect.character} {suspect.user_name} 避免了 守衛 {guard.user_name} 的關押',
                    name='turn')
                delattr(self.game, 'detain_event')
                self.end_turn()
            else:
                self.send_pop_up(f'[通知] 你不能避免關押', query=query)
        else:
            self.delete_message('avoid_detain_button')
            self.game.do_jail(suspect.user_id)
            self.send_announce(
                f'[動作] {guard.user_name} 關押了 {suspect.user_name}',
                name='turn')
            delattr(self.game, 'detain_event')
            self.end_turn()

    def ask_assassinate(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask assassinate')
        ###
        from_player = self.game.players[from_id]

        choices = self.game.can_be_assassinate_by(from_player.user_id)
        keyboard = self.generate_keyboard_player(choices, cancel=True)

        message = f"[詢問] {from_player.user_name} 你想要刺殺誰？"
        name = 'assassinate_button'
        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name, legal_ids=[from_id]
        )

    def do_assassinate(self, query=None, from_id=None, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do assassinate')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['assassinate_button']['legal_ids']:
                return
            self.delete_message('assassinate_button')
            if query.data == str(GameAction.CANCEL):
                self.ask_action()
                return
            else:
                target_id = int(query.data)

        player_1 = self.game.players[from_id]
        player_2 = self.game.players[target_id]

        if player_1.is_hidden():
            self.do_reveal(from_id)

        self.game.assassinate_event = {
            'assassin': from_id,
            'victim': target_id,
            'protectors': set(
                self.game.get_neighbors(from_id) + \
                self.game.get_neighbors(target_id)),
            'answered': [],
        }

        message = f'[動作] {player_1.user_name} 嘗試刺殺 {player_2.user_name}'
        self.send_announce(message, name='turn')

        self.ask_assassinate_reaction()
        for p in self.game.assassinate_event['protectors']:
            player = self.game.players[p]
            if player.is_ai():
                stop_assassinate = player.ai_stop_assassinate(self.game)
                self.do_assassinate_reaction(
                    protector_id=player.user_id,
                    stop_assassinate=stop_assassinate)

    def ask_assassinate_reaction(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask stop assassinate')
        ###
        assassin = self.game.players[self.game.assassinate_event['assassin']]
        victim = self.game.players[self.game.assassinate_event['victim']]
        protectors = [ self.game.players[i] \
            for i in self.game.assassinate_event['protectors']]

        keyboard = [[
            tg.InlineKeyboardButton(callback_data=1, text='要'),
            tg.InlineKeyboardButton(callback_data=-1, text='不要'),
        ]]

        protector_names = ', '.join([p.user_name for p in protectors])
        message = f"[詢問] {protector_names} 要公開自己的身份來阻止刺殺嗎？"
        name = 'stop_assassinate_button'
            
        self.game_state = GameState.STOP_ASSASSINATE
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name, legal_ids=self.game.assassinate_event['protectors']
        )

    def do_assassinate_reaction(self, query=None, stop_assassinate=False, protector_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do stop assassinate')
        ###
        if query is not None:
            protector_id = query.from_user.id
            stop_assassinate = int(query.data) > 0
        if not hasattr(self.game, 'assassinate_event'):
            return
        if protector_id not in self.game.assassinate_event['protectors'] \
        or protector_id in self.game.assassinate_event['answered']:
            return

        assassin = self.game.players[self.game.assassinate_event['assassin']]
        victim = self.game.players[self.game.assassinate_event['victim']]
        protector = self.game.players[protector_id]

        if stop_assassinate:
            if protector.can_stop_assassinate(self.game):
                if protector.is_hidden():
                    self.do_reveal(protector.user_id)
                self.delete_message('stop_assassinate_button')
                self.send_announce(
                    f'[動作] {protector.character} {protector.user_name} 阻止了刺殺',
                    name='turn')
                self.game.do_kill(assassin.user_id)
                self.send_announce(
                    f'[動作] {assassin.character} {assassin.user_name} 刺殺失敗 死亡',
                    name='turn')
                delattr(self.game, 'assassinate_event')
                self.end_turn()
            else:
                self.send_pop_up(f'[通知] 你不能阻止刺殺', query=query)
        else:
            self.game.assassinate_event['answered'].append(protector_id)
            if len(self.game.assassinate_event['answered']) \
            == len(self.game.assassinate_event['protectors']):
                self.delete_message('stop_assassinate_button')
                self.game.do_kill(victim.user_id)
                self.do_reveal(victim.user_id)
                self.send_announce(
                    f'[動作] {assassin.user_name} 刺殺了 {victim.user_name}',
                    name='turn')
                delattr(self.game, 'assassinate_event')
                self.end_turn()

    def do_call(self, from_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do dance')
        ###
        from_player = self.game.players[from_id]

        if from_player.is_hidden():
            self.do_reveal(from_id)

        self.send_announce(
            f'[動作] {from_player.user_name}: 我要革命！！！',
            name='turn')
        self.game.revolution_event = {
            'answered': [from_player.user_id],
        }
        self.ask_join(from_id)

    def ask_join(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask join')
        ###
        self.game_state = GameState.JOIN_REVOLUTION
        
        from_player = self.game.players[from_id]

        keyboard = [[
            tg.InlineKeyboardButton(callback_data=1, text='要'),
            tg.InlineKeyboardButton(callback_data=-1, text='不要')],[
        ]]
        message = f"[詢問] {from_player.user_name} 號召了革命 你要公開自己的身份來響應嗎？"
        name = 'join_button'
        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name
        )

        for i in self.game.player_orders:
            if i != from_player.user_id:
                target_player = self.game.players[i]
                if target_player.is_ai():
                    self.do_join(
                        join_revolution=target_player.ai_join(self.game), 
                        target_id=i) 
                elif target_player.is_known() and not target_player.is_slave():
                    self.do_join(
                        join_revolution=False, 
                        target_id=i)
                elif target_player.is_known() and not target_player.is_slave():
                    self.do_join(
                        join_revolution=False, 
                        target_id=i)         

    def do_join(self, query=None, join_revolution=False, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do join {self.game.revolution_event}')
            print(query, join_revolution, target_id)
        ###
        if query is not None:
            target_id = query.from_user.id
            join_revolution = int(query.data) > 0
        if target_id in self.game.revolution_event['answered']:
            return

        # joined_players = self.game.players[self.revolution_event['joined']]
        # target_pla = self.game.players[self.assassinate_event['victim']]
        target_player = self.game.players[target_id]

        if join_revolution:
            if target_player.can_join():
                if target_player.is_hidden():
                    self.do_reveal(target_id, verbose=False)
                self.game.revolution_event['answered'].append(target_id)
                self.send_announce(
                    f'[動作] {target_player.user_name}: 我要革命！！！',
                    name='turn')    
            elif query is not None:
                self.send_pop_up(f'[通知] 你不能響應', query=query)
        else:
            self.game.revolution_event['answered'].append(target_id)
            # self.send_announce(f'[動作] {target_player.user_name} 拒絕了革命請求')

        if len(self.game.revolution_event['answered']) == len(self.game.player_orders):
            self.delete_message('join_button')
            delattr(self.game, 'revolution_event')
            if self.game.check_win_condition(only_revolution=True):
                self.end_game()
            else:
                self.send_announce(f'[動作] 革命人數不足 失敗了',
                    name='turn')
                self.end_turn()

    def ask_capture(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask capture')
        ###

        from_player = self.game.players[from_id]

        choices = self.game.can_be_capture_by(from_player.user_id)
        keyboard = self.generate_keyboard_player(choices, cancel=True)

        message = f"[詢問] {from_player.user_name} 你想要抓捕誰？"
        name = 'capture_button'
        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name, legal_ids=[from_id]
        )

    def do_capture(self, query=None, from_id=None, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do capture')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['capture_button']['legal_ids']:
                return
            self.delete_message('capture_button')
            if query.data == str(GameAction.CANCEL):
                self.ask_action()
                return
            else:
                target_id = int(query.data)

        player_1 = self.game.players[from_id]
        player_2 = self.game.players[target_id]

        if player_1.is_hidden():
            self.do_reveal(from_id)

        if player_2.is_slave():
            self.game.do_capture(from_id, target_id)
            if player_2.is_known():
                message = f'[動作] {player_1.user_name} 抓捕了 公開奴隸 {player_2.user_name}'
                self.send_announce(message, name='turn')
                self.end_turn()
            else:
                message = f'[動作] {player_1.user_name} 抓捕了 隱藏奴隸 {player_2.user_name}，獲得額外回合'
                self.send_announce(message, name='turn')
                self.do_reveal(target_id)
                self.ask_action()
        else:
            message = f'[動作] {player_1.user_name} 抓捕失敗，{player_2.user_name} 不是奴隸'
            self.send_announce(message, name='turn')
            self.end_turn()

    def do_dance(self, from_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do dance')
        ###
        player_1 = self.game.players[from_id]
        if player_1.is_hidden():
            self.do_reveal(from_id)

        message = f'[動作] {player_1.user_name} 持續跳舞中'
        self.send_announce(message, name='turn')
        self.end_turn()

    def ask_support(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask support')
        ###
        from_player = self.game.players[from_id]

        keyboard = [[
            tg.InlineKeyboardButton(callback_data='loyal', text='保皇派'),
            tg.InlineKeyboardButton(callback_data='royal', text='革命軍')],[
        ], [
            tg.InlineKeyboardButton(
                callback_data=GameAction.CANCEL.value, text=str(GameAction.CANCEL))
        ]]

        self.send_buttons(
            f"[詢問] {from_player.user_name} 你想要支持哪一派？",
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='support_button', legal_ids=[from_id]
        )

    def do_support(self, query=None, from_id=None, support_team=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do support')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['support_button']['legal_ids']:
                return
            self.delete_message('support_button')
            if query.data == str(GameAction.CANCEL):
                self.ask_action()
                return
            else:
                support_team = query.data

        vizier = self.game.players[from_id]
        if vizier.is_hidden():
            self.do_reveal(from_id)

        self.game.manipulate_event = {
            'vizier': from_id,
            'support_team': support_team
        }
        team_str = '保皇派' if support_team == 'loyal' else '反叛軍'
        self.send_announce(
            f'[動作] 大官 {vizier.user_name} 公開支持 {team_str} 的獲勝',
            name='turn')
        
        if vizier.is_ai():
            _, target_id = vizier.ai_manipulate(self.game)
            self.do_manipulate(from_id=from_id, target_id=target_id)
        else:
            self.ask_manipulate(from_id=from_id)

    def ask_manipulate(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask manipulate')
        ###

        from_player = self.game.players[from_id]

        choices = self.game.can_be_manipulate_by(from_player.user_id)
        keyboard = self.generate_keyboard_player(choices, cancel=True)

        message = f"[詢問] {from_player.user_name} 你想要操弄誰？"        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='manipulate_button', legal_ids=[from_id]
        )

    def do_manipulate(self, query=None, from_id=None, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do manipulate')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['manipulate_button']['legal_ids']:
                return
            self.delete_message('manipulate_button')
            if query.data == str(GameAction.CANCEL):
                self.ask_manipulate(from_id)
                return
            else:
                target_id = int(query.data)

        player_1 = self.game.players[from_id]
        player_2 = self.game.players[target_id]

        self.game.manipulate_event['target'] = target_id

        message = f'[動作] {player_1.user_name} 操弄了 {player_2.user_name} 強制進行動作'
        self.send_announce(message, name='turn')
        self.do_reveal(target_id)
        player_2.exhaust = True
        self.ask_action(target_id, manipulate=True)

    def ask_predict_peek(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask predict peak')
        ###

        from_player = self.game.players[from_id]

        choices = self.game.can_be_peek_by(from_player.user_id, predict=True)
        keyboard = self.generate_keyboard_player(choices, cancel=True)

        if not hasattr(self.game, 'predict_event'):
            self.game.predict_event = {
                'peeked': [],
                'predict_team': None,
                'choices': choices
            }

        message = f"[詢問] {from_player.user_name} 做出預言前 想要先偷看誰的身份(選三個)？"        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='predict_peek_button', legal_ids=[from_id]
        )

    def do_predict_peek(self, query):
        ### DEBUG MODE
        if self.debug:
            print(f'Do predict peek')
        ###
        from_id = query.from_user.id
        if from_id not in self.msg_history['predict_peek_button']['legal_ids']:
            return
        if query.data == str(GameAction.CANCEL):
            self.ask_action()
            if hasattr(self.game, 'predict_event'):
                delattr(self.game, predict_event)
            return
        else:
            target_id = int(query.data)
    
        if target_id in self.game.predict_event['peeked']:
            self.game.predict_event['peeked'].remove(target_id)
        else:
            self.game.predict_event['peeked'].append(target_id)
        peeked_players_str = ', '.join([ 
            self.game.players[p].user_name for p in self.game.predict_event['peeked']] )
        self.send_announce(
            f'[詢問] 目前選到的角色有 {peeked_players_str}',
            name='predict')

        player_1 = self.game.players[from_id]
        target_ids = self.game.predict_event['peeked']

        if len(target_ids) == \
            min(3, self.game.predict_event['choices']):
            peek_message = ''
            for target_id in target_ids:
                player_2 = self.game.players[target_id]
                peek_message += f'[通知] {player_2.user_name} 目前的身份是 {player_2.character}'

                self.send_announce(
                    f'[動作] {player_1.user_name} 偷看了 {player_2.user_name} 的身份',
                    name='turn'
                )
            self.delete_message('predict_peek_button')
            self.send_pop_up(
                peek_message,
                query=query
            )
            player_1.memo = peek_message

            self.ask_predict(from_id=from_id)

    def ask_predict(self, from_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask predict')
        ###

        from_player = self.game.players[from_id]

        keyboard = [[
            tg.InlineKeyboardButton(callback_data='loyal', text='保皇派'),
            tg.InlineKeyboardButton(callback_data='royal', text='革命軍')],[
        ]]

        message = f"[詢問] {from_player.user_name} 你的預言是？"        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='predict_button', legal_ids=[from_id]
        )

    def do_predict(self, query=None, from_id=None, predict_team=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do predict')
        ###
        if query is not None:
            from_id = query.from_user.id
            if from_id not in self.msg_history['predict_button']['legal_ids']:
                return
            predict_team = query.data
        
        self.game.predict_event['predict_team'] = predict_team

        player_1 = self.game.players[from_id]
        player_1.must_switch = True

        team_str = '保皇派' if predict_team == 'loyal' else '反叛軍'
        self.send_announce(
            f'[動作] {player_1.user_name} 預言了 {team_str} 的獲勝',
            name='turn'
        )
        self.end_turn()

    def is_admin(self, user_id):
        return user_id == self.admin_id

    """Utility functions
    """
    def generate_keyboard_player(self, player_choices, max_len=2, cancel=True):
        keyboard = [[], []]
        i = 0
        for target_id in player_choices:
            keyboard[i].append(tg.InlineKeyboardButton(
                callback_data=target_id, 
                text=str(self.game.players[target_id].status())))
            if len(keyboard[i]) >= max_len:
                keyboard.append([])
                i += 1
        if cancel:
            keyboard.append([])
            keyboard[-1].append(tg.InlineKeyboardButton(
                callback_data=str(GameAction.CANCEL), text=str(GameAction.CANCEL)))
            keyboard[-1].append(tg.InlineKeyboardButton(
                callback_data=str(GameAction.GIVEUP), text=str(GameAction.GIVEUP)))
        return keyboard

    def generate_keyboard_action(self, action_choices, max_len=2):
        keyboard = [[]]
        i = 0
        for action in action_choices:
            if len(keyboard[i]) >= max_len:
                keyboard.append([])
                i += 1
            keyboard[i].append(tg.InlineKeyboardButton(
                callback_data=action.value, 
                text=str(action)))
        return keyboard

