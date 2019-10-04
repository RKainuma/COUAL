#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np


class Color(): 

    AREA_RATIO_THRESHOLD = 0.005

    @classmethod
    def read_input_image(cls, img):
        # print(img)
        # inputImg = cv2.imread(img)
        # ret = cls.detect_red_color(inputImg)
        # ret = cls.detect_blue_color(inputImg)
        ret = cls.detect_green_color(img)
        if ret is not None:
            cv2.circle(img, ret, 10, (0,0,0
                ),-1)
        cv2.imwrite("out.png", img)

    @classmethod
    def detect_red_color(cls, img):
        # HSV色空間に変換
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 赤色のHSVの値域1
        hsv_min = np.array([0,64,0])
        hsv_max = np.array([30,255,255])
        mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

        # 赤色のHSVの値域2
        hsv_min = np.array([150,64,0])
        hsv_max = np.array([179,255,255])
        mask2 = cv2.inRange(hsv, hsv_min, hsv_max)

        # 赤色領域のマスク（255：赤色、0：赤色以外
        mask = mask1 + mask2

        # マスキング処理
        masked_img = cv2.bitwise_and(img, img, mask=mask)

        return mask, masked_img

    @classmethod
    def detect_green_color(cls, img):
        h,w,c = img.shape
        # HSV色空間に変換
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

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
            # 見つからなかったらNoneを返す
            print("the area is too small")
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
        # HSV色空間に変換
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 青色のHSVの値域1
        hsv_min = np.array([90, 64, 0])
        hsv_max = np.array([150,255,255])

        # 青色領域のマスク（255：赤色、0：赤色以外）    
        mask = cv2.inRange(hsv, hsv_min, hsv_max)

        # マスキング処理
        masked_img = cv2.bitwise_and(img, img, mask=mask)
     
        return mask, masked_img


# if __name__ == '__main__':
#   imgSrc = "/Users/rkainuma/Desktop/colorSam/redHatake.jpg"
#   main(imgSrc)

