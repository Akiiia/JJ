
from douzero.env import move_detector as md
from douzero.env import move_selector as ms
from douzero.env.move_generator import MovesGener
from collections import Counter
import random
from douzero.evaluation.deep_agent2 import DeepAgent
import json

RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                    '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12,
                    'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30}

EnvCard2RealCard = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                    8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q',
                    13: 'K', 14: 'A', 17: '2', 20: 'X', 30: 'D'}

class InfoSet(object):

    def __init__(self,player_position):
        self.player_position = player_position  #OK
        self.player_hand_cards = None #OK
        self.num_cards_left_dict = None #OK
        self.three_landlord_cards = None #OK
        self.card_play_action_seq = None #OK
        self.other_hand_cards = None
        self.legal_actions = None
        self.last_move = None
        self.last_two_moves = None
        self.last_move_dict = None
        self.played_cards = None
        self.all_handcards = None
        self.last_pid = None #OK
        self.bomb_num = 0 #OK
        self.init_card = None #OK


        #self.player_hand_cards #AI首牌
        #self.num_cards_left_dict = {'landlord': [],'landlord_up': [],'landlord_down': []} 三个手里的牌
        #three_landlord_cards #三张底牌
        #self.all_action = [] 所有的出牌记录
        #self.other_hand_cards = [] #除了我其它俩家的总剩牌(可乱序)如："D22TT99998777666555444433"
        #self.legal_actions #可以出的牌
        #self.last_move = [] #最后一个出牌记录
        #self.last_two_moves = [] #最后两个出牌记录
        #self.last_move_dict = [] #三个玩家的最后出牌记录
        #self.played_cards = {'landlord': [],'landlord_up': [],'landlord_down': []} 三个玩家的出牌记录
        #self.all_handcards = {'landlord': [],'landlord_up': [],'landlord_down': []} 三个玩家手里剩余的牌
        #self.init_card = {'landlord': [],'landlord_up': [],'landlord_down': []} 三个玩家初始牌


    def make_env(self,
                 player_hand_cards = [], #AI手里的牌
                 three_landlord_cards = [], #三张底牌
                 card_play_action_seq = [], #所有的出牌流程记录
                 played_cards = {}, #三个玩家的出牌记录
                 num_cards_left_dict = {}, #三个玩家手里剩余牌的数量
                 last_move_dict = {}

                 ):
        
        self.player_hand_cards = player_hand_cards
        self.three_landlord_cards = three_landlord_cards
        self.card_play_action_seq = card_play_action_seq
        self.played_cards = played_cards
        self.num_cards_left_dict = num_cards_left_dict
        self.last_move_dict = last_move_dict

        # print("player_position",self.player_position)
        # print("player_hand_cards",player_hand_cards)
        # print("three_landlord_cards",three_landlord_cards)
        # print("card_play_action_seq",card_play_action_seq)
        # print("played_cards",played_cards)
        # print("num_cards_left_dict",num_cards_left_dict)
        # print("last_move_dict",last_move_dict)
        # print('----------------------------------------------------------------------------------------------')
        #初始牌局：init_card
        self.AllEnvCard = [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7,
                        8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12,
                        12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 17, 17, 17, 17, 20, 30]
        
        counter1 = Counter(self.AllEnvCard)
        counter2 = Counter(self.player_hand_cards)
        other_cards = []
        for x in self.AllEnvCard:
            if counter1[x] > counter2[x]:
                other_cards.append(x)
                counter1[x] -= 1
        random.shuffle(other_cards) #AI手里的牌减去三张底牌及其他两家的牌

        if self.player_position == "landlord":
            self.init_card = {
                'three_landlord_cards':self.three_landlord_cards,
                "landlord":self.player_hand_cards,
                "landlord_up": other_cards[:17] ,
                "landlord_down": other_cards[-17:] 
            }
        elif self.player_position == "landlord_up":
            self.init_card = {
                'three_landlord_cards':self.three_landlord_cards,
                "landlord":other_cards[:20],
                "landlord_up": player_hand_cards  ,
                "landlord_down": other_cards[-17:]
            }
        elif self.player_position == "landlord_down":
            self.init_card = {
                'three_landlord_cards':self.three_landlord_cards,
                "landlord":other_cards[:20],
                "landlord_up": other_cards[-17:] ,
                "landlord_down":player_hand_cards 
            }

        #未出的牌
        try:
            self.other_hand_cards = gen_other_card(self.player_position,self.player_hand_cards,self.played_cards)
        except:
            pass
        # #最后一次出牌记录
        try:
            self.last_move = get_last_move(self.card_play_action_seq)
        except:
            pass
        # 最后两次次出牌记录
        try:
            self.last_two_moves = get_last_two_moves(self.card_play_action_seq)
        except:
            pass
        #三个玩家手里剩余的牌
        try:
            self.all_handcards = gen_all_cards(self.player_position,self.player_hand_cards,self.other_hand_cards,self.num_cards_left_dict,self.played_cards)
        except:
            pass

        if self.player_position == 'landlord' and len(self.last_move_dict['landlord_up']) != 0:
            self.last_pid = 'landlord_up'
        elif self.player_position == 'landlord_down' and len(self.last_move_dict['landlord']) != 0:
            self.last_pid = 'landlord'
        elif self.player_position == 'landlord_up' and len(self.last_move_dict['landlord_down']) != 0:
            self.last_pid = 'landlord_down'
        elif self.player_position == 'landlord' and len(self.last_move_dict['landlord_up']) == 0 and len(self.last_move_dict['landlord_down']) != 0:
            self.last_pid = 'landlord_down'
        elif self.player_position == 'landlord_down' and len(self.last_move_dict['landlord']) == 0 and len(self.last_move_dict['landlord_up']) != 0:
            self.last_pid = 'landlord_up'
        elif self.player_position == 'landlord_up' and len(self.last_move_dict['landlord_down']) == 0 and len(self.last_move_dict['landlord']) != 0:
            self.last_pid = 'landlord'
        else:
            self.last_pid = self.player_position
        # #炸弹出现次数

        for _,value in self.last_move_dict.items():
            if len(value) == 4 and len(list(set(value))) == 1 or value == [20,30]:
                self.bomb_num = self.bomb_num + 1

        #可以出牌的牌型
        try:
            self.legal_actions = get_legal_card_play_actions(self.all_handcards[self.player_position],self.card_play_action_seq)
        except:
            pass


