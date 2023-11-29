from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Ui_ui2 import Ui_MainWindow
import sys
import os
import configparser
from yolo import yolo_detect
import cv2
import numpy as np
from capture import capture
import win32gui, win32con, win32api
import aircv as ac
import time
import BidModel
import random
from Check_Playing_rules import check_cards
from douzero.env.move_generator import *
from game_evn import *
from douzero.evaluation.deep_agent2 import DeepAgent

import datetime
import urllib.request


devlist = []
Hwnd = 0

hand_cards_pos_region = [450, 720, 0, 1280]  # 手牌区域
three_cards_pos_region = [0, 60, 330, 720]  # 底牌区域
down_cards_pos_region = [90, 315, 660, 1020]  # 玩家1出牌区域
up_cards_pos_region = [80, 315, 180, 640]  # 玩家2出牌区域
ai_cards_pos_region = [300, 500, 310, 890]  # AI出牌区域

# 模型路径
card_play_model_path_dict = {
    'landlord': "baselines/landlord.ckpt",
    'landlord_up': "baselines/landlord_up.ckpt",
    'landlord_down': "baselines/landlord_down.ckpt"
}

EnvCard2RealCard = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                    8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q',
                    13: 'K', 14: 'A', 17: '2', 20: 'X', 30: 'D'}

RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                    '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12,
                    'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30}

landlord1 = cv2.imdecode(np.fromfile("./pic/landlord1.bmp", dtype=np.uint8), -1)
landlord2 = cv2.imdecode(np.fromfile("./pic/landlord2.bmp", dtype=np.uint8), -1)
landlord3 = cv2.imdecode(np.fromfile("./pic/landlord3.bmp", dtype=np.uint8), -1)
landlord4 = cv2.imdecode(np.fromfile("./pic/landlord4.bmp", dtype=np.uint8), -1)
landlord5 = cv2.imdecode(np.fromfile("./pic/landlord5.bmp", dtype=np.uint8), -1)
landlord6 = cv2.imdecode(np.fromfile("./pic/landlord6.bmp", dtype=np.uint8), -1)
landlord7 = cv2.imdecode(np.fromfile("./pic/landlord7.bmp", dtype=np.uint8), -1)
landlord8 = cv2.imdecode(np.fromfile("./pic/landlord8.bmp", dtype=np.uint8), -1)
landlord9 = cv2.imdecode(np.fromfile("./pic/landlord9.bmp", dtype=np.uint8), -1)
gear0_1 = cv2.imdecode(np.fromfile("./pic/gear0_1.bmp", dtype=np.uint8), -1)
gear1_1 = cv2.imdecode(np.fromfile("./pic/gear1_1.bmp", dtype=np.uint8), -1)
gear2_1 = cv2.imdecode(np.fromfile("./pic/gear2_1.bmp", dtype=np.uint8), -1)
gear3_1 = cv2.imdecode(np.fromfile("./pic/gear3_1.bmp", dtype=np.uint8), -1)
gear0_2 = cv2.imdecode(np.fromfile("./pic/gear0_2.bmp", dtype=np.uint8), -1)
gear1_2 = cv2.imdecode(np.fromfile("./pic/gear1_2.bmp", dtype=np.uint8), -1)
gear2_2 = cv2.imdecode(np.fromfile("./pic/gear2_2.bmp", dtype=np.uint8), -1)
gear3_2 = cv2.imdecode(np.fromfile("./pic/gear3_2.bmp", dtype=np.uint8), -1)
pass1 = cv2.imdecode(np.fromfile("./pic/pass1.bmp", dtype=np.uint8), -1)
pass2 = cv2.imdecode(np.fromfile("./pic/pass2.bmp", dtype=np.uint8), -1)
no_play1 = cv2.imdecode(np.fromfile("./pic/no_play1.bmp", dtype=np.uint8), -1)
no_play2 = cv2.imdecode(np.fromfile("./pic/no_play2.bmp", dtype=np.uint8), -1)
play1 = cv2.imdecode(np.fromfile("./pic/play1.bmp", dtype=np.uint8), -1)
play2 = cv2.imdecode(np.fromfile("./pic/play2.bmp", dtype=np.uint8), -1)
CanNot1 = cv2.imdecode(np.fromfile("./pic/CanNot1.bmp", dtype=np.uint8), -1)
CanNot2 = cv2.imdecode(np.fromfile("./pic/CanNot2.bmp", dtype=np.uint8), -1)
again1 = cv2.imdecode(np.fromfile("./pic/again1.bmp", dtype=np.uint8), -1)
again2 = cv2.imdecode(np.fromfile("./pic/again2.bmp", dtype=np.uint8), -1)

