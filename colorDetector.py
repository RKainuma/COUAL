#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cv2
from itertools import combinations
import json
import numpy as np
import math
import os
import sys
from timeit import default_timer

# from cloud_firestore import ColorSchemeStorage
from color_diff import proceed_color_diff
from image_processors import hsv_to_bgr_tuple, rgb_to_hsv
from subtractive_color import execute


class Color:
    AREA_RATION_THRESHOLD = 0.01
    h = None
    s = None
    v = None
    hsv = None
    vsize = 20 #垂直方向の画像分割サイズ
    hsize = 20 #水平方向の画像分割サイズ
    vertical_divisions = 0 #垂直方向の画像分割数
    horizontal_divisions = 0 #水平方向の画像分割数
    need_generate_recommend_image = False

    @classmethod
    def get_confront_RGBs_lst(cls, inputImg):
        lshape= cls.vsize * cls.hsize
        reshaped_inputImg = np.reshape(inputImg, (lshape, 3))
        RGB_elements = []
        for elm in reshaped_inputImg:
            RGB_elements.append(elm.tolist())
        uniq_RGB_elements = Color.get_unique_list(RGB_elements)  # 色の重複を取り除いたリストを生成

        if len(uniq_RGB_elements) == 1:
            ret = False
        else:
            confront_RGBs_list = list(combinations(uniq_RGB_elements, 2))  # 総当たり組み合わせができるように、tupleを生成
            ret = confront_RGBs_list

        return ret

    @staticmethod
    def get_unique_list(seq):
        """重複している要素を削除してユニーク化する処理 / 要素がリスト型の場合に使用する処理"""
        seen = []
        return [x for x in seq if x not in seen and not seen.append(x)]

    @classmethod
    def exist_warning_color(cls, img):
        target_img = execute(img)
        cls.h, cls.w, cls.c = target_img.shape
        cls.hsv = rgb_to_hsv(target_img)
        return cls.detect_warning_color()

    @classmethod
    def analyse_old(cls, target_img):
        vertical_divisions, horizontal_divisions, sliced_imgs, message = cls.slice_and_detect_image(target_img)
        if (cls.need_generate_recommend_image) :
            merged_img = cls.merge_image(vertical_divisions, horizontal_divisions, sliced_imgs)
            recommend_img = cls.generate_recommend_image()
            return merged_img, merged_img, message
        else :
            merged_img = cls.merge_image(vertical_divisions, horizontal_divisions, sliced_imgs)
            return merged_img, message

    # 速度検証用で実際の処理には使わない
    @classmethod
    def split_img(cls, target_img):
        imgRGB = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)
        h, w, *args = imgRGB.shape[:3]
        v_split, h_split = np.floor_divide([h, w], [cls.vsize, cls.hsize])
        _imgRGB = imgRGB[:h // v_split * v_split, :w // h_split * h_split]
        for h_img in np.vsplit(_imgRGB, v_split):  # Y軸方向に分割する
            for v_img in np.hsplit(h_img, h_split):  # X軸方向に分割する
                yield v_img

    @classmethod
    def analyze_img(cls, imgBGR, is_scan=True):
        imgRGB = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2RGB)
        cnt = 0
        if is_scan:
            img_generator = cls.scan_img(imgRGB)
        else:
            img_generator = cls.split_img(imgRGB)

        for roi in img_generator:
            confront_RGBs_lst = cls.get_confront_RGBs_lst(roi)
            if confront_RGBs_lst is False:
                pass
            else:
                for confront_RGBs in confront_RGBs_lst:
                    RGB1, RGB2 = confront_RGBs[0], confront_RGBs[1]
                    warning = proceed_color_diff(RGB1, RGB2)
            cnt+=1

        return cnt

    # 画像を走査する // ジェネレータとしてroiを出力
    @classmethod
    def scan_img(cls, imgRGB):
        h, w, *args = imgRGB.shape[:3]
        # x_step = int(h/math.floor(w / 20))  # x軸への移動回数を20pxごとの処理を元に設定　FIXME: こちらの方がより細かい範囲をチェックできる
        # y_step = int(w/math.floor(h / 20))  # yへの移動回数を20pxごとの処理を元に設定　FIXME: こちらの方がより細かい範囲をチェックできる
        x_step = cls.hsize  # x軸へ20pxごとに処理
        y_step = cls.vsize  # y軸へ20pxごとに処理
        x0 = 0  # x軸への処理におけ初期位置
        y0 = 0  # x軸への処理におけ初期位置
        j = 0

        # Y軸歩行へのループ
        while y_step + (j * y_step) < h:
            i = 0
            ys = y0 + (j * y_step)
            yf = y_step + (j * y_step)

            # X軸歩行へのループ
            while x_step + (i * x_step) < w:
                roi = imgRGB[ys:yf, x0 + (i * x_step):x_step + (i * x_step)]  # 元画像から領域をroiで抽出
                yield roi
                i = i + 1
            j = j + 1

    @classmethod
    def slice_and_detect_image_old(cls, target_img):
        selected_img_height, selected_img_wide = target_img.shape[:2]  # 画像の大きさ
        vertical_divisions, horizontal_divisions = np.floor_divide([selected_img_height, selected_img_wide], [cls.vsize, cls.hsize])

        # 均等に分割できないと np.spllt() が使えないので、除算したときに余りがでないように画像の端数を切り捨てる。
        crop_img = target_img[:vertical_divisions * cls.vsize, :horizontal_divisions * cls.hsize]
        # 分割する。
        sliced_imgs = []
        message = '画像に問題はありません。'
        s = default_timer()
        for h_img in np.vsplit(crop_img, vertical_divisions):  # 垂直方向に分割する。
            for v_img in np.hsplit(h_img, horizontal_divisions):  # 水平方向に分割する。
                confront_RGBs_lst = cls.get_confront_RGBs_lst(v_img)
                if confront_RGBs_lst is False:  # 16px*16pxの中で１色のみの場合はpass
                    pass
                else:
                    for confront_RGBs in confront_RGBs_lst:
                        RGB1, RGB2 = confront_RGBs[0], confront_RGBs[1]

                        warning = proceed_color_diff(RGB1, RGB2)
                        if warning:
                            v_img = cv2.rectangle(v_img, (0, 0), (cls.vsize, cls.hsize), (180, 54, 142), 2, 4)
                        sliced_imgs.append(v_img)
        e = default_timer() - s
        print(e)
        print("========>>>>>計測終了 // 処理時間: {}".format(e))
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
            for e in each['neg_pattern_lst']:
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='分割して処理を処理をする画像のファイルパスを指定する')
    parser.add_argument("image", help='Add file path.')
    parser.add_argument("--split", action="store_true", default=False, help='This is split mode.')
    args = parser.parse_args()

    if os.path.exists(args.image): 
        IMG = args.image
    else: 
        raise FileNotFoundError("Add correct file path")

    if args.split:
        method = "SPLIT"
        is_scan = False
    else:
        method = "SCAN"
        is_scan = True

    imgBGR = cv2.imread(IMG)
    Color = Color()
    s = default_timer()
    cnt = Color.analyze_img(imgBGR, is_scan)
    e = default_timer() - s

    print("\n=====================================")
    print("Called method: \033[34m {} \033[0m".format(method))
    print("Process time: \033[32m  {}s \033[0m".format(e))
    print("Process times: \033[31m {} \033[0m".format(cnt))
    print("=====================================\n")
