#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import json
import numpy as np

from image_processors import rgb_to_hsv
from image_processors import hsv_to_bgr_tuple
from subtractive_color import execute
from cloud_firestore import ColorSchemeStorage

class Color: 

    AREA_RATION_THRESHOLD = 0.01
    h = None
    s = None
    v = None
    hsv = None
    vsize = 16 #垂直方向の画像分割サイズ
    hsize = 16 #水平方向の画像分割サイズ
    vertical_divisions = 0 #垂直方向の画像分割数
    horizontal_divisions = 0 #水平方向の画像分割数
    need_generate_recommend_image = False

    @classmethod
    def exist_warning_color(cls, img):
        target_img = execute(img)
        cls.h, cls.w, cls.c = target_img.shape
        cls.hsv = rgb_to_hsv(target_img)
        return cls.detect_warning_color()

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
                warning, positive_color_bgr = cls.exist_warning_color(v_img)
                if(warning):
                    print("(**********")
                    v_img = cv2.rectangle(v_img, (0, 0), (cls.vsize, cls.hsize), positive_color_bgr, 2, 4)
                    # message = cls.generate_message()
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
    def detect_warning_color(cls):
        # 分割された画像にbase colorが含まれているかチェックする
        for each in ColorSchemeStorage.storage_keys_to_analyze_color():
            expandBaseColorArray = each['expand_base_color']
            ex_img = None
            # HSVの最小値・最大値を2つずつ保持する可能性があるため
            if len(expandBaseColorArray) == 2 :
                ex_img = cv2.inRange(cls.hsv, expandBaseColorArray[0], expandBaseColorArray[1])
            else:
                ex_img = cv2.inRange(cls.hsv, expandBaseColorArray[0], expandBaseColorArray[1]) + cv2.inRange(cls.hsv, expandBaseColorArray[2], expandBaseColorArray[3])
            
            contours,hierarchy = cv2.findContours(ex_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            base_areas = np.array(list(map(cv2.contourArea, contours)))
            
            #base colorが存在しなければ後続の処理は実行しない
            if len(base_areas) == 0 or np.max(base_areas) / (cls.h*cls.w) < cls.AREA_RATION_THRESHOLD:
                continue
            
            #negative colorの存在チェック
            for e in each['neg_pattern_lst'] :
                n_ex_img = cv2.inRange(cls.hsv, e[0], e[1])
                n_contours,n_hierarchy = cv2.findContours(n_ex_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                negative_areas = np.array(list(map(cv2.contourArea, n_contours)))
                #negative colorが存在しなければ問題なし
                if len(negative_areas) == 0 or np.max(negative_areas) / (cls.h*cls.w) < cls.AREA_RATION_THRESHOLD:
                    continue
                
                positive_color_hsv = each['pos_pattern_lst'][0][0]
                return True, hsv_to_bgr_tuple(positive_color_hsv[0], positive_color_hsv[1], positive_color_hsv[2])
        return False, None
    
    @classmethod
    def generate_message(cls):
        return 'HSV[' + ','.join(map(str, cls.hsv_min2_array)) + '~' + ','.join(map(str, cls.hsv_max1_array)) + ']の色が含まれています。'