play_flag1 = cv2.imdecode(np.fromfile("./pic/play_flag1.bmp", dtype=np.uint8), -1)
play_flag2 = cv2.imdecode(np.fromfile("./pic/play_flag2.bmp", dtype=np.uint8), -1)
play_flag3 = cv2.imdecode(np.fromfile("./pic/play_flag3.bmp", dtype=np.uint8), -1)
play_flag4 = cv2.imdecode(np.fromfile("./pic/play_flag4.bmp", dtype=np.uint8), -1)
play_flag5 = cv2.imdecode(np.fromfile("./pic/play_flag5.bmp", dtype=np.uint8), -1)
play_flag6 = cv2.imdecode(np.fromfile("./pic/play_flag6.bmp", dtype=np.uint8), -1)

over_flag1 = cv2.imdecode(np.fromfile("./pic/over_flag1.bmp", dtype=np.uint8), -1)
over_flag2 = cv2.imdecode(np.fromfile("./pic/over_flag2.bmp", dtype=np.uint8), -1)
Cancel = cv2.imdecode(np.fromfile("./pic/Cancel.bmp", dtype=np.uint8), -1)
no_life = cv2.imdecode(np.fromfile("./pic/no_life.bmp", dtype=np.uint8), -1)
tips1 = cv2.imdecode(np.fromfile("./pic/tips1.bmp", dtype=np.uint8), -1)
tips2 = cv2.imdecode(np.fromfile("./pic/tips2.bmp", dtype=np.uint8), -1)


# --------------------------------------------------------------------------------------------
def list_remove(all_list, sub_list):
    for a in sub_list:
        for b in all_list:
            if a == b:
                all_list.remove(b)
                break
    return all_list


# --------------------------------------------------------------------------------------------
def doClick(cx, cy):
    global Hwnd
    long_position = win32api.MAKELONG(int(cx), int(cy))  # 模拟鼠标指针 传送到指定坐标
    win32api.SendMessage(Hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)  # 模拟鼠标按下
    win32api.SendMessage(Hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)  # 模拟鼠标弹起


# --------------------------------------------------------------------------------------------
def find_pic(pics, threshold=0.8, click=False):
    global Hwnd
    sourec_pic = capture(Hwnd)
    try:
        pos = ac.find_template(im_source=sourec_pic, im_search=pics, threshold=threshold, rgb=True)
    except:
        return False
    if pos:
        if click:
            doClick(pos['result'][0], pos['result'][1])
        return True
    return False


# --------------------------------------------------------------------------------------------
def find_pic2(sourec_pic, pics, threshold=0.8):
    try:
        pos = ac.find_template(im_source=sourec_pic, im_search=pics, threshold=threshold, rgb=True)
    except:
        return False
    if pos:
        return True
    return False


# --------------------------------------------------------------------------------------------
def find_closest_number(num, lst):
    closest = lst[0]
    diff = abs(num - closest)
    for i in range(1, len(lst)):
        if abs(num - lst[i]) < diff:
            closest = lst[i]
            diff = abs(num - closest)
    if abs(num - closest) > 10:
        # 距离较远
        return True
    else:
        return False


# --------------------------------------------------------------------------------------------

