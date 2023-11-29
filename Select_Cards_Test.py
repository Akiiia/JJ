
import cv2
import numpy as np
from capture import capture
import win32gui,win32con,win32api
from yolo import yolo_detect
import time
import random
Hwnd = 197166

card1 = cv2.imdecode(np.fromfile( "./pic/card1.bmp", dtype=np.uint8), -1)
card2 = cv2.imdecode(np.fromfile( "./pic/card2.bmp", dtype=np.uint8), -1)
card3 = cv2.imdecode(np.fromfile( "./pic/card3.bmp", dtype=np.uint8), -1)
card4 = cv2.imdecode(np.fromfile( "./pic/card4.bmp", dtype=np.uint8), -1)
card5 = cv2.imdecode(np.fromfile( "./pic/card5.bmp", dtype=np.uint8), -1)
card6 = cv2.imdecode(np.fromfile( "./pic/card6.bmp", dtype=np.uint8), -1)

card_items = []
card_items.append(card1)
card_items.append(card2)
card_items.append(card3)
card_items.append(card4)
card_items.append(card5)
card_items.append(card6)


def doClick(cx,cy):
    global Hwnd
    long_position = win32api.MAKELONG(int(cx), int(cy))#模拟鼠标指针 传送到指定坐标
    win32api.SendMessage(Hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)#模拟鼠标按下
    time.sleep(0.01)
    win32api.SendMessage(Hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)#模拟鼠标弹起

def find_closest_number(num, lst):
    closest = lst[0]
    diff = abs(num - closest)
    for i in range(1, len(lst)):
        if abs(num - lst[i]) < diff:
            closest = lst[i]
            diff = abs(num - closest)
    if abs(num - closest) > 10:
        #距离较远
        return True
    else:
        return False

def seleck_cards(cards):
    global Hwnd
    position_list = [0]
    for i in range(random.randint(2,4)):
        doClick(random.randint(520,750),random.randint(160,340))
        time.sleep(0.05)
    time.sleep(0.05)
    _,class_list, pos_list,= yolo_detect(capture(Hwnd))  
    min_value = min([sub_list[1] for sub_list in pos_list])-10
    print("min_value:",min_value)

    for card in cards:#待选的牌
        _,class_list, pos_list,= yolo_detect(capture(Hwnd))  
        for c,p in zip(class_list, pos_list):
            if c != card:
                continue
            if c == card and p[1] >= min_value and find_closest_number(p[0],position_list):
                doClick(p[0]+20,p[1]+50)
                time.sleep(0.1)
                position_list.append(p[0])
                break
            elif c == card and p[1] < min_value and find_closest_number(p[0],position_list):
                position_list.append(p[0])
                break
        time.sleep(0.1)
    time.sleep(0.1)
    
    _,class_list, pos_list,= yolo_detect(capture(Hwnd))  
    for c,p in zip(class_list, pos_list):
        if p[1] < min_value and find_closest_number(p[0],position_list):
            print(c,p)
            doClick(p[0]+20,p[1]+50)
            time.sleep(0.1)



#seleck_cards('34567')

seleck_cards('JJJJ99')

