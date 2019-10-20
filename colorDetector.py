#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import json

from image_processors import rgb_to_hsv



class Color: 

    AREA_RATION_THRESHOLD = 0.01
    h = None
    s = None
    v = None
    hsv = None
    hsv_min1_array = [0,190,180]
    hsv_max1_array = [15,255,220]
    hsv_min2_array = [165,190,180]
    hsv_max2_array = [179,255,220]
    img_info={}
    vsize = 16
    hsize = 16
    vertical_divisions = 0
    side_divisions = 0

    @classmethod
    def exist_warning_coler(cls, target_img):
        cls.h, cls.w, cls.c = target_img.shape
        cls.hsv = rgb_to_hsv(target_img)
        target_positon = cls.detect_red_color()
        if target_positon is None:
            return False
        else:
            return True

    @classmethod
    def analyse(cls, target_img):
        vertical_divisions, side_divisions, sliced_imgs, message = cls.slice_and_detect_image(target_img)
        return cls.merge_image(vertical_divisions, side_divisions, sliced_imgs), message

    @classmethod
    def slice_and_detect_image(cls, target_img):
        selected_img_height, selected_img_wide = target_img.shape[:2]  # 画像の大きさ
        vertical_divisions, side_divisions = np.floor_divide([selected_img_height, selected_img_wide], [cls.vsize, cls.hsize])  # 分割数

        # 均等に分割できないと np.spllt() が使えないので、除算したときに余りがでないように画像の端数を切り捨てる。
        crop_img = target_img[:vertical_divisions * cls.vsize, :side_divisions * cls.hsize]
        # 分割する。
        sliced_imgs = []
        message = '画像に問題はありません。'
        for h_img in np.vsplit(crop_img, vertical_divisions):  # 垂直方向に分割する。
            for v_img in np.hsplit(h_img, side_divisions):  # 水平方向に分割する。
                if(cls.exist_warning_coler(v_img)):
                    v_img = cv2.rectangle(v_img, (0, 0), (cls.vsize, cls.hsize), (255, 0, 0), 3, 4)
                    message = cls.generate_message()
                sliced_imgs.append(v_img)
        sliced_imgs = np.array(sliced_imgs)
        return vertical_divisions, side_divisions, sliced_imgs, message
    
    @classmethod
    def merge_image(cls, vertical_divisions, side_divisions, sliced_imgs):
        marge_vsize, marge_hsize, ch = sliced_imgs.shape[1:]
        split_imgs = sliced_imgs.reshape(vertical_divisions, side_divisions, marge_vsize, marge_hsize, ch)
        return np.vstack([np.hstack(h_imgs) for h_imgs in split_imgs])

    @classmethod
    def detect_red_color(cls):
        # 赤色のHSVの値域
        ex_img = cv2.inRange(cls.hsv, np.array(cls.hsv_min1_array), np.array(cls.hsv_max1_array)) + cv2.inRange(cls.hsv, np.array(cls.hsv_min2_array), np.array(cls.hsv_max2_array))

        # 輪郭抽出
        contours,hierarchy = cv2.findContours(ex_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        # 面積を計算
        areas = np.array(list(map(cv2.contourArea, contours)))

        if len(areas) == 0 or np.max(areas) / (cls.h*cls.w) < cls.AREA_RATION_THRESHOLD:

            return None

        else:
            # 赤色空間の中心座標を取得
            target_areas = np.nonzero(areas)
            lst=[]
            for idx in target_areas[0]:
                result = cv2.moments(contours[idx])
                x = int(result["m10"]/result["m00"])
                y = int(result["m01"]/result["m00"])
                lst.append((x,y))

            return lst
    
    @classmethod
    def generate_message(cls):
        return 'HSV[' + ','.join(map(str, cls.hsv_min2_array)) + '~' + ','.join(map(str, cls.hsv_max1_array)) + ']の色が含まれています。'
