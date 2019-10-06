#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np

from image_processors import rgb_to_hsv



class Color(): 

    AREA_RATIO_THRESHOLD = 0.005

    @classmethod
    def read_input_image(cls, target_img):
        target_positon = cls.detect_red_color(target_img)
        if target_positon is None:
            print("Could not detect red")
        else:
            target_img = cv2.circle(target_img, target_positon, 10, (0, 0, 0), -1)
            target_img = cv2.putText(target_img, 'Found Red', target_positon, cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 5, cv2.LINE_AA)

        target_positon = cls.detect_green_color(target_img)
        if target_positon is None:
            print("Could not detect green")
        else:
            target_img = cv2.circle(target_img, target_positon, 10, (0, 0, 0), -1)
            target_img = cv2.putText(target_img, 'Found Green', target_positon, cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 5, cv2.LINE_AA)

        target_positon = cls.detect_blue_color(target_img)
        if target_positon is None:
            print("Could not detect blue")
        else:
            target_img = cv2.circle(target_img, target_positon, 10, (0, 0, 0), -1)
            target_img = cv2.putText(target_img, 'Found Blue', target_positon, cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 5, cv2.LINE_AA)

        return target_img

    @classmethod
    def detect_red_color(cls, img):
        h,w,c = img.shape

        hsv = rgb_to_hsv(img)

        # 赤色のHSVの値域1
        hsv_min = np.array([0,64,0])
        hsv_max = np.array([30,255,255])
        ex_img1 = cv2.inRange(hsv, hsv_min, hsv_max)

        # 赤色のHSVの値域2
        hsv_min = np.array([150,64,0])
        hsv_max = np.array([179,255,255])
        ex_img2 = cv2.inRange(hsv, hsv_min, hsv_max)

        ex_img = ex_img1 + ex_img2

        # 輪郭抽出
        contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        # 面積を計算
        areas = np.array(list(map(cv2.contourArea,contours)))

        if len(areas) == 0 or np.max(areas) / (h*w) < cls.AREA_RATIO_THRESHOLD:

            return None

        else:
            # 面積が最大の塊の重心を計算し返す
            max_idx = np.argmax(areas)
            max_area = areas[max_idx]
            result = cv2.moments(contours[max_idx])
            x = int(result["m10"]/result["m00"])
            y = int(result["m01"]/result["m00"])

            return (x,y)


    @classmethod
    def detect_green_color(cls, img):
        h,w,c = img.shape

        hsv = rgb_to_hsv(img)

        # 緑色のHSVの値域1
        hsv_min = np.array([30, 64, 0])
        hsv_max = np.array([90,255,255])

        # 緑色領域のマスク（255：赤色、0：赤色以外）    
        ex_img = cv2.inRange(hsv, hsv_min, hsv_max)
        
        # 輪郭抽出
        contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        # 面積を計算
        areas = np.array(list(map(cv2.contourArea,contours)))

        if len(areas) == 0 or np.max(areas) / (h*w) < cls.AREA_RATIO_THRESHOLD:

            return None

        else:
            # 面積が最大の塊の重心を計算し返す
            max_idx = np.argmax(areas)
            max_area = areas[max_idx]
            result = cv2.moments(contours[max_idx])
            x = int(result["m10"]/result["m00"])
            y = int(result["m01"]/result["m00"])

            return (x,y)

    @classmethod
    def detect_blue_color(cls, img):
        h,w,c = img.shape
        
        hsv = rgb_to_hsv(img)

        # 青色のHSVの値域1
        hsv_min = np.array([90, 64, 0])
        hsv_max = np.array([150,255,255])

        # 青色領域のマスク（255：赤色、0：赤色以外）    
        ex_img = cv2.inRange(hsv, hsv_min, hsv_max)

        # 輪郭抽出
        contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        # 面積を計算
        areas = np.array(list(map(cv2.contourArea,contours)))

        if len(areas) == 0 or np.max(areas) / (h*w) < cls.AREA_RATIO_THRESHOLD:

            return None

        else:
            # 面積が最大の塊の重心を計算し返す
            max_idx = np.argmax(areas)
            max_area = areas[max_idx]
            result = cv2.moments(contours[max_idx])
            x = int(result["m10"]/result["m00"])
            y = int(result["m01"]/result["m00"])

            return (x,y)