class DouDiZhu(QThread):
    Signal_Up_action = pyqtSignal(str)
    Signal_Up_play_card = pyqtSignal(str)  # 更新上家出牌信息
    Signal_Down_play_card = pyqtSignal(str)  # 更新下家出牌信息
    Signal_Ai_play_card = pyqtSignal(str)  # 更新Ai出牌信息
    Signal_Three_card = pyqtSignal(str)  # 更新底牌信息
    Signal_ai_play_history = pyqtSignal(str)  # 更新AI出牌记录
    Signal_up_play_history = pyqtSignal(str)  # 更新上家出来记录
    Signal_down_play_history = pyqtSignal(str)  # 更新下家出牌记录
    Signal_up_msg = pyqtSignal(str)  # 更新输出信息
    Signal_Record_card = pyqtSignal(list)  # 更新出牌记录信息

    Working = True

    def __init__(self):
        super(QThread, self).__init__()

    ########################################################################
    # 获取地主三张底牌
    def find_three_cards(self):
        global Hwnd, three_cards_pos_region
        img = capture(Hwnd)
        img = img[three_cards_pos_region[0]:three_cards_pos_region[1],
              three_cards_pos_region[2]:three_cards_pos_region[3]]  # 我的牌
        _, class_list, pos_list, = yolo_detect(img)
        if class_list and len(class_list) == 3:
            return ''.join(class_list)
        else:
            return []

    ########################################################################
    # 识别AI手里的牌
    def Get_MyHandCards(self):
        global Hwnd, hand_cards_pos_region
        if find_pic(again1, threshold=0.8, click=True):
            time.sleep(5)
        if find_pic(again2, threshold=0.8, click=True):
            time.sleep(5)
        img = capture(Hwnd)
        img = img[hand_cards_pos_region[0]:hand_cards_pos_region[1],
              hand_cards_pos_region[2]:hand_cards_pos_region[3]]  # 我的牌
        _, class_list, pos_list, = yolo_detect(img)
        if class_list == None:
            return []

        return ''.join([str(i) for i in class_list])

    ########################################################################
    # 获取下家出牌
    def get_down_play_cards(self):
        global Hwnd, down_cards_pos_region
        img = capture(Hwnd)
        img = img[down_cards_pos_region[0]:down_cards_pos_region[1],
              down_cards_pos_region[2]:down_cards_pos_region[3]]  # 我的牌
        _, class_list, _, = yolo_detect(img)
        if class_list:
            class_list.sort()
            return class_list
        return []

    ########################################################################
    # 获取上家出牌
    def get_up_play_cards(self):
        global Hwnd, up_cards_pos_region
        img = capture(Hwnd)
        img = img[up_cards_pos_region[0]:up_cards_pos_region[1], up_cards_pos_region[2]:up_cards_pos_region[3]]  # 我的牌
        _, class_list, pos_list, = yolo_detect(img)
        if class_list:
            class_list.sort()
            return class_list
        return []

    ########################################################################
    # 获取AI出牌
    def get_ai_play_cards(self):
        global Hwnd, up_cards_pos_region
        img = capture(Hwnd)
        img = img[ai_cards_pos_region[0]:ai_cards_pos_region[1], ai_cards_pos_region[2]:ai_cards_pos_region[3]]  # 我的牌
        _, class_list, pos_list, = yolo_detect(img)
        if class_list:
            class_list.sort()
            return class_list
        return []

    ########################################################################
    # 识别AI扮演的角色
    def find_landlord(self):
        # ['landlord_up', 'landlord', 'landlord_down']
        items = ("地主上家", "地主", "地主下家")
        sourec_pic = capture(Hwnd)
        items = []
        items.append(landlord1)
        items.append(landlord2)
        items.append(landlord3)
        items.append(landlord4)
        items.append(landlord5)
        items.append(landlord6)
        items.append(landlord7)
        items.append(landlord8)
        items.append(landlord7)

        for i in items:
            pos = ac.find_template(im_source=sourec_pic, im_search=i, threshold=0.8, rgb=True)
            if pos:
                cv2.rectangle(sourec_pic, pos['rectangle'][0], pos['rectangle'][3], [0, 0, 255], 2)
                ret = pos['result']
                x, y = ret
                if x < 640 and y < 360:
                    self.user_position_code = items[2]  # "地主下家"
                    self.Signal_up_msg.emit("Ai角色【地主下家】")
                    return 'landlord_down'
                elif x > 640:
                    self.Signal_up_msg.emit("Ai角色【地主上家】")
                    self.user_position_code = items[0]  # "地主上家"
                    return 'landlord_up'
                elif y > 400:
                    self.Signal_up_msg.emit("Ai角色【地主】")
                    self.user_position_code = items[1]  # "地主"
                    return 'landlord'
        return False

    ########################################################################
    # 检查出牌区域是不是有牌（白色）
    def check_white(self, s='left'):
        image = capture(Hwnd)
        if s == "left":
            image = image[up_cards_pos_region[0]:up_cards_pos_region[1], up_cards_pos_region[2]:up_cards_pos_region[3]]
        elif s == "right":
            image = image[down_cards_pos_region[0]:down_cards_pos_region[1],
                    down_cards_pos_region[2]:down_cards_pos_region[3]]

        card_items = []
        card_items.append(play_flag1)
        card_items.append(play_flag1)
        card_items.append(play_flag1)
        card_items.append(play_flag1)
        card_items.append(play_flag1)
        card_items.append(play_flag1)

        for card in card_items:
            if find_pic2(image, card):
                return True
                break
        return False

    ########################################################################
    def check_pass(self, s='left'):
        image = capture(Hwnd)
        if s == "left":
            image = image[up_cards_pos_region[0]:up_cards_pos_region[1], up_cards_pos_region[2]:up_cards_pos_region[3]]
        elif s == "right":
            image = image[down_cards_pos_region[0]:down_cards_pos_region[1],
                    down_cards_pos_region[2]:down_cards_pos_region[3]]

        if find_pic2(image, pass1) or find_pic2(image, pass2):
            return True
        else:
            return False

    ########################################################################
    def seleck_cards(self, cards):  #
        global Hwnd
        position_list = [0]
        for i in range(random.randint(2, 4)):
            doClick(random.randint(520, 750), random.randint(160, 340))
            time.sleep(0.05)
        time.sleep(0.05)
        _, class_list, pos_list, = yolo_detect(capture(Hwnd))
        try:
            min_value = min([sub_list[1] for sub_list in pos_list]) - 10
        except:
            return

        for card in cards:  # 待选的牌
            _, class_list, pos_list, = yolo_detect(capture(Hwnd))
            print(class_list)
            if len(class_list) <= 0:
                return
            for c, p in zip(class_list, pos_list):
                if c != card:
                    continue
                if c == card and p[1] >= min_value and find_closest_number(p[0], position_list):
                    doClick(p[0] + 20, p[1] + 90)
                    time.sleep(0.1)
                    position_list.append(p[0])
                    break
                elif c == card and p[1] < min_value and find_closest_number(p[0], position_list):
                    position_list.append(p[0])
                    break
            time.sleep(0.05)

        time.sleep(0.05)
        _, class_list, pos_list, = yolo_detect(capture(Hwnd))
        if class_list:
            for c, p in zip(class_list, pos_list):
                if p[1] < min_value and find_closest_number(p[0], position_list):
                    print(c, p)
                    doClick(p[0] + 20, p[1] + 90)
                    time.sleep(0.05)

        if find_pic(play1, click=True):
            time.sleep(0.01)
        if find_pic(play2, click=True):
            time.sleep(0.01)

    ########################################################################

    def job_run(self):

        # 智能体需要的参数
        # 1 三张底牌
        three_landlord_cards = []
        # 2 AI手牌
        player_hand_cards = []
        # 3 AI扮演角色
        player_position = ''
        # 4 各个玩家出的牌
        played_cards = {"landlord": [], "landlord_up": [], "landlord_down": []}
        # 5 各个玩家最后出的牌
        last_move_dict = {"landlord": [], "landlord_up": [], "landlord_down": []}
        # 6 所有的出牌顺序
        card_play_action_seq = []
        # 7 各个玩家手里剩余牌的数量
        num_cards_left_dict = {"landlord": 20, "landlord_up": 17, "landlord_down": 17}

        ai_play_his = []
        up_play_his = []
        down_play_his = []

        self.AllEnvCard = [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7,
                           8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12,
                           12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 17, 17, 17, 17, 20, 30]
        while True:
            # 获取手牌
            self.HandCards = self.Get_MyHandCards()
            # 评估当前手里的牌
            s = "".join(self.HandCards)
            score = BidModel.predict_score(s)
            self.Signal_up_msg.emit('当前叫地主评分:{}'.format(round(score, 2)))
            if score < 0.3 and (find_pic(gear0_1, click=True) or find_pic(gear0_2, click=True)):
                self.Signal_up_msg.emit('不叫')
            elif score > 0.3 and score <= 1 and (find_pic(gear1_1, click=True) or find_pic(gear1_2, click=True)):
                self.Signal_up_msg.emit('叫1分')
            elif score > 1 and score <= 1.5 and (find_pic(gear2_1, click=True) or find_pic(gear2_2, click=True)):
                self.Signal_up_msg.emit('叫2分')
            elif find_pic(gear3_1, click=True) or find_pic(gear3_2, click=True):
                self.Signal_up_msg.emit('叫3分')
            self.three_cards = self.find_three_cards()
            if len(self.three_cards) > 0:
                self.Signal_Three_card.emit("底牌:" + "-".join(self.three_cards))
                break
            else:
                self.Signal_Three_card.emit("底牌:???")
            time.sleep(2)

        # 判断AI扮演的角色
        while True:
            self.Signal_up_msg.emit('判断AI扮演的角色')
            self.user_position = self.find_landlord()  # 判断AI扮演的角色 #['landlord_up', 'landlord', 'landlord_down']
            if self.user_position:
                break
            time.sleep(1)

        self.HandCards = self.Get_MyHandCards()

        # 得到出牌顺序
        # 出牌顺序：0-玩家出牌, 1-玩家下家出牌, 2-玩家上家出牌
        if self.user_position == "landlord":
            play_order = 0
        elif self.user_position == "landlord_up":
            play_order = 1
        else:
            play_order = 2

        # 创建智能体
        game_info = InfoSet(self.user_position)
        Agent = DeepAgent(self.user_position, card_play_model_path_dict[self.user_position])

        self.Signal_up_msg.emit('出牌中...')
        while True:
            if find_pic(over_flag1) or find_pic(over_flag2):
                break
            if find_pic(no_life, click=True):
                break
            if find_pic(again1, click=True):
                break
            if find_pic(again2, click=True):
                break
            if find_pic(Cancel, click=True):
                time.sleep(0.1)

            ##############################################################################
            # AI出牌

            # [RealCard2EnvCard[c] for c in list(self.three_cards)]
            if play_order == 0:

                cards = []
                self.Signal_Ai_play_card.emit('Ai思考中...')
                game_info.make_env(player_hand_cards=[RealCard2EnvCard[c] for c in list(self.HandCards)],
                                   three_landlord_cards=[RealCard2EnvCard[c] for c in list(self.three_cards)],
                                   card_play_action_seq=card_play_action_seq,
                                   played_cards=played_cards,
                                   num_cards_left_dict=num_cards_left_dict,
                                   last_move_dict=last_move_dict
                                   )
                # 智能体计算
                try:
                    best_action, best_action_win_rate, action_list = Agent.act(game_info)
                except:
                    return
                action_message = {"action": str(''.join([EnvCard2RealCard[c] for c in best_action])),
                                  "win_rate": str(round(float(best_action_win_rate) * 100, 2)) + "%"}

                msg = {}
                # 遍历智能体计算的结果
                for card in action_list:
                    action = [EnvCard2RealCard[c] for c in list(card[0])]
                    if len(action) == 0:
                        action = ["Pass"]
                    win_rate = round(card[1].tolist()[0], 3)
                    msg["".join(action)] = win_rate

                if len(list(msg.items())) >= 5:
                    item = list(msg.items())[:5]
                else:
                    item = list(msg.items())
                self.Signal_Up_action.emit(json.dumps(item))

                # 自动出牌
                if action_message['action'] != "" and myWin.checkBox_Auto.isChecked():
                    self.Signal_Ai_play_card.emit(action_message['action'])
                    for i in range(5):
                        self.seleck_cards(action_message['action'].replace('10', 'T'))
                        time.sleep(0.2)
                        if find_pic(tips1) == False and find_pic(tips2) == False:
                            break
                        time.sleep(0.1)

                    cards = list(action_message['action'])
                else:
                    self.Signal_Ai_play_card.emit('Pass')

                if myWin.checkBox_Auto.isChecked():  # 自动出牌后要点击戳爱
                    find_pic(CanNot1, click=True)
                    find_pic(CanNot2, click=True)
                    find_pic(no_play1, click=True)
                    find_pic(no_play2, click=True)

                if not myWin.checkBox_Auto.isChecked():  # 手动出牌等待出牌结束
                    while True:
                        if find_pic(play1) == False and find_pic(play2) == False:
                            time.sleep(0.1)
                            break
                        time.sleep(0.1)

                    for i in range(3):
                        cards = self.get_ai_play_cards()
                        if cards:
                            break
                        time.sleep(0.1)

                elif myWin.checkBox_Auto.isChecked() and action_message['action'] == "":  # Pass
                    cards = []

                self.Signal_Record_card.emit(cards)

                # 发送出牌历史信息
                ai_play_his.append(''.join(cards))
                play_his = ['P' if x == '' else x for x in ai_play_his]
                his = '-'.join(play_his)
                self.Signal_ai_play_history.emit(his)

                play_cards = [RealCard2EnvCard[c] for c in list(cards)]

                card_play_action_seq.append(play_cards)
                if self.user_position == "landlord":
                    played_cards["landlord"].extend(play_cards)
                    last_move_dict["landlord"] = play_cards
                    num_cards_left_dict["landlord"] = num_cards_left_dict["landlord"] - len(cards)

                if self.user_position == "landlord_up":
                    played_cards["landlord_up"].extend(play_cards)
                    last_move_dict["landlord_up"] = play_cards
                    num_cards_left_dict["landlord_up"] = num_cards_left_dict["landlord"] - len(cards)

                if self.user_position == "landlord_down":
                    played_cards["landlord_down"].extend(play_cards)
                    last_move_dict["landlord_down"] = play_cards
                    num_cards_left_dict["landlord_down"] = num_cards_left_dict["landlord"] - len(cards)

                play_order = 1
                time.sleep(0.1)

            ##############################################################################
            # 右边>等待下家出牌
            elif play_order == 1:
                cards = []
                self.Signal_Down_play_card.emit("等待下家出牌...")
                pass_flag = False

                while True:
                    if find_pic(tips1) or find_pic(tips2) or find_pic(CanNot1) or find_pic(CanNot2):
                        break
                    if self.check_white('right'):
                        break
                    if self.check_pass(s='right'):
                        pass_flag = True
                        break
                    if find_pic(over_flag1) or find_pic(over_flag2):
                        break
                    time.sleep(0.01)

                if pass_flag == False:
                    time.sleep(0.5)
                    for i in range(20):
                        cards = self.get_down_play_cards()
                        texts = '-'.join([str(i) for i in cards])
                        if check_cards(texts) != '':
                            break
                        if self.check_white('right') == False:
                            break
                        time.sleep(0.1)

                self.Signal_Record_card.emit(cards)
                if cards:
                    texts = '-'.join([str(i) for i in cards])
                    self.Signal_Down_play_card.emit(texts)
                else:
                    self.Signal_Down_play_card.emit("Pass")

                # 发送出牌历史信息
                down_play_his.append(''.join(cards))
                play_his = ['P' if x == '' else x for x in down_play_his]
                his = '-'.join(play_his)
                self.Signal_down_play_history.emit(his)

                play_cards = [RealCard2EnvCard[c] for c in list(cards)]  # 转为AI能识别的数字
                # 最后的出牌动作
                card_play_action_seq.append(play_cards)
                if self.user_position == "landlord":
                    played_cards["landlord_down"].extend(play_cards)
                    last_move_dict["landlord_down"] = play_cards
                    num_cards_left_dict["landlord_down"] = num_cards_left_dict["landlord_down"] - len(cards)

                elif self.user_position == "landlord_up":
                    played_cards["landlord"].extend(play_cards)
                    last_move_dict["landlord"] = play_cards
                    num_cards_left_dict["landlord"] = num_cards_left_dict["landlord"] - len(cards)

                elif self.user_position == "landlord_down":
                    played_cards["landlord_up"].extend(play_cards)
                    last_move_dict["landlord_up"] = play_cards
                    num_cards_left_dict["landlord_up"] = num_cards_left_dict["landlord_up"] - len(cards)

                play_order = 2
            ##############################################################################
            # 左边>等待上家出牌
            elif play_order == 2:
                cards = []
                self.Signal_Up_play_card.emit("等待上家出牌...")
                pass_flag = False

                while True:
                    if find_pic(tips1) or find_pic(tips2) or find_pic(CanNot1) or find_pic(CanNot2):
                        break
                    if self.check_white('left'):
                        break
                    if self.check_pass(s='left'):
                        pass_flag = True
                        break
                    if find_pic(over_flag1) or find_pic(over_flag2):
                        break
                    time.sleep(0.01)

                if pass_flag == False:
                    time.sleep(0.5)
                    for i in range(20):
                        cards = self.get_up_play_cards()
                        texts = '-'.join([str(i) for i in cards])
                        if check_cards(texts) != '':
                            break
                        if self.check_white('left') == False:
                            break
                        time.sleep(0.1)

                self.Signal_Record_card.emit(cards)
                if cards:
                    texts = '-'.join([str(i) for i in cards])
                    self.Signal_Up_play_card.emit(texts)
                else:
                    self.Signal_Up_play_card.emit("Pass")

                # 发送出牌历史信息
                up_play_his.append(''.join(cards))
                play_his = ['P' if x == '' else x for x in up_play_his]
                his = '-'.join(play_his)
                self.Signal_up_play_history.emit(his)

                play_cards = [RealCard2EnvCard[c] for c in list(cards)]

                card_play_action_seq.append(play_cards)
                if self.user_position == "landlord":
                    played_cards["landlord_up"].extend(play_cards)
                    last_move_dict["landlord_up"] = play_cards
                    num_cards_left_dict["landlord_up"] = num_cards_left_dict["landlord_up"] - len(cards)

                if self.user_position == "landlord_up":
                    played_cards["landlord_down"].extend(play_cards)
                    last_move_dict["landlord_down"] = play_cards
                    num_cards_left_dict["landlord_down"] = num_cards_left_dict["landlord_down"] - len(cards)

                if self.user_position == "landlord_down":
                    played_cards["landlord"].extend(play_cards)
                    last_move_dict["landlord"] = play_cards
                    num_cards_left_dict["landlord"] = num_cards_left_dict["landlord"] - len(cards)
                play_order = 0
                ##############################################################################

            ##############################################################################
        time.sleep(3)

    def run(self):
        while self.Working:
            self.Signal_Record_card.emit(['-1'])
            self.Signal_Up_action.emit('')
            self.Signal_Up_play_card.emit('')
            self.Signal_Down_play_card.emit('')
            self.Signal_Ai_play_card.emit('')
            self.Signal_Three_card.emit('')
            self.Signal_ai_play_history.emit('')
            self.Signal_up_play_history.emit('')
            self.Signal_down_play_history.emit('')
            self.Signal_up_msg.emit('')  # 更新输出信息
            self.Signal_Record_card.emit(['-1'])

            self.job_run()
            time.sleep(1)


