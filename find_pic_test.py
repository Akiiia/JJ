import aircv as ac
from capture import capture
import cv2
import numpy as np
import win32gui

hwnd = 131924



wait_flag = cv2.imdecode(np.fromfile( "./pic/play_flag.bmp", dtype=np.uint8), -1)



def pic_find_template():
    while True:
        sourec_pic = capture(hwnd)
        #sourec_pic = cv2.imread(r"C:\Users\Administrator\Documents\leidian64\Pictures\Screenshots\26.png")
        pos = ac.find_template(im_source = sourec_pic,im_search = wait_flag,threshold = 0.86,rgb=True)
        if pos:
            print(pos['result'])
            cv2.rectangle(sourec_pic, pos['rectangle'][0],pos['rectangle'][3], [0,0,255], 2)
            ret = pos['result']


        cv2.imshow('sourec_pic',sourec_pic)
        cv2.waitKey(25)


def find_all_template():
    while True:
        sourec_pic = capture(hwnd)
        items = ac.find_all_template(im_source = sourec_pic,im_search = wait_flag,threshold = 0.95,rgb=True)
        if items:
            for pos in items:
                print(pos['result'])
                cv2.rectangle(sourec_pic, pos['rectangle'][0],pos['rectangle'][3], [0,0,255], 2)



        cv2.imshow('sourec_pic',sourec_pic)
        cv2.waitKey(25)

find_all_template()