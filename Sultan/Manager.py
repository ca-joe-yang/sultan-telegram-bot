import numpy as np
from .Action import BotAction
from .State import State
from .Game import SultanGame

class SultanManager:

    def __init__(self, bot, chat_id, user_id, user_name=None):
        self.bot = bot
        self.chat_id = chat_id
        self.game = SultanGame(chat_id=chat_id, 
            admin_id=user_id, admin_name=user_name)

        self.send_announce(f'[公告] {-chat_id}號房已建立 目前主持人為{user_name}')


        keyboard = [[
            tg.InlineKeyboardButton(
                callback_data='join', text='加入'),
            tg.InlineKeyboardButton(
                callback_data='exit', text='退出')],[
            tg.InlineKeyboardButton(
                callback_data='add_ai', text='[admin] 增加AI'),
            tg.InlineKeyboardButton(
                callback_data='remove_ai', text='[admin] 減少AI'),
            tg.InlineKeyboardButton(
                callback_data='start', text='[admin] 開始遊戲'),
        ]]
        self.send_buttons()
            msg = self.bot.send_message(chat_id,
                reply_markup=tg.InlineKeyboardMarkup(keyboard),
                text=f"[公告] {game.admin_name}想要玩推翻蘇丹，你要加入嗎？")
            game.msg_id['register_button'] = msg.message_id
            
            msg = self.bot.send_message(chat_id,
                text=f"[公告] 目前報名有：{game.print_players_list()}")
            game.msg_id['register_players'] = msg.message_id
            
            game.set_state(GameState.REGISTER)

    def send_announce(self, message):
        self.bot.send_message(self.chat_id, message)

    def send_pop_up(self, message, query):
        pass

    def send_buttons(self, message, markup, name):
        msg = self.bot.send_message(self.chat_id,
            reply_markup=markup,
            text=message)
            
        self.msg_id['register_button'] = msg.message_id

    def switch_character(self, game, player_id_1, player_id_2, hide=False):
        player_1 = game.players[player_id_1]
        player_2 = game.players[player_id_2]
        
        if (player_id_2, player_id_1) == game.last_swicth_pair:
            return False, [{
                'type': BotAction.ANNOUNCE,
                'message': f'[違法] 玩家 {player_1.user_name} 和 玩家 {player_2.user_name} 才剛交換過'
            }]
        elif not hide and player_2.is_not_hidden():
            return False, [{
                'type': BotAction.PRIVATE,
                'message': f'[違法] 玩家 {player_2.user_name} 的身份非隱藏 不能交換'
            }]
        
        game.switch_character(player_id_1, player_id_2)

        if hide:
            player_1.hidden = True
            return True, [{
                'type': BotAction.ANNOUNCE,
                'message': f'[動作] 玩家 {player_1.user_name} 隱藏起來 並偷偷和某人交換了身份'
            }]
        
        if player_2.is_spare():
            return True, [{
                'type': BotAction.ANNOUNCE,
                'message': f'[動作] 玩家 {player_1.user_name} 和 白板 交換了身份'
            }]
        else:
            return True, [{
                'type': BotAction.ANNOUNCE,
                'message': f'[動作] 玩家 {player_1.user_name} 和 玩家 {player_2.user_name} 交換了身份'
            }]

    def peek_character(self, game, player_id_1, player_id_2):
        player_1 = game.players[player_id_1]
        player_2 = game.players[player_id_2]
        if player_2.is_not_hidden():
            return False, [{
                'type': BotAction.ANNOUNCE,
                'message': f'[違法] 玩家 {player_2.user_name} 的身份非隱藏'
            }]

        return True, [{
            'type': BotAction.PRIVATE,
            'user_id': player_1.user_id,
            'message': f'[偷看] 玩家 {player_2.user_name} 目前的身份是 {player_2.character}'
        },{
            'type': BotAction.ANNOUNCE,
            'message': f'[動作] 玩家 {player_1.user_name} 偷看了 玩家 {player_2.user_name} 的身份'
        }]

    def check_character(self, game, user_id):
        count = 0
        message = []
        for target_id in game.player_order:
            if target_id != 0:
                count += 1
            message.append(f'{count}: {game.players[target_id].status(verbose=user_id == target_id)}')
        message = '\n'.join(message)
        return True, [{
            'type': BotAction.PRIVATE,
            'user_id': user_id,
            'message': f'[查看]\n{message}'
        }]

    def reveal_character(self, game, player_id):
        player = game.players[player_id]
        player.hidden = False
        if player.is_sultan():
            game.sultan = player_id
            game.crown_token = player_id
        return True, [{
            'type': BotAction.ANNOUNCE,
            'message': f'[動作] 玩家 {player.user_name} 公開了他的身份為 {player.character}'
        }]

    def execute(self, game, user_id, target_id):
        sultan_name = game.players[user_id].user_name
        target_player = game.players[target_id]
        target_player.alive = False
        game.dead_player(target_id)
        return True, [{
            'type': BotAction.ANNOUNCE,
            'message': f'[動作] 蘇丹 {sultan_name} 處決了 {target_player.user_name}'
        }]

    def detain(self, game):
        guard_id = game.detain_event['guard']
        guard = game.players[guard_id]

        suspect_id = game.detain_event['suspect']
        suspect = game.players[suspect_id]
        suspect.jail = True
        return True, [{
            'type': BotAction.ANNOUNCE,
            'message': f'[動作] 守衛 {guard.user_name} 關押了 {suspect.user_name}'
        }]

    def avoid_detain(self, game):
        guard_id = game.detain_event['guard']
        guard = game.players[guard_id]

        suspect_id = game.detain_event['suspect']
        suspect = game.players[suspect_id]

        if target_player.can_avoid_detain():
            target_player.hidden = False
            if target_player.is_sultan():
                game.sultan = target_player.user_id
                game.crown_token = guard_id
            message = f'[動作] 玩家 {suspect.user_name} ' + \
                f'出示了身份 {suspect.character}，避免了 守衛 {guard.user_name} 的關押'
            return True, [{
                'type': BotAction.ANNOUNCE,
                'message': message
            }]
        else:
            return False, [{
                'type': BotAction.PRIVATE,
                'message': f'[違法] 你不是保皇派 不能避免關押'
            }]

    def assassinate(self, game):
        if len(game.assassinate_event['protector']) == 0:
            killer_id = game.assassinate_event['killer']
            killer = game.players[killer_id]

            victim_id = game.assassinate_event['victim']
            victim = game.players[victim_id]
            victim.alive = False
            if victim.is_sultan():
                game.winner = 'rebel'
            return True, [{
                'type': BotAction.ANNOUNCE,
                'message': f'[動作] 刺客 {killer.user_name} 刺殺了 {victim.user_name}'
            }]
        else:
            return False, [{
                'type': BotAction.IDLE,
            }]

    def stop_assassinate(self, game, user_id):
        killer_id = game.assassinate_event['killer']
        killer = game.players[killer_id]

        victim_id = game.assassinate_event['victim']
        victim = game.players[victim_id]

        protector = game.players[user_id]

        if protector.can_stop_assassinate():
            protector.hidden = False
            killer.alive = False
            game.dead_player(victim_id)
            message = f'[動作] 玩家 {protector.user_name} ' + \
                f'出示了身份 {protector.character}，阻止了 刺客 {killer.user_name} 刺殺 {victim.user_name}'
            return True, [{
                'type': BotAction.ANNOUNCE,
                'message': message
            }]
        else:
            return False, [{
                'type': BotAction.PRIVATE,
                'message': f'[違法] 你不是守衛 不能阻止刺殺'
            }]

    def join(self, game, user_id):
        joiner = game.players[user_id]

        if joiner.can_join():
            joiner.hidden = False
            # game.dead_player(victim_id)

            game.revolution_event['joined'].add(user_id)

            ret_ids = set()
            for user_id in game.revolution_event['joined']:
                ret_ids.update(game.neighbor(user_id))
            for user_id in game.revolution_event['joined']:
                ret_ids.remove(user_id)
            game.revolution_event['called'] = ret_ids

            message = f'[動作] 奴隸 {joiner.user_name}: 我要革命！！！'
            return False, [{
                'type': BotAction.ANNOUNCE,
                'message': message
            }]
        else:
            return False, [{
                'type': BotAction.PRIVATE,
                'message': f'[違法] 你不是奴隸 不能響應'
            }]

    def check_revolution(self):
        if len(game.revolution_event['joined']) >= 3:
            game.winner = 'rebel'
            return True, [{
                'type': BotAction.ANNOUNCE,
                'message': f'[動作] 奴隸 革命成功！'
            }]
        elif len(game.revolution_event['called']) == 0:
            return True, [{
                'type': BotAction.ANNOUNCE,
                'message': f'[動作] 奴隸 革命失敗！'
            }]
        else:
            return False, [{
                'type': BotAction.IDLE,
            }]




class SultanAI:

    def __init__(self, character):
        self.character = character

    def action(self):
        pass