# --------------------------------------------------------------------------------------------

class MyMainWindow(QMainWindow, Ui_MainWindow, QObject):
    SignalData = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        try:
            self.setWindowIcon(QIcon('.\pic\logo.ico'))
        except:
            pass

        self.pushButton_Refresh.clicked.connect(self.Refresh_devices)  # 刷新模拟器
        self.pushButton_init.clicked.connect(self.devices_init)  # 初始化
        self.pushButton_hand.clicked.connect(self.detection_hand_cards)  # 检测手牌
        self.pushButton_three.clicked.connect(self.detection_thred_card)  # 检测三张底牌
        self.pushButton_up_card.clicked.connect(self.detection_up_play)  # 检测上家出牌
        self.pushButton_down_card.clicked.connect(self.detection_down_play)  # 检测下家出牌
        self.pushButton_start.clicked.connect(self.game_start)  # 启动脚本
        self.horizontalScrollBar.valueChanged.connect(self.setOpacity)

    def setOpacity(self):
        valus = (self.horizontalScrollBar.value() / 10)
        self.setWindowOpacity(valus)

    ########################################################################
    def Refresh_devices(self):
        global devlist
        devlist.clear()
        self.comboBox_drives.clear()

        # 索引、标题、顶层窗口句柄、绑定窗口句柄、是否进入android（是否运行）、进程PID、VBox进程PID
        # cmd = 'D:\LDPlayer9\ldconsole.exe list2'
        cmd = 'dnconsole.exe list2'

        result = os.popen(cmd).read()
        info = result.split('\n')
        result = list()
        for line in info:
            if len(line) > 1:
                dnplayer = line.split(',')
                if dnplayer[3] != "0":
                    devlist.append([dnplayer[0], dnplayer[1], dnplayer[3]])

        for devs in devlist:
            self.comboBox_drives.addItem(devs[1])

    ########################################################################
    def devices_init(self):
        global Hwnd, devlist
        index = self.comboBox_drives.currentIndex()
        try:
            Hwnd = int(devlist[index][2])
        except:
            pass
        self.setWindowTitle("JJ斗地主 - " + devlist[index][1])

    ########################################################################
    def detection_hand_cards(self):
        global Hwnd
        while True:
            img = capture(Hwnd)
            img = img[hand_cards_pos_region[0]:hand_cards_pos_region[1],
                  hand_cards_pos_region[2]:hand_cards_pos_region[3]]
            image, class_list, pos_list = yolo_detect(img)
            cv2.imshow("ESC", image)
            # 等待 25 毫秒
            if cv2.waitKey(25) & 0xFF == 27:
                cv2.destroyWindow("ESC")
                return

    ########################################################################
    def detection_up_play(self):
        global Hwnd
        while True:
            img = capture(Hwnd)
            img = img[up_cards_pos_region[0]:up_cards_pos_region[1], up_cards_pos_region[2]:up_cards_pos_region[3]]
            image, class_list, pos_list = yolo_detect(img)
            cv2.imshow("ESC", image)
            # 等待 25 毫秒
            if cv2.waitKey(25) & 0xFF == 27:
                cv2.destroyWindow("ESC")
                return

    ########################################################################
    def detection_down_play(self):
        global Hwnd
        while True:
            img = capture(Hwnd)
            img = img[down_cards_pos_region[0]:down_cards_pos_region[1],
                  down_cards_pos_region[2]:down_cards_pos_region[3]]
            image, class_list, pos_list = yolo_detect(img)
            cv2.imshow("ESC", image)
            # 等待 25 毫秒
            if cv2.waitKey(25) & 0xFF == 27:
                # 按下 'q' 键退出
                cv2.destroyWindow("ESC")
                return

    ########################################################################
    def detection_thred_card(self):
        global Hwnd
        while True:
            img = capture(Hwnd)
            img = img[three_cards_pos_region[0]:three_cards_pos_region[1],
                  three_cards_pos_region[2]:three_cards_pos_region[3]]
            image, class_list, pos_list = yolo_detect(img)
            cv2.imshow("ESC", image)
            # 等待 25 毫秒
            if cv2.waitKey(25) & 0xFF == 27:
                # 按下 'q' 键退出
                cv2.destroyWindow("ESC")
                return

    ########################################################################
    # 更新AI出牌策略
    def up_action_lisy(self, msg):
        self.label_action_list.setText(msg)

    ########################################################################
    # 更新上家出牌信息
    def up_Up_play_cards(self, msg):
        self.label_up_play_card.setText(msg)

    ########################################################################
    # 更新下家出牌信息
    def up_Down_play_cards(self, msg):
        self.label_down_play_card.setText(msg)

    ########################################################################
    # 更新Ai出牌信息
    def up_Ai_play_cards(self, msg):
        self.label_ai_play_card.setText(msg)

    ########################################################################
    # 更新底牌信息
    def up_Three_card(self, msg):
        self.label_three_card.setText(msg)

    ########################################################################
    # 更新AI出牌记录
    def up_ai_play_history(self, msg):
        self.label_ai_play_history.setText(msg)

    ########################################################################
    # 更新上家出牌记录
    def up_Up_play_history(self, msg):
        self.label_up_play_history.setText(msg)

    ########################################################################
    # 更新下家出牌记录
    def up_Down_play_history(self, msg):
        self.label_down_play_history.setText(msg)

    ########################################################################
    # 更新输出信息
    def up_msg(self, msg):
        self.label_msg.setText(msg)

    ########################################################################
    # 更新记牌器
    def up_record(self, msg_list):
        for value in msg_list:
            if value == "-1" or value == -1:
                for col in range(15):
                    item = QTableWidgetItem("0")
                    self.tableWidget.setItem(0, col, item)
            if value == "3":
                col = 0
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "4":
                col = 1
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "5":
                col = 2
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "6":
                col = 3
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "7":
                col = 4
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "8":
                col = 5
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "9":
                col = 6
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)

            elif value == "T":
                col = 7
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "J":
                col = 8
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "Q":
                col = 9
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "K":
                col = 10
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "A":
                col = 11
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "2":
                col = 12
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "X":
                col = 13
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)
            elif value == "D":
                col = 14
                item = self.tableWidget.item(0, col)
                new_value = int(item.text()) + 1
                item = QTableWidgetItem(str(new_value))
                self.tableWidget.setItem(0, col, item)

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置水平和垂直居中对齐

    ########################################################################
    def game_start(self):
        self.pushButton_start.setEnabled(False)
        self.game = DouDiZhu()
        self.game.Signal_Up_action.connect(self.up_action_lisy)  # 更新上家出牌信息
        self.game.Signal_Up_play_card.connect(self.up_Up_play_cards)  # 更新上家出牌信息
        self.game.Signal_Down_play_card.connect(self.up_Down_play_cards)  # 更新下家出牌信息
        self.game.Signal_Ai_play_card.connect(self.up_Ai_play_cards)  # 更新Ai出牌信息
        self.game.Signal_Three_card.connect(self.up_Three_card)  # 更新底牌信息
        self.game.Signal_ai_play_history.connect(self.up_ai_play_history)  # 更新AI出牌记录
        self.game.Signal_up_play_history.connect(self.up_Up_play_history)  # 更新上家出来记录
        self.game.Signal_down_play_history.connect(self.up_Down_play_history)  # 更新下家出牌记录

        self.game.Signal_up_msg.connect(self.up_msg)  # 更新输出信息
        self.game.Signal_Record_card.connect(self.up_record)  # 更新记牌器
        self.game.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
