#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import numpy as np
import re

import firebase_admin
from firebase_admin import credentials, firestore


def format_hsv_numeric(hsv):
    """
    <OpenCV>
    H: 0~179 <= (360)*0.5
    S: 0~255 <= (100)*2.55
    V: 0~255 <= (100)*2.55
    <mmin and max HSV>
    Hue: ±8 (OpenCV: ±4)
    Saturation: ±10.1960...(OpenCV: ±26)
    Value: ±5.0980... (OpenCV: ±13)
    <補足>
    Hueの領域が179を超える値となる場合、hsv_minとhsv_macをそれぞれ２つ返す
    """
    hsv = re.findall(r'\d+', hsv)
    # format_hsv_numeric as for OprnCV
    h = math.ceil(int(hsv[0]) * 0.5)
    s = math.ceil(int(hsv[1]) * 2.55)
    v = math.ceil(int(hsv[2]) * 2.55)

    s_min = s - 26 
    if s_min < 0: 
        s_min = 0

    s_max = s + 26
    if s_max > 255:
        s_max = 255

    v_min = v - 13
    if v_min < 0:
        v_min = 0

    v_max = v + 13
    if v_max > 255: 
        v_max = 255

    h_min = h - 4
    if h_min < 0:
        h_min = 0

    h_max = h + 4

    if h_max > 179: # <補足参照>
        hsv1_min_array = [h_min, s_min, v_min]
        hsv1_max_array = [179, s_max, v_max]

        h_max -= 179
        hsv2_min_array = [0, s_min, v_min]
        hsv2_max_array = [h_max, s_max, v_max]

        ret = [np.array(hsv1_min_array), np.array(hsv1_max_array), np.array(hsv2_min_array), np.array(hsv2_max_array)]
    else:
        hsv_min_array = [h_min, s_min, v_min]
        hsv_max_array = [h_max, s_max, v_max]

        ret = [np.array(hsv_min_array), np.array(hsv_max_array)]

    return ret


def conver_hyphen_to_comma(hsv):
        hsv = re.findall(r'\d+', hsv)
        h = int(hsv[0])
        s = int(hsv[1])
        v = int(hsv[2])
        ret = np.array([h, s, v])

        return ret

class ColorSchemeStorage:
    cred = credentials.Certificate("./coual-cefec-firebase-adminsdk-uv5bf-38b2fb2901.json") # ダウンロードした秘密鍵
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    keys_to_analyze_color_lst = []
    neg_pattern_lst = []

    @classmethod
    def post_color_scheme(cls, base_hsv, base_color_name, pattern_stat, accent_hsv, accent_color_name):
        """配色パターンをDBにPOSTする / DBはCloud-Firestore"""
        parent_ref = cls.db.collection('color-schemes').document(base_hsv)
        children_ref = parent_ref.collection(pattern_stat).document(accent_hsv)
        children_ref.set({
            'base-color': base_color_name,
            'accent-color': accent_color_name,
        })

    @classmethod
    def get_keys_to_analyze_color(cls):
        """
        DBから取得したベースカラーの検索キーを格納した配列を生成
        配列1番目: ベースカラーの元の値
        配列2番目: ベースカラーをHSV空間の領域指定した値
        配列3番目: ベースカラーをHSV空間の領域指定した値で2番目の配列で格納したHueの値が359を超えた場合に生成
        """
        color_schemes_ref = cls.db.collection('color-schemes')
        main_docs = color_schemes_ref.get()
        cnt = 0
        for main_doc in main_docs:
            cnt += 1
            expand_base_colors = format_hsv_numeric(main_doc.id)
            neg_ref = color_schemes_ref.document(main_doc.id).collection('negative').get()
            neg_pattern_lst = []
            for neg_pattern in neg_ref:
                format_neg_pattern = format_hsv_numeric(neg_pattern.id)
                neg_pattern_lst.append(format_neg_pattern)

            pos_ref = color_schemes_ref.document(main_doc.id).collection('positive').get()
            pos_pattern_lst = []
            for pos_pattern in pos_ref:
                format_pos_pattern = format_hsv_numeric(pos_pattern.id)
                pos_pattern_lst.append(format_pos_pattern)

            format_base_color = conver_hyphen_to_comma(main_doc.id)
            keys_to_analyze_color = {"base_color":format_base_color, "expand_base_color":expand_base_colors, "neg_pattern_lst": neg_pattern_lst, "pos_pattern_lst": pos_pattern_lst}
            cls.keys_to_analyze_color_lst.append(keys_to_analyze_color)

        return cls.keys_to_analyze_color_lst

    @classmethod
    def storage_keys_to_analyze_color(cls):
        """get_keys_to_analyze_color()で毎回Cloud-Firestoreにアクセスするのは時間がかかるので、取得した値をクラス変数として常にアクセスできる状態で生成"""
        return cls.keys_to_analyze_color_lst


# # メインコレクションから親ドキュメントを取得
# colors_ref = db.collection('colors-scheme')
# main_docs = colors_ref.get()

# parent_docs = []
# print("\n\n=======ドキュメント(base_color)========")
# for main_doc in main_docs:
#     parent_docs.append(main_doc.id)
#     print(main_doc.id)


# print("\n\n=======サブコレクション(negative)========")
# for parent_doc in parent_docs:
#     bad_ref = colors_ref.document(parent_doc).collection('negative')
#     bad_docs = bad_ref.get()
#     print("\nドキュメントのID(base_color): {} ".format(parent_doc))
#     for bad_doc in bad_docs:
#         print("accent_color=> {}".format(bad_doc.id))
