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
    img_info={}

    @classmethod
    def read_input_image(cls, target_img):
        cls.h, cls.w, cls.c = target_img.shape
        cls.hsv = rgb_to_hsv(target_img)
        target_positon = cls.detect_red_color()
        # print(target_positon)
        if target_positon is None:
            print("Could not detect red")
        else:
            put_num=1
            target_positon.reverse()
            for t_p in target_positon:
                # target_img = cv2.circle(target_img, t_p, 10, (0, 0, 0), 1)
                target_img = cv2.putText(target_img, str(put_num), t_p, cv2.FONT_HERSHEY_PLAIN, 2, (167, 87, 168), 2, cv2.LINE_AA)
                cls.img_info[put_num] = "red"
                # print("num{} is red".format(put_num))
                put_num+=1
        
        # target_positon = cls.detect_green_color()
        # if target_positon is None:
        #     print("Could not detect green")
        # else:
        #     target_img = cv2.circle(target_img, target_positon, 10, (0, 0, 0), -1)
        #     target_img = cv2.putText(target_img, 'Found Green', target_positon, cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 5, cv2.LINE_AA)

        # target_positon = cls.detect_blue_color()
        # if target_positon is None:
        #     print("Could not detect blue")
        # else:
        #     target_img = cv2.circle(target_img, target_positon, 10, (0, 0, 0), -1)
        #     target_img = cv2.putText(target_img, 'xound Blue', target_positon, cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 5, cv2.LINE_AA)

        data_json = json.dumps(cls.img_info)
        return target_img, data_json

    @classmethod
    def detect_red_color(cls):
        # 赤色のHSVの値域1
        hsv_min = np.array([0,190,180])
        hsv_max = np.array([15,255,220])
        ex_img1 = cv2.inRange(cls.hsv, hsv_min, hsv_max)

        # 赤色のHSVの値域2
        hsv_min = np.array([165,190,180])
        hsv_max = np.array([179,255,220])
        ex_img2 = cv2.inRange(cls.hsv, hsv_min, hsv_max)

        ex_img = ex_img1 + ex_img2

        # 輪郭抽出
        contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        # 面積を計算
        areas = np.array(list(map(cv2.contourArea,contours)))

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

    # NOTE: HSV色空間での緑色の抽出 / 緑色抽出時に使用
    # @classmethod
    # def detect_green_color(cls):
    #     # 緑色のHSVの値域1
    #     hsv_min = np.array([30, 64, 0])
    #     hsv_max = np.array([90,255,255])

    #     # 緑色領域のマスク（255：赤色、0：赤色以外）    
    #     ex_img = cv2.inRange(cls.hsv, hsv_min, hsv_max)
        
    #     # 輪郭抽出
    #     contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    #     # 面積を計算
    #     areas = np.array(list(map(cv2.contourArea,contours)))

    #     if len(areas) == 0 or np.max(areas) / (cls.h*cls.w) < cls.AREA_RATION_THRESHOLD:

    #         return None

    #     else:
    #         # 面積が最大の塊の重心を計算し返す
    #         max_idx = np.argmax(areas)
    #         max_area = areas[max_idx]
    #         result = cv2.moments(contours[max_idx])
    #         x = int(result["m10"]/result["m00"])
    #         y = int(result["m01"]/result["m00"])

    #         return (x,y)

    # HSV色空間での青色の抽出 / 青色抽出の際に使用
    # @classmethod
    # def detect_blue_color(cls):

    #     # 青色のHSVの値域1
    #     hsv_min = np.array([90, 64, 0])
    #     hsv_max = np.array([150,255,255])

    #     # 青色領域のマスク（255：赤色、0：赤色以外）    
    #     ex_img = cv2.inRange(cls.hsv, hsv_min, hsv_max)

    #     # 輪郭抽出
    #     contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    #     # 面積を計算
    #     areas = np.array(list(map(cv2.contourArea,contours)))

    #     if len(areas) == 0 or np.max(areas) / (cls.h*cls.w) < cls.AREA_RATION_THRESHOLD:

    #         return None

    #     else:
    #         # 面積が最大の塊の重心を計算し返す
    #         max_idx = np.argmax(areas)
    #         max_area = areas[max_idx]
    #         result = cv2.moments(contours[max_idx])
    #         x = int(result["m10"]/result["m00"])
    #         y = int(result["m01"]/result["m00"])

    #         return (x,y)