#获取最后一次的出牌
def get_last_move(all_action = []):
    last_move = []
    if len(all_action) != 0:
        if len(all_action[-1]) == 0:
            last_move = all_action[-2]
        else:
            last_move = all_action[-1]

    return last_move

#获取最后二次的出牌
def get_last_two_moves(all_action = []):
    last_two_moves = [[], []]
    for card in all_action[-2:]:
        last_two_moves.insert(0, card)
        last_two_moves = last_two_moves[:2]
    return last_two_moves


#获取可以出的牌
def get_legal_card_play_actions(player_hand_cards=[],all_action=[]):
    mg = MovesGener(player_hand_cards)
    action_sequence = all_action

    rival_move = []
    if len(action_sequence) != 0:
        if len(action_sequence[-1]) == 0:
            rival_move = action_sequence[-2]
        else:
            rival_move = action_sequence[-1]

    rival_type = md.get_move_type(rival_move)
    rival_move_type = rival_type['type']
    rival_move_len = rival_type.get('len', 1)
    moves = list()

    if rival_move_type == md.TYPE_0_PASS:
        moves = mg.gen_moves()

    elif rival_move_type == md.TYPE_1_SINGLE:
        all_moves = mg.gen_type_1_single()
        moves = ms.filter_type_1_single(all_moves, rival_move)

    elif rival_move_type == md.TYPE_2_PAIR:
        all_moves = mg.gen_type_2_pair()
        moves = ms.filter_type_2_pair(all_moves, rival_move)

    elif rival_move_type == md.TYPE_3_TRIPLE:
        all_moves = mg.gen_type_3_triple()
        moves = ms.filter_type_3_triple(all_moves, rival_move)

    elif rival_move_type == md.TYPE_4_BOMB:
        all_moves = mg.gen_type_4_bomb() + mg.gen_type_5_king_bomb()
        moves = ms.filter_type_4_bomb(all_moves, rival_move)

    elif rival_move_type == md.TYPE_5_KING_BOMB:
        moves = []

    elif rival_move_type == md.TYPE_6_3_1:
        all_moves = mg.gen_type_6_3_1()
        moves = ms.filter_type_6_3_1(all_moves, rival_move)

    elif rival_move_type == md.TYPE_7_3_2:
        all_moves = mg.gen_type_7_3_2()
        moves = ms.filter_type_7_3_2(all_moves, rival_move)

    elif rival_move_type == md.TYPE_8_SERIAL_SINGLE:
        all_moves = mg.gen_type_8_serial_single(repeat_num=rival_move_len)
        moves = ms.filter_type_8_serial_single(all_moves, rival_move)

    elif rival_move_type == md.TYPE_9_SERIAL_PAIR:
        all_moves = mg.gen_type_9_serial_pair(repeat_num=rival_move_len)
        moves = ms.filter_type_9_serial_pair(all_moves, rival_move)

    elif rival_move_type == md.TYPE_10_SERIAL_TRIPLE:
        all_moves = mg.gen_type_10_serial_triple(repeat_num=rival_move_len)
        moves = ms.filter_type_10_serial_triple(all_moves, rival_move)

    elif rival_move_type == md.TYPE_11_SERIAL_3_1:
        all_moves = mg.gen_type_11_serial_3_1(repeat_num=rival_move_len)
        moves = ms.filter_type_11_serial_3_1(all_moves, rival_move)

    elif rival_move_type == md.TYPE_12_SERIAL_3_2:
        all_moves = mg.gen_type_12_serial_3_2(repeat_num=rival_move_len)
        moves = ms.filter_type_12_serial_3_2(all_moves, rival_move)

    elif rival_move_type == md.TYPE_13_4_2:
        all_moves = mg.gen_type_13_4_2()
        moves = ms.filter_type_13_4_2(all_moves, rival_move)

    elif rival_move_type == md.TYPE_14_4_22:
        all_moves = mg.gen_type_14_4_22()
        moves = ms.filter_type_14_4_22(all_moves, rival_move)

    if rival_move_type not in [md.TYPE_0_PASS,
                                md.TYPE_4_BOMB, md.TYPE_5_KING_BOMB]:
        moves = moves + mg.gen_type_4_bomb() + mg.gen_type_5_king_bomb()

    if len(rival_move) != 0:  # rival_move is not 'pass'
        moves = moves + [[]]

    for m in moves:
        m.sort()

    return moves
    
