#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
from capture import capture
import random
"""
图片的预处理及切割
"""


def clear_border(img):
  h, w = img.shape[:2]
  for y in range(0, w):
    for x in range(0, h):
      if y > w -20 or y < 1:#右方与左方一列
        img[x, y] = 255
      if x > h - 10:#下方
        img[x, y] = 255
  return img

def count_number(num_list, num):
    """
    统计一维数组中某个数字的个数
    :param num_list:
    :param num:
    :return: num的数量
    """
    t = 0
    for i in num_list:
        if i == num:
            t += 1
    return t


# 切割图片
def cut_vertical(img_list, c_value=255):
    """
    投影法竖直切割图片的数组
    :param img_list: 传入的数据为一个由（二维）图片构成的数组，不是单纯的图片
    :param c_value: 切割的值 c_value
    :return: 切割之后的图片的数组
    """
    # 如果传入的是一个普通的二值化的图片，则需要首先将这个二值化的图片升维为图片的数组
    if len(np.array(img_list).shape) == 2:
        img_list = img_list[None]
    r_list = []
    for img_i in img_list:
        end = 0
        for i in range(len(img_i.T)):
            if count_number(img_i.T[i], c_value) >= img_i.shape[0]:
                star = end
                end = i
                if end - star > 5:
                    r_list.append(img_i[:, star:end])
    return r_list

if __name__ =="__main__":
    n = 0
    while True:
        img = capture(196708)
        img_cut = img[158:184,40:80]
        #img_cut = img[158:184,1205:1245]

  
        im = cv2.resize(img_cut, None, fx=3, fy=2, interpolation=cv2.INTER_LINEAR)  # 放大图片
        im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)  # 图片灰度处理
        ret, im_inv = cv2.threshold(im_gray, 150, 255, cv2.THRESH_BINARY_INV)  # 将图片做二值化处理
        im_inv = clear_border(im_inv)  # 清除边缘噪点
      

        cv2.imshow('img_cut', img_cut)

        # 垂直分割投影法分割图片
        img_list = cut_vertical(im_inv)
        for i in img_list:
            im = cv2.resize(i, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)  # 放大图片
            cv2.imshow('cut', im)
            if cv2.waitKey(2000) & 0xFF == ord('1'):
                print('保存图片')
                cv2.imwrite('./temp/{}.bmp'.format(random.randint(0, 10000)), im)
                n = n + 1
                

        cv2.destroyAllWindows()







