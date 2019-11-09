#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import json
import numpy as np
import matplotlib.pyplot as plt

from image_processors import rgb_to_hsv
from subtractive_color import execute

class Color: 

    AREA_RATION_THRESHOLD = 0.01
    h = None
    s = None
    v = None
    hsv = None
    hsv_min1_array = [0,130,130]
    hsv_max1_array = [15,255,255]
    hsv_min2_array = [165,130,130]
    hsv_max2_array = [179,255,255]
    hsv_min_green_array = [15,130,130]
    hsv_max_green_array = [90,255,255]
    vsize = 16 #垂直方向の画像分割サイズ
    hsize = 16 #水平方向の画像分割サイズ
    vertical_divisions = 0 #垂直方向の画像分割数
    horizontal_divisions = 0 #水平方向の画像分割数
    need_generate_recommend_image = False

    @classmethod
    def exist_warning_coler(cls, img):
        target_img = execute(img)
        cls.h, cls.w, cls.c = target_img.shape
        cls.hsv = rgb_to_hsv(target_img)
        return cls.detect_red_color()

    @classmethod
    def analyse(cls, target_img):
        vertical_divisions, horizontal_divisions, sliced_imgs, message = cls.slice_and_detect_image(target_img)
        if (cls.need_generate_recommend_image) :
            merged_img = cls.merge_image(vertical_divisions, horizontal_divisions, sliced_imgs)
            recommend_img = cls.generate_recommend_image()
            return merged_img, merged_img, message
        else :
            merged_img = cls.merge_image(vertical_divisions, horizontal_divisions, sliced_imgs)
            return merged_img, message

    @classmethod
    def slice_and_detect_image(cls, target_img):
        selected_img_height, selected_img_wide = target_img.shape[:2]  # 画像の大きさ
        vertical_divisions, horizontal_divisions = np.floor_divide([selected_img_height, selected_img_wide], [cls.vsize, cls.hsize])

        # 均等に分割できないと np.spllt() が使えないので、除算したときに余りがでないように画像の端数を切り捨てる。
        crop_img = target_img[:vertical_divisions * cls.vsize, :horizontal_divisions * cls.hsize]
        # 分割する。
        sliced_imgs = []
        message = '画像に問題はありません。'
        for h_img in np.vsplit(crop_img, vertical_divisions):  # 垂直方向に分割する。
            for v_img in np.hsplit(h_img, horizontal_divisions):  # 水平方向に分割する。
                if(cls.exist_warning_coler(v_img)):
                    v_img = cv2.rectangle(v_img, (0, 0), (cls.vsize, cls.hsize), (255, 255, 0), 2, 4)
                    message = cls.generate_message()
                sliced_imgs.append(v_img)
        sliced_imgs = np.array(sliced_imgs)
        return vertical_divisions, horizontal_divisions, sliced_imgs, message
    
    @classmethod
    def merge_image(cls, vertical_divisions, horizontal_divisions, sliced_imgs):
        marge_vsize, marge_hsize, ch = sliced_imgs.shape[1:]
        split_imgs = sliced_imgs.reshape(vertical_divisions, horizontal_divisions, marge_vsize, marge_hsize, ch)
        return np.vstack([np.hstack(h_imgs) for h_imgs in split_imgs])

    @classmethod
    def generate_recommend_image(cls, vertical_divisions, horizontal_divisions, sliced_imgs):
        return np.vstack([np.hstack(h_imgs) for h_imgs in split_imgs])

    @classmethod
    def detect_red_color(cls):
        # 赤色のHSVの値域
        ex_img_red = cv2.inRange(cls.hsv, np.array(cls.hsv_min1_array), np.array(cls.hsv_max1_array)) + cv2.inRange(cls.hsv, np.array(cls.hsv_min2_array), np.array(cls.hsv_max2_array))
        # 緑色のHSVの値域
        ex_img_green = cv2.inRange(cls.hsv, np.array(cls.hsv_min_green_array), np.array(cls.hsv_max_green_array))

        # 輪郭抽出
        contours_red,hierarchy_red = cv2.findContours(ex_img_red, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        contours_green,hierarchy_green = cv2.findContours(ex_img_green, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        # 面積を計算
        red_areas = np.array(list(map(cv2.contourArea, contours_red)))
        green_areas = np.array(list(map(cv2.contourArea, contours_green)))

        if len(red_areas) == 0 or np.max(red_areas) / (cls.h*cls.w) < cls.AREA_RATION_THRESHOLD:
            return False
        elif len(green_areas) == 0 or np.max(green_areas) / (cls.h*cls.w) < cls.AREA_RATION_THRESHOLD:
            return False
        else:
            return True
    
    @classmethod
    def generate_message(cls):
        return 'HSV[' + ','.join(map(str, cls.hsv_min2_array)) + '~' + ','.join(map(str, cls.hsv_max1_array)) + ']の色が含まれています。'