def gen_other_card(player_position,player_hand_cards,played_cards={}):
    # print(player_position)
    # print(player_hand_cards)
    # print(played_cards)


    play_card = []
    for key,valus in played_cards.items():
        if key != player_position:
            play_card.append(valus)
    play_card.append(player_hand_cards)

    AllEnvCard = [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7,
        8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12,
        12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 17, 17, 17, 17, 20, 30]
    All_Play_Card = [x for sublist in play_card for x in sublist] #将列表中的所有元素提取出来
    counter1 = Counter(AllEnvCard)
    counter2 = Counter(All_Play_Card)
    result = []
    for x in AllEnvCard:
        if counter1[x] > counter2[x]:
            result.append(x)
            counter1[x] -= 1
    result.sort()
    return result

def gen_all_cards(player_position,HandCards = [],other_hand_cards=[],num_cards_left_dict={},played_cards = {}):

    all_handcards = {"landlord": [],"landlord_up": [],"landlord_down": []}
    if player_position =="landlord":
        all_handcards['landlord'] = list((Counter(HandCards) - Counter(played_cards['landlord'])).elements())
        all_handcards['landlord_down'] = other_hand_cards[:num_cards_left_dict['landlord_down']]
        all_handcards['landlord_up'] = other_hand_cards[-num_cards_left_dict['landlord_up']:]

    elif player_position =="landlord_down":
        all_handcards['landlord'] = other_hand_cards[:num_cards_left_dict['landlord']]
        all_handcards['landlord_down'] = list((Counter(HandCards) - Counter(played_cards['landlord_down'])).elements())
        all_handcards['landlord_up'] = other_hand_cards[-num_cards_left_dict['landlord_up']:]

    elif player_position =="landlord_up":
        all_handcards['landlord'] = other_hand_cards[:num_cards_left_dict['landlord']]
        all_handcards['landlord_down'] = other_hand_cards[-num_cards_left_dict['landlord_down']:]
        all_handcards['landlord_up'] = list((Counter(HandCards) - Counter(played_cards['landlord_up'])).elements())

    #print(all_handcards[player_position])
    return all_handcards

