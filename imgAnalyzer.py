#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cv2
import datetime
from itertools import combinations
import json
import numpy as np
import math
import os
import sys
from timeit import default_timer

# from cloud_firestore import ColorSchemeStorage
# from color_diff import proceed_color_diff # 古い方
from calc_CIEDE2000 import proceed_color_diff
from image_processors import hsv_to_bgr_tuple, rgb_to_hsv
from subtractive_color import execute


class ImgAnalyzer:
    vsize = 16  # 垂直方向の画像分割サイズ
    hsize = 16  # 水平方向の画像分割サイズ

    @classmethod
    def get_confront_RGBs_lst(cls, inputImg):
        """画像内に存在するRGBで総当たりの組み合わせを生成"""
        lshape= cls.vsize * cls.hsize
        reshaped_inputImg = np.reshape(inputImg, (lshape, 3))
        RGB_elements = []
        for elm in reshaped_inputImg:
            RGB_elements.append(elm.tolist())
        uniq_RGB_elements = ImgAnalyzer.get_unique_list(RGB_elements)

        if len(uniq_RGB_elements) == 1:
            ret = False
        else:
            confront_RGBs_list = list(combinations(uniq_RGB_elements, 2))
            ret = confront_RGBs_list

        return ret

    @classmethod
    def mark_as_rectangle(cls, target_img, rectangles):
        """座標情報を元に矩形を描画する"""
        for rectangle in rectangles:
            xmin, xmax, ymin, ymax = rectangle
            cv2.rectangle(target_img, (xmin, ymin), (xmax, ymax), (180, 54, 142), 1, 4)

        return target_img

    @staticmethod
    def get_unique_list(seq):
        """重複している要素を削除してユニーク化する処理 / 要素がリスト型の場合に使用する処理"""
        seen = []
        return [x for x in seq if x not in seen and not seen.append(x)]

    # 検証用
    @classmethod
    def split_img(cls, target_img):
        """画像を分割する // ジェネレータとしてroiを出力 // 速度検証用で実際の処理には使わない"""
        imgRGB = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)
        h, w, *args = imgRGB.shape[:3]
        v_split, h_split = np.floor_divide([h, w], [cls.vsize, cls.hsize])
        _imgRGB = imgRGB[:h // v_split * v_split, :w // h_split * h_split]
        for h_img in np.vsplit(_imgRGB, v_split):  # Y軸方向に分割する
            for v_img in np.hsplit(h_img, h_split):  # X軸方向に分割する
                yield v_img, False

    @classmethod
    def scan_img(cls, imgRGB):
        """画像を走査する // ジェネレータとしてroiを出力"""
        h, w, *args = imgRGB.shape[:3]
        x_step = cls.hsize  # x軸へ20pxごとに処理
        y_step = cls.vsize  # y軸へ20pxごとに処理
        x0 = 0  # x軸への処理におけ初期位置
        y0 = 0  # x軸への処理におけ初期位置
        j = 0

        # Y軸方向へのループ
        while y_step + (j * y_step) < h:
            i = 0
            ys = y0 + (j * y_step)
            yf = y_step + (j * y_step)

            # X軸方向へのループ
            while x_step + (i * x_step) < w:
                xmin, xmax, ymin, ymax = x0 + (i * x_step), x_step + (i * x_step), ys, yf
                rectangle = (xmin, xmax, ymin, ymax)
                roi = imgRGB[ymin:ymax, xmin:xmax]  # 元画像から領域をroiで抽出
                yield roi, rectangle
                i = i + 1
            j = j + 1

    @classmethod
    def analyze_img(cls, imgBGR):
        imgRGB = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2RGB)
        cnt = 0

        rectangles = []
        for img in cls.scan_img(imgRGB):
            roi, rectangle = img[0], img[1]
            confront_RGBs_lst = cls.get_confront_RGBs_lst(roi)
            if confront_RGBs_lst is False:
                pass
            else:
                for confront_RGBs in confront_RGBs_lst:
                    RGB1, RGB2 = confront_RGBs[0], confront_RGBs[1]

                    warning = proceed_color_diff(RGB1, RGB2)
                    if warning:
                        rectangles.append(rectangle)
                        break
                    else:
                        pass
            cnt+=1

        marked_imgRGB = cls.mark_as_rectangle(imgRGB, rectangles)

        return marked_imgRGB, cnt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='分割して処理を処理をする画像のファイルパスを指定する')
    parser.add_argument("image", help='Add file path.')
    parser.add_argument("--split", action="store_true", default=False, help='This is split mode.')
    parser.add_argument("--scan", action="store_true", default=False, help='This is scan mode.')
    args = parser.parse_args()

    if args.scan and args.split:
        raise NameError("\033[31m Choose --split or --scan \033[0m")
    else:
        pass

    if os.path.exists(args.image): 
        IMG = args.image
    else: 
        raise FileNotFoundError("\033[31m Add correct file path \033[0m")

    if args.split:
        method = "TEST-SPLIT"
        is_split = True
        is_SpeedTest = True
    elif args.scan:
        method = "TEST-SCAN"
        is_SpeedTest = True
        is_split = True
    else:
        method = "SCAN"
        is_SpeedTest = False

    imgBGR = cv2.imread(IMG)
    ImgAnalyzer = ImgAnalyzer()
    s = default_timer()

    if is_SpeedTest:
        imgRGB = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2RGB)
        if is_split:
            img_generator = ImgAnalyzer.split_img(imgRGB)
        else:
            img_generator = ImgAnalyzer.scan_img(imgRGB)
        cnt = 0
        for img in img_generator:
            roi, *args = img
            confront_RGBs_lst = ImgAnalyzer.get_confront_RGBs_lst(roi)
            if confront_RGBs_lst is False:
                pass
            else:
                for confront_RGBs in confront_RGBs_lst:
                    RGB1, RGB2 = confront_RGBs[0], confront_RGBs[1]
            cnt+=1

    else:
        result_imgRGB, cnt = ImgAnalyzer.analyze_img(imgBGR)
        result_imgBGR = cv2.cvtColor(result_imgRGB, cv2.COLOR_BGR2RGB)
        fname= "./out/out_{}.jpg".format(datetime.datetime.now())
        cv2.imwrite(fname, result_imgBGR)
    e = default_timer() - s

    print("\n=====================================")
    print("Called method: \033[34m {} \033[0m".format(method))
    print("Process time: \033[32m  {}s \033[0m".format(e))
    print("Process times: \033[31m {} \033[0m".format(cnt))
    print("=====================================\n")
