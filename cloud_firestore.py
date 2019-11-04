#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import re

import firebase_admin
from firebase_admin import credentials, firestore


cred = credentials.Certificate("./coual-cefec-firebase-adminsdk-uv5bf-38b2fb2901.json") # ダウンロードした秘密鍵
firebase_admin.initialize_app(cred)

db = firestore.client()

def post_color_scheme(base_hsv, base_color_name, pattern_stat, accent_hsv, accent_color_name):
    # print("base_hsv=>{}".format(base_hsv))
    # print("base_color_name=>{}".format(base_color_name))
    # print("pattern_stat=>{}".format(pattern_stat))
    # print("accent_hsv=>{}".format(accent_hsv))
    # print("accent_color_name=>{}".format(accent_color_name))
    parent_ref = db.collection('color-schemes').document(base_hsv)
    children_ref = parent_ref.collection(pattern_stat).document(accent_hsv)
    children_ref.set({
        'base-color': base_color_name,
        'accent-color': accent_color_name,
    })


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
        hsv1_min_array = (h_min, s_min, v_min)
        hsv1_max_array = (179, s_max, v_max)

        h_max -= 179
        hsv2_min_array = (0, s_min, v_min)
        hsv2_max_array = (h_max, s_max, v_max)

        ret = [hsv1_min_array, hsv1_max_array, hsv2_min_array, hsv2_max_array]

    else:
        hsv_min_array = [h_min, s_min, v_min]
        hsv_max_array = [h_max, s_max, v_max]

        ret = [hsv_min_array, hsv_max_array]



# # colors コレクションからドキュメントを取得
# colors_ref = db.collection('colors')
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