if __name__ == "__main__":

    #三张底牌
    three_landlord_cards = [10, 8, 14]
    #AI手牌
    player_hand_cards = [4, 5, 6, 6, 7, 7, 8, 8, 8, 9, 9, 10, 11, 12, 13, 14, 20]
    #AI扮演角色
    player_position = 'landlord'
    #各个玩家出过的牌
    played_cards = {"landlord": [],"landlord_up": [],"landlord_down": []}
    #各个玩家最后的出牌动作
    last_move_dict = {"landlord": [],"landlord_up": [],"landlord_down": []}
    #所有的出牌顺序
    card_play_action_seq = []
    # 每个玩家手里剩余牌的数量
    num_cards_left_dict = {"landlord":20,"landlord_up": 17,"landlord_down": 17}

    game_info = InfoSet(player_position)
    game_info.make_env(player_hand_cards = player_hand_cards,
                       three_landlord_cards = three_landlord_cards,
                       card_play_action_seq = card_play_action_seq,
                       played_cards = played_cards,
                       num_cards_left_dict = num_cards_left_dict,
                       last_move_dict = last_move_dict
                       )

    # print('player_position:',game_info.player_position )
    # print('player_hand_cards:',game_info.player_hand_cards)
    # print('num_cards_left_dict:',game_info.num_cards_left_dict)
    # print('three_landlord_cards:',game_info.three_landlord_cards)
    # print('card_play_action_seq:',game_info.card_play_action_seq)
    # print('other_hand_cards:',game_info.other_hand_cards)
    # print('legal_actions:',game_info.legal_actions)
    # print('last_move:',game_info.last_move)
    # print('last_two_moves:',game_info.last_two_moves)
    # print('last_move_dict:',game_info.last_move_dict)
    # print('played_cards:',game_info.played_cards)
    # print('all_handcards:',game_info.all_handcards)
    # print('last_pid:',game_info.last_pid)
    # print('bomb_num:',game_info.bomb_num)
    # print('init_card:',game_info.init_card)

    #模型路径
    card_play_model_path_dict = {
        'landlord': "baselines/landlord.ckpt",
        'landlord_up': "baselines/landlord_up.ckpt",
        'landlord_down': "baselines/landlord_down.ckpt"
    }
    ai = DeepAgent(player_position,card_play_model_path_dict[player_position])
    best_action,best_action_confidence,action_list = ai.act(game_info)
    msg = {}
    for card in action_list:
        action = [EnvCard2RealCard[c] for c in list(card[0])]
        win_rate = round(card[1].tolist()[0],3)
        msg["".join(action)] = win_rate

    if len(list(msg.items())) >= 5:
        item = list(msg.items())[:5]
        print(json.dumps(item))
    else:
        item = list(msg.items())
        print(json.dumps(item))   
