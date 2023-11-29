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

# 初始化一些变量和常量
devlist = []
Hwnd = 0

# 定义不同区域的位置，用于图像识别
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

# 定义牌值转换字典
EnvCard2RealCard = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                    8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q',
                    13: 'K', 14: 'A', 17: '2', 20: 'X', 30: 'D'}

RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                    '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12,
                    'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30}

# 从文件中加载图像资源，用于图像匹配
landlord1 = cv2.imdecode(np.fromfile("./pic/landlord1.bmp", dtype=np.uint8), -1)
# ... (省略了其他的图像加载代码)

# --------------------------------------------------------------------------------------------
def list_remove(all_list, sub_list):
    # 从一个列表中移除另一个列表中的元素
    for a in sub_list:
        for b in all_list:
            if a == b:
                all_list.remove(b)
                break
    return all_list

# --------------------------------------------------------------------------------------------
def doClick(cx, cy):
    # 模拟在指定位置进行鼠标点击
    global Hwnd
    long_position = win32api.MAKELONG(int(cx), int(cy))
    win32api.SendMessage(Hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
    win32api.SendMessage(Hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)

# --------------------------------------------------------------------------------------------
def find_pic(pics, threshold=0.8, click=False):
    # 在屏幕上查找匹配的图片
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
    # 在给定的图片上查找匹配的小图片
    try:
        pos = ac.find_template(im_source=sourec_pic, im_search=pics, threshold=threshold, rgb=True)
    except:
        return False
    if pos:
        return True
    return False


# --------------------------------------------------------------------------------------------
def find_closest_number(num, lst):
    # 在列表中找到距离给定数字最近的数
    closest = lst[0]
    diff = abs(num - closest)
    for i in range(1, len(lst)):
        if abs(num - lst[i]) < diff:
            closest = lst[i]
            diff = abs(num - closest)
    if abs(num - closest) > 10:
        # 如果最近的数与给定数的差值大于10，则返回True
        return True
    else:
        return False


# --------------------------------------------------------------------------------------------

class DouDiZhu(QThread):
    # 创建斗地主游戏的主要线程类
    # 定义一些信号，用于与图形用户界面通信
    Signal_Up_action = pyqtSignal(str)
    Signal_Up_play_card = pyqtSignal(str)  # 更新上家出牌信息
    Signal_Down_play_card = pyqtSignal(str)  # 更新下家出牌信息
    Signal_Ai_play_card = pyqtSignal(str)  # 更新Ai出牌信息
    Signal_Three_card = pyqtSignal(str)  # 更新底牌信息
    Signal_ai_play_history = pyqtSignal(str)  # 更新AI出牌记录
    Signal_up_play_history = pyqtSignal(str)  # 更新上家出牌记录
    Signal_down_play_history = pyqtSignal(str)  # 更新下家出牌记录
    Signal_up_msg = pyqtSignal(str)  # 更新输出信息
    Signal_Record_card = pyqtSignal(list)  # 更新出牌记录信息

    Working = True

    def __init__(self):
        # 初始化线程
        super(QThread, self).__init__()

    ########################################################################
    # 获取地主三张底牌
    def find_three_cards(self):
        # 截取特定区域的屏幕图像并通过YOLO模型检测牌面
        global Hwnd, three_cards_pos_region
        img = capture(Hwnd)
        img = img[three_cards_pos_region[0]:three_cards_pos_region[1],
              three_cards_pos_region[2]:three_cards_pos_region[3]]  # 截取底牌区域的图像
        _, class_list, pos_list, = yolo_detect(img)
        if class_list and len(class_list) == 3:
            return ''.join(class_list)
        else:
            return []

    ########################################################################
    # 识别AI手里的牌
    def Get_MyHandCards(self):
        # 截取特定区域的屏幕图像并通过YOLO模型检测手牌
        global Hwnd, hand_cards_pos_region
        if find_pic(again1, threshold=0.8, click=True):
            time.sleep(5)
        if find_pic(again2, threshold=0.8, click=True):
            time.sleep(5)
        img = capture(Hwnd)
        img = img[hand_cards_pos_region[0]:hand_cards_pos_region[1],
              hand_cards_pos_region[2]:hand_cards_pos_region[3]]  # 截取手牌区域的图像
        _, class_list, pos_list, = yolo_detect(img)
        if class_list == None:
            return []

        return ''.join([str(i) for i in class_list])

    ########################################################################
    # 获取下家出牌
    def get_down_play_cards(self):
        # 截取特定区域的屏幕图像并通过YOLO模型检测下家出的牌
        global Hwnd, down_cards_pos_region
        img = capture(Hwnd)
        img = img[down_cards_pos_region[0]:down_cards_pos_region[1],
              down_cards_pos_region[2]:down_cards_pos_region[3]]  # 截取下家出牌区域的图像
        _, class_list, _, = yolo_detect(img)
        if class_list:
            class_list.sort()
            return class_list
        return []

    ########################################################################
    # 获取上家出牌
    def get_up_play_cards(self):
        # 截取特定区域的屏幕图像并通过YOLO模型检测上家出的牌
        global Hwnd, up_cards_pos_region
        img = capture(Hwnd)
        img = img[up_cards_pos_region[0]:up_cards_pos_region[1],
              up_cards_pos_region[2]:up_cards_pos_region[3]]  # 截取上家出牌区域的图像
        _, class_list, pos_list, = yolo_detect(img)
        if class_list:
            class_list.sort()
            return class_list
        return []

    ########################################################################
    # 获取AI出牌
    def get_ai_play_cards(self):
        # 截取特定区域的屏幕图像并通过YOLO模型检测AI出的牌
        global Hwnd, ai_cards_pos_region
        img = capture(Hwnd)
        img = img[ai_cards_pos_region[0]:ai_cards_pos_region[1],
              ai_cards_pos_region[2]:ai_cards_pos_region[3]]  # 截取AI出牌区域的图像
        _, class_list, pos_list, = yolo_detect(img)
        if class_list:
            class_list.sort()
            return class_list
        return []

    ########################################################################
    # 识别AI扮演的角色
    def find_landlord(self):
        # 通过图像匹配确定AI扮演的角色（地主、地主上家、地主下家）
        sourec_pic = capture(Hwnd)
        items = []
        items.append(landlord1)
        items.append(landlord2)
        # ... (省略了其他的图片添加代码)

        for i in items:
            pos = ac.find_template(im_source=sourec_pic, im_search=i, threshold=0.8, rgb=True)
            if pos:
                cv2.rectangle(sourec_pic, pos['rectangle'][0], pos['rectangle'][3], [0, 0, 255], 2)
                ret = pos['result']
                x, y = ret
                if x < 640 and y < 360:
                    self.user_position_code = "地主下家"
                    self.Signal_up_msg.emit("Ai角色【地主下家】")
                    return 'landlord_down'
                elif x > 640:
                    self.Signal_up_msg.emit("Ai角色【地主上家】")
                    self.user_position_code = "地主上家"
                    return 'landlord_up'
                elif y > 400:
                    self.Signal_up_msg.emit("Ai角色【地主】")
                    self.user_position_code = "地主"
                    return 'landlord'
        return False

    ########################################################################
    # 检查出牌区域是不是有牌（白色）
    def check_white(self, s='left'):
        # 检查出牌区域是否有牌，根据白色像素的分布来判定
        image = capture(Hwnd)
        if s == "left":
            image = image[up_cards_pos_region[0]:up_cards_pos_region[1], up_cards_pos_region[2]:up_cards_pos_region[3]]
        elif s == "right":
            image = image[down_cards_pos_region[0]:down_cards_pos_region[1],
                    down_cards_pos_region[2]:down_cards_pos_region[3]]

        card_items = []
        card_items.append(play_flag1)
        # ... (省略了其他的图片添加代码)

        for item in card_items:
            pos = ac.find_template(im_source=image, im_search=item, threshold=0.8, rgb=True)
            if pos:
                return True
        return False