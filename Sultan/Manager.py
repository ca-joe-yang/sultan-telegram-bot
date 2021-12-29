from .Action import GameAction
from .State import State as GameState
from .Game import SultanGame

import numpy as np
import telegram as tg
import time

GAME_COUNT = 0

class SultanManager:

    def __init__(self, bot, chat_id, debug=True):
        ### DEBUG MODE
        self.debug = debug
        ###

        self.game_state = GameState.NO_GAME
        self.bot = bot
        self.chat_id = chat_id

        with open('README.md', 'r') as f:
            self.tutorial_str  = f.read()

        global GAME_COUNT
        GAME_COUNT += 1
        self.game_id = GAME_COUNT

        self.send_announce(f'[公告] {self.game_id} 號房已建立')

    def new_game(self, user_id, user_name=None, debug=True):
        self.game = SultanGame(debug=debug)

        self.game_state = GameState.IDLE
        self.admin_id = user_id
        self.admin_name = user_name
        self.msg_history = {}

        self.send_announce(f'[公告] 新遊戲開始 目前主持人為 {user_name}') 

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
            message=f"[公告] {self.admin_name} 想要玩 推翻蘇丹，你要加入嗎？",
            markup=tg.InlineKeyboardMarkup(keyboard),
            name='register_button'
        )
        self.send_announce(
            message=f"[公告] 目前報名有：{self.game.print_players_list()}",
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
        
        if data == 'join':
            ### DEBUG MODE
            if self.debug:
                print(f'Join {user_name} {user_id}')
            ###
            if user_id in self.game.players:
                message = f'[通知] 你已經加入遊戲了'
            else:
                self.game.add_player(user_id, user_name)
                message = f'[通知] 成功加入遊戲'
                self.edit_announce(
                    message=f"[公告] 目前報名有：{self.game.print_players_list()}",
                    name='register_players'
                )
            self.send_pop_up(message, query)
        elif data == 'exit':
            ### DEBUG MODE
            if self.debug:
                print(f'Exit {user_name} {user_id}')
            ###
            if user_id in self.game.players:
                self.game.remove_player(user_id, user_name)
                message = f'[通知] 成功退出遊戲'
                self.edit_announce(
                    message=f"[公告] 目前報名有：{self.game.print_players_list()}",
                    name='register_players'
                )
            else:
                message = f'[通知] 你不在遊戲中'
            self.send_pop_up(message, query)
        elif data == 'add_ai' and self.is_admin(user_id):
            ### DEBUG MODE
            if self.debug:
                print(f'Add ai')
            ###
            while len(self.game.players) < 5:
                # print(self.game.players)
                self.game.add_player(ai=True)
            self.edit_announce(
                message=f"[公告] 目前報名有：{self.game.print_players_list()}",
                name='register_players'
            )
        elif data == 'remove_ai' and self.is_admin(user_id):
            ### DEBUG MODE
            if self.debug:
                print(f'Remove ai')
            ###
            self.game.remove_player(ai=True)
            self.edit_announce(
                message=f"[公告] 目前報名有：{self.game.print_players_list()}",
                name='register_players'
            )
        elif data == 'start' and self.is_admin(user_id):
            ### DEBUG MODE
            if self.debug:
                print(f'Start')
            ###
            self.start_game()
            self.start_turn()

    def send_announce(self, message, name=None):
        ### DEBUG MODE
        if self.debug:
            print(f'[Announce] {name}: {message}')
        ###
        msg = self.bot.send_message(self.chat_id, message)
        if name is not None:
            self.msg_history[name] = msg.message_id

    def edit_announce(self, message, name):
        ### DEBUG MODE
        if self.debug:
            print(f'[Edit] {name}: {message}')
        ###
        self.bot.edit_message_text(
            message,
            self.chat_id, self.msg_history[name]
        )

    def send_pop_up(self, message, query):
        ### DEBUG MODE
        if self.debug:
            print(f'[Popup] {message}')
        ###
        query.answer(text=message, show_alert=True)

    def send_private(self, message, user_id):
        ### DEBUG MODE
        if self.debug:
            print(f'[private] {user_id}: {message}')
        ###
        self.bot.send_message(user_id, message)

    def send_buttons(self, message, markup, name=None):
        ### DEBUG MODE
        if self.debug:
            print(f'[Button] {message}')
        ###
        if name in self.msg_history:
            try:
                self.delete_message(name)
            except:
                pass
        
        msg = self.bot.send_message(self.chat_id,
            reply_markup=markup,
            text=message)
            
        if name is not None:
            self.msg_history[name] = msg.message_id

    def delete_message(self, name):
        if name in self.msg_history:
            ### DEBUG MODE
            if self.debug:
                print(f'Delete {name}: {self.msg_history[name]}')
            ###
            try:
                self.bot.delete_message(self.chat_id, self.msg_history[name])
            except:
                print(f'Message {name} not found')
                print(self.msg_history)
            del self.msg_history[name]

    def start_game(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Start game')
        ###
        self.delete_message('register_button')
        self.send_announce(f'[公告] 遊戲開始')
        self.game.start_game()
        self.ask_general()

    def end_game(self):
        ### DEBUG MODE
        if self.debug:
            print(f'End game')
        ###
        if self.game.winner == 'loyal':
            self.send_announce(
                f'[公告] {self.game.win_condition} 保皇黨 勝利！')
        elif self.game.winner == 'rebel':
            self.send_announce(
                f'[公告] {self.game.win_condition} 反叛軍 勝利！')
        else:
            raise
        self.send_announce(f'[公告] 遊戲結束')
        self.game_state = GameState.IDLE

    def start_turn(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Start turn')
        ###
        self.game_state = GameState.TURN_START
        cur_player = self.game.current_player()

        if cur_player.throne_countdown is not None:
            cur_player.throne_countdown -= 1
        
        if self.game.check_win_condition():
            self.end_game()
            return

        if cur_player.is_jail():
            self.send_announce(
                message=f'[公告] {cur_player.user_name} 出獄'
            )
            cur_player.jail = False
            self.end_turn()
            return
        # user_id = game.current_player().user_id
        # user_name = game.players[user_id].user_name
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

        self.game.next_player()
        self.start_turn()

    def ask_general(self):
        keyboard = [[], []]

        keyboard[0].append(tg.InlineKeyboardButton(
            callback_data=GameAction.CHECK.value, text=str(GameAction.CHECK)))        
        keyboard[0].append(tg.InlineKeyboardButton(
            callback_data=GameAction.TUTORIAL.value, text=str(GameAction.TUTORIAL)))
        keyboard[1].append(tg.InlineKeyboardButton(
            callback_data=GameAction.SKIP.value, text=str(GameAction.SKIP)))

        self.send_buttons(
            message='[通用]',
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

        if action == GameAction.SKIP and self.is_admin(user_id):
            self.send_announce(f'[動作] {self.game.current_player().user_name} 回合被跳過了')
            self.end_turn()

        elif action == GameAction.CHECK:
            info = self.game.get_player_information(user_id)
            message = '\n'.join(info)
            self.send_pop_up(f'[查看]\n{message}', query)

        elif action == GameAction.TUTORIAL:
            self.send_tutorial(user_id)

    def send_tutorial(self, user_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Send tutorial')
        ###
        self.send_private(self.tutorial_str, user_id)

    def ask_action(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask action')
        ###
        self.game_state = GameState.TURN_START

        cur_player = self.game.current_player()

        if cur_player.is_ai():
            action, target_id = cur_player.ai_action(self.game)
            self.do_action(action=action, target_id=target_id)
        else:
            action_choices = self.game.legal_actions()

            keyboard = self.generate_keyboard_action(
                action_choices, max_len=2)
            self.send_buttons(
                message=f"[動作] 輪到 {cur_player.user_name}，想要採取甚麼行動？",
                markup=tg.InlineKeyboardMarkup(keyboard),
                name='action_button'
            )

    def do_action(self, query=None, action=None, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do action')
        ###
        cur_player = self.game.current_player()
        
        if query is not None:
            if query.from_user.id != cur_player.user_id:
                return
            else:
                action = GameAction(int(query.data))
                ### DEBUG MODE
                if self.debug:
                    print(f'{query.data} {action}')
                ###

        self.game_state = GameState.TURN_MID
        self.delete_message('action_button')

        if action == GameAction.REVEAL:
            self.do_reveal(cur_player.user_id)
            self.ask_action()

        elif action == GameAction.PEEK:
            self.ask_peek(target_id=target_id)
        
        elif action == GameAction.SWITCH:
            self.ask_switch(target_id=target_id, hide=False)
        
        elif action == GameAction.HIDE:
            self.ask_switch(target_id=target_id, hide=True)
        
        elif action == GameAction.EXECUTE:
            self.ask_execute(target_id=target_id)

        elif action == GameAction.DETAIN:
            self.ask_detain(target_id=target_id)

        elif action == GameAction.ASSASSINATE:
            self.ask_assassinate(target_id=target_id)

        elif action == GameAction.CALL:
            self.ask_join()

    def do_reveal(self, player_id):
        ### DEBUG MODE
        if self.debug:
            print(f'Do reveal')
        ###
        player = self.game.players[player_id]
        if player.is_hidden():
            player.hidden = False
            self.send_announce(
                f'[動作] 玩家 {player.user_name} 公開了他的身份為 {player.character}')
            if player.is_sultan():
                self.game.sultan_id = player_id
                self.game.current_player().throne_countdown = 1
                self.send_announce(
                    f'[公告] 登基程序開始 到下一次 {self.game.current_player().user_name} 的回合')
        

    def ask_peek(self, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask peek')
        ###
        cur_player = self.game.current_player()

        if cur_player.is_ai():
            self.do_peek(
                player_1_id=cur_player.user_id, 
                player_2_id=target_id)  
        else:
            choices = self.game.can_be_peek_by(cur_player.user_id)
            keyboard = self.generate_keyboard_player(choices, cancel=True)

            self.send_buttons(
                f"[動作] {cur_player.user_name} 想要偷看誰的身份？",
                markup=tg.InlineKeyboardMarkup(keyboard),
                name='peek_button'
            )

    def do_peek(self, query=None, player_1_id=None, player_2_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do peek')
        ###
        if query is not None:
            self.delete_message('peek_button')
            if GameAction(int(query.data)) == GameAction.CANCEL:
                self.ask_action()
                return
            else:
                player_2_id = int(query.data)
            player_1_id = query.from_user.id

        player_1 = self.game.players[player_1_id]
        player_2 = self.game.players[player_2_id]

        if query is not None:
            peek_message = f'[偷看] 玩家 {player_2.user_name} 目前的身份是 {player_2.character}'
            self.send_pop_up(
                peek_message,
                query=query
            )
            # player_1.memo = peek_message
        self.send_announce(
            f'[動作] 玩家 {player_1.user_name} 偷看了 玩家 {player_2.user_name} 的身份'
        )
        self.end_turn()

    def ask_switch(self, target_id=None, hide=False):
        ### DEBUG MODE
        if self.debug:
            if hide:
                print(f'Ask hide')
            else:
                print(f'Ask switch')
        ###
        cur_player = self.game.current_player()

        if cur_player.is_ai():
            self.do_switch(
                player_1_id=cur_player.user_id, 
                player_2_id=target_id,
                hide=hide)
        else:
            choices = self.game.can_be_switch_by(cur_player.user_id, hide=hide)
            keyboard = self.generate_keyboard_player(choices, cancel=True)

            if hide:
                message = f"[動作] {cur_player.user_name} 隱藏身份前 想要偷偷和誰的身份交換？"
                name = 'hide_button'
            else:
                message = f"[動作] {cur_player.user_name} 想要和誰的身份交換？"
                name = 'switch_button'
            
            self.send_buttons(
                message,
                markup=tg.InlineKeyboardMarkup(keyboard),
                name=name
            )

    def do_switch(self, query=None, player_1_id=None, player_2_id=None, hide=False):
        ### DEBUG MODE
        if self.debug:
            if hide:
                print(f'Do hide')
            else:
                print(f'Do switch')
        ###
        if query is not None:
            if hide:
                self.delete_message('hide_button')
            else:
                self.delete_message('switch_button')
            if GameAction(int(query.data)) == GameAction.CANCEL:
                self.ask_action()
                return
            else:
                player_2_id = int(query.data)
            player_1_id = query.from_user.id

        player_1 = self.game.players[player_1_id]
        player_2 = self.game.players[player_2_id]
    
        if hide:
            self.game.do_hide(player_1_id)
            message = f'[動作] {player_1.user_name} 隱藏了身份 並偷偷和某人交換了身份'
        else:
            message = f'[動作] {player_1.user_name} 和 {player_2.user_name} 交換了身份'

        self.game.do_switch(player_1_id, player_2_id)

        self.send_announce(message)
        self.end_turn()

    def ask_execute(self, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask execute')
        ###
        cur_player = self.game.current_player()

        if cur_player.is_ai():
            self.do_execute(
                player_1_id=cur_player.user_id, 
                player_2_id=target_id)
        else:
            choices = self.game.can_be_execute_by(cur_player.user_id)
            keyboard = self.generate_keyboard_player(choices, cancel=True)

            message = f"[動作] {cur_player.user_name} 你想要處決誰？"
            name = 'execute_button'
            
            self.send_buttons(
                message,
                markup=tg.InlineKeyboardMarkup(keyboard),
                name=name
            )

    def do_execute(self, query=None, player_1_id=None, player_2_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do execute')
        ###
        if query is not None:
            self.delete_message('execute_button')
            if GameAction(int(query.data)) == GameAction.CANCEL:
                self.ask_action()
                return
            else:
                player_2_id = int(query.data)
            player_1_id = query.from_user.id

        player_1 = self.game.players[player_1_id]
        player_2 = self.game.players[player_2_id]
    
        self.game.do_kill(player_2_id)
        
        message = f'[動作] {player_1.user_name} 處決了 {player_2.user_name}'

        self.send_announce(message)
        self.end_turn()

    def ask_detain(self, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Send detain')
        ###
        cur_player = self.game.current_player()

        if cur_player.is_ai():
            self.do_detain_start(
                player_1_id=cur_player.user_id, 
                player_2_id=target_id)
        else:
            choices = self.game.can_be_detain_by(cur_player.user_id)
            keyboard = self.generate_keyboard_player(choices, cancel=True)

            message = f"[動作] {cur_player.user_name} 你想要關押誰？"
            name = 'detain_button'
            
            self.send_buttons(
                message,
                markup=tg.InlineKeyboardMarkup(keyboard),
                name=name
            )

    def do_detain_start(self, query=None, player_1_id=None, player_2_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do detain')
        ###
        if query is not None:
            self.delete_message('detain_button')
            if GameAction(int(query.data)) == GameAction.CANCEL:
                self.ask_action()
                return
            else:
                player_2_id = int(query.data)
            player_1_id = query.from_user.id

        player_1 = self.game.players[player_1_id]
        player_2 = self.game.players[player_2_id]

        self.detain_event = {
            'guard': player_1_id,
            'suspect': player_2_id
        }

        message = f'[動作] {player_1.user_name} 嘗試關押 {player_2.user_name}'
        self.send_announce(message)

        self.ask_avoid_detain()

    def ask_avoid_detain(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Send avoid detain')
        ###
        guard = self.game.players[self.detain_event['guard']]
        suspect = self.game.players[self.detain_event['suspect']]

        if suspect.is_ai():
            avoid_detain = suspect.ai_avoid_detain()
            self.game_state = GameState.AVOID_DETAIN
            self.do_detain_end(avoid_detain=avoid_detain)
        else:
            keyboard = [[
                tg.InlineKeyboardButton(callback_data=1, text='要'),
                tg.InlineKeyboardButton(callback_data=-1, text='不要'),
            ]]

            message = f"[動作] {suspect.user_name} 你要公開自己的身份來避免關押嗎？"
            name = 'avoid_detain_button'
            
            self.send_buttons(
                message,
                markup=tg.InlineKeyboardMarkup(keyboard),
                name=name
            )
            self.game_state = GameState.AVOID_DETAIN

    def do_detain_end(self, query=None, avoid_detain=False):
        ### DEBUG MODE
        if self.debug:
            print(f'Do avoid detain')
        ###
        guard = self.game.players[self.detain_event['guard']]
        suspect = self.game.players[self.detain_event['suspect']]
        
        if query is not None:
            if query.from_user.id != suspect.user_id:
                return
            avoid_detain = int(query.data) > 0

        if avoid_detain:
            if suspect.can_avoid_detain():
                self.delete_message('avoid_detain_button')
                if suspect.is_hidden():
                    self.do_reveal(suspect.user_id)
                self.send_announce(
                    f'[動作] {suspect.character} {suspect.user_name} 避免了 守衛 {guard.user_name} 的關押')
                self.detain_event.clear()
                self.end_turn()
            else:
                self.send_pop_up(f'[違法] 你不是保皇派 不能避免關押', query=query)
        else:
            self.delete_message('avoid_detain_button')
            self.game.do_prison(suspect.user_id)
            self.send_announce(
                f'[動作] {guard.user_name} 關押了 {suspect.user_name}')
            self.detain_event.clear()
            self.end_turn()

    def ask_assassinate(self, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask assassinate')
        ###
        cur_player = self.game.current_player()

        if cur_player.is_ai():
            self.do_assassinate_start(
                player_1_id=cur_player.user_id, 
                player_2_id=target_id)
        else:
            choices = self.game.can_be_assassinate_by(cur_player.user_id)
            keyboard = self.generate_keyboard_player(choices, cancel=True)

            message = f"[動作] {cur_player.user_name} 你想要刺殺誰？"
            name = 'assassinate_button'
            
            self.send_buttons(
                message,
                markup=tg.InlineKeyboardMarkup(keyboard),
                name=name
            )

    def do_assassinate_start(self, query=None, player_1_id=None, player_2_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do assassinate')
        ###
        if query is not None:
            self.delete_message('assassinate_button')
            if GameAction(int(query.data)) == GameAction.CANCEL:
                self.ask_action()
                return
            else:
                player_2_id = int(query.data)
            player_1_id = query.from_user.id

        player_1 = self.game.players[player_1_id]
        player_2 = self.game.players[player_2_id]

        self.assassinate_event = {
            'assassin': player_1_id,
            'victim': player_2_id,
            'protectors': set(
                self.game.get_neighbors(player_1_id) + \
                self.game.get_neighbors(player_2_id)),
            'answered': [],
        }
        if player_1_id in self.assassinate_event['protectors']:
            self.assassinate_event['protectors'].remove(player_1_id)
        if player_2_id in self.assassinate_event['protectors']:
            self.assassinate_event['protectors'].remove(player_2_id)

        message = f'[動作] {player_1.user_name} 嘗試刺殺 {player_2.user_name}'
        self.send_announce(message)
        self.ask_stop_assassinate()

    def ask_stop_assassinate(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask stop assassinate')
        ###
        assassin = self.game.players[self.assassinate_event['assassin']]
        victim = self.game.players[self.assassinate_event['victim']]
        protectors = [ self.game.players[i] \
            for i in self.assassinate_event['protectors']]

        keyboard = [[
            tg.InlineKeyboardButton(callback_data=1, text='要'),
            tg.InlineKeyboardButton(callback_data=-1, text='不要'),
        ]]

        protector_names = ', '.join([p.user_name for p in protectors])
        message = f"[動作] {protector_names} 要公開自己的身份來阻止刺殺嗎？"
        name = 'stop_assassinate_button'
            
        self.game_state = GameState.STOP_ASSASSINATE
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name
        )

        for p in protectors:
            if p.is_ai():
                stop_assassinate = p.ai_stop_assassinate()
                self.do_assassinate_end(
                    protector_id=p.user_id,
                    stop_assassinate=stop_assassinate)

    def do_assassinate_end(self, query=None, stop_assassinate=False, protector_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do stop assassinate')
        ###
        if query is not None:
            protector_id = query.from_user.id
            stop_assassinate = int(query.data) > 0
        if protector_id not in self.assassinate_event['protectors'] \
        or protector_id in self.assassinate_event['answered']:
            return

        assassin = self.game.players[self.assassinate_event['assassin']]
        victim = self.game.players[self.assassinate_event['victim']]
        protector = self.game.players[protector_id]

        if stop_assassinate:
            if protector.can_stop_assassinate():
                if protector.is_hidden():
                    self.do_reveal(protector.user_id)
                self.delete_message('stop_assassinate_button')
                self.send_announce(
                    f'[動作] {protector.character} {protector.user_name} 阻止了刺殺')
                self.game.do_kill(assassin.user_id)
                self.send_announce(
                    f'[動作] {assassin.character} {assassin.user_name} 刺殺失敗 死亡')
                self.assassinate_event.clear()
                self.end_turn()
            else:
                self.send_pop_up(f'[違法] 你不是守衛 不能阻止刺殺', query=query)
        else:
            self.assassinate_event['answered'].append(protector_id)
            if len(self.assassinate_event['answered']) == len(self.assassinate_event['protectors']):
                self.delete_message('stop_assassinate_button')
                self.game.do_kill(victim.user_id)
                self.do_reveal(victim.user_id)
                self.send_announce(
                    f'[動作] {assassin.user_name} 刺殺了 {victim.user_name}')
                self.assassinate_event.clear()
                self.end_turn()

    def ask_join(self):
        ### DEBUG MODE
        if self.debug:
            print(f'Ask join')
        ###
        self.game_state = GameState.JOIN_REVOLUTION
        
        cur_player = self.game.current_player()

        self.revolution_event = {
            'answered': [cur_player.user_id],
        }

        self.send_announce(f'[動作] {cur_player.user_name}: 我要革命！！！')

        keyboard = [[
            tg.InlineKeyboardButton(callback_data=1, text='要'),
            tg.InlineKeyboardButton(callback_data=-1, text='不要')],[
        ]]
        message = f"[動作] {cur_player.user_name} 號召了革命 你要公開自己的身份來響應嗎？"
        name = 'join_button'
        
        self.send_buttons(
            message,
            markup=tg.InlineKeyboardMarkup(keyboard),
            name=name
        )

        for i in self.game.player_orders:
            if i != cur_player.user_id:
                target_player = self.game.players[i]
                # print(i, target_player.user_id)
                if target_player.is_ai():
                    # print(i, target_player.user_id, target_player.ai_join(self.game))
                    self.do_join(
                        join_revolution=target_player.ai_join(self.game), 
                        target_id=i)        

    def do_join(self, query=None, join_revolution=False, target_id=None):
        ### DEBUG MODE
        if self.debug:
            print(f'Do join {self.revolution_event}')
            print(query, join_revolution, target_id)
        ###
        if query is not None:
            target_id = query.from_user.id
            join_revolution = int(query.data) > 0
        if target_id in self.revolution_event['answered']:
            return

        # joined_players = self.game.players[self.revolution_event['joined']]
        # target_pla = self.game.players[self.assassinate_event['victim']]
        target_player = self.game.players[target_id]

        if join_revolution:
            if target_player.can_join():
                if target_player.is_hidden():
                    self.do_reveal(target_id)
                self.revolution_event['answered'].append(target_id)
                self.send_announce(
                    f'[動作] {target_player.user_name}: 我要革命！！！')    
            elif query is not None:
                self.send_pop_up(f'[違法] 你不能響應', query=query)
        else:
            self.revolution_event['answered'].append(target_id)
            self.send_announce(f'[動作] {target_player.user_name} 拒絕了革命請求')

        if len(self.revolution_event['answered']) == len(self.game.player_orders):
            self.delete_message('join_button')
            self.revolution_event.clear()
            if self.game.check_win_condition(only_revolution=True):
                self.end_game()
            else:
                self.send_announce(f'[動作] 革命人數不足 失敗了')
                self.end_turn()

    def is_admin(self, user_id):
        return user_id == self.admin_id

    """Utility functions
    """
    def generate_keyboard_player(self, player_choices, max_len=2, cancel=True):
        keyboard = [[]]
        i = 0
        if cancel:
            keyboard[i].append(tg.InlineKeyboardButton(
                callback_data=GameAction.CANCEL.value, text=str(GameAction.CANCEL)))
        for target_id in player_choices:
            if len(keyboard[i]) >= max_len:
                keyboard.append([])
                i += 1
            keyboard[i].append(tg.InlineKeyboardButton(
                callback_data=target_id, 
                text=str(self.game.players[target_id].status())))
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

