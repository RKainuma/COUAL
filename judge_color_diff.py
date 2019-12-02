#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cv2
import numpy as np
import sys


def RGB2XYZ(inputRGB):
    # RGB表色系をXYZ表色の単位に変換
    converted_RGB = []
    for elm in inputRGB:
        elm =elm / 255

        if elm > 0.04045:
            elm = np.power((elm + 0.055) / 1.055, 2.4)
        else:
            elm = elm / 12.92
        converted_RGB.append(elm)

    RGB2XYZ_conversion_factor = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) # RGB表色系からXYZ表色系への変換係数
    converted_RGB = np.array(converted_RGB)
    calucedXYZ = np.dot(RGB2XYZ_conversion_factor, converted_RGB)
    outputXYZ = np.dot(calucedXYZ, 100)

    return outputXYZ


def XYZ2LMS(inputXYZ):
    XYZ2LMS_conversion_factor = np.array([[0.15516, 0.54307, -0.03701], [-0.15516, 0.45692, 0.02969], [0, 0, 0.00732]]) # XYZ表色系からLMS値への変換係数
    outputLMS = np.dot(XYZ2LMS_conversion_factor, inputXYZ)

    return outputLMS


# 二色型色覚が見ているMS平面,LS平面,LM平面に投影するための係数を算出
def culcDichromatCoefficient(whiteLMS,dichromatLMS):
    elm1 = whiteLMS[1] * dichromatLMS[2] - whiteLMS[2] * dichromatLMS[1]
    elm2 = whiteLMS[2] * dichromatLMS[0] - whiteLMS[0] * dichromatLMS[2]
    elm3 = whiteLMS[0] * dichromatLMS[1] - whiteLMS[1] * dichromatLMS[0]
    ret = np.array([elm1, elm2, elm3])

    return ret


def LMS4protan(inputLMS):
    whiteXYZ = np.array([0.333, 0.333, 0.333])  #XYZ表色系における白色エネルギー
    whiteLMS = XYZ2LMS(whiteXYZ)  # 白色のLMS値を光エネルギーの傾き判定の基準とする
    tangent_inputLMS = inputLMS[2]/inputLMS[1]  # ProtanはL軸情報が喪失するのでMS平面に投影
    tangent_whiteLMS = whiteLMS[2]/whiteLMS[1]  # 入力LMSと白色LMS値の傾き

    XYZ575nm = np.array([0.8425, 0.9154, 0.0018]) # 波長575nmのXYZ表色系
    XYZ475nm = np.array([0.1421, 0.1126, 1.0419]) # 波長475nmのXYZ表色系
    if tangent_inputLMS < tangent_whiteLMS:
        dichromatLMS = XYZ2LMS(XYZ575nm)  # 白色よりも波長が大きい
    else:
        dichromatLMS = XYZ2LMS(XYZ475nm)  # 白色よりも波長が小さい

    DichromatCoefficient = culcDichromatCoefficient(whiteLMS, dichromatLMS)

    # Protan変換の場合はL軸に沿って投影させる
    protanL = (DichromatCoefficient[1] * inputLMS[1] + DichromatCoefficient[2] * inputLMS[2]) / DichromatCoefficient[0] * -1
    protanLMS = np.array([protanL, inputLMS[1], inputLMS[2]])

    return protanLMS


def LMS4deutan(inputLMS):
    whiteXYZ = np.array([0.333, 0.333, 0.333])  #XYZ表色系における白色エネルギー
    whiteLMS = XYZ2LMS(whiteXYZ)  # 白色のLMS値を光エネルギーの傾き判定の基準とする
    tangent_inputLMS = inputLMS[2]/inputLMS[0]  # ProtanはLMS空間のM軸情報が喪失するのでLS平面に投影
    tangent_whiteLMS = whiteLMS[2]/whiteLMS[0]  # 入力LMSと白色LMS値の傾き

    XYZ575nm = np.array([0.8425, 0.9154, 0.0018]) # 波長575nmのXYZ表色系
    XYZ475nm = np.array([0.1421, 0.1126, 1.0419]) # 波長475nmのXYZ表色系
    if tangent_inputLMS < tangent_whiteLMS:
        dichromatLMS = XYZ2LMS(XYZ575nm)  # 白色よりも波長が大きい
    else:
        dichromatLMS = XYZ2LMS(XYZ475nm)  # 白色よりも波長が小さい

    DichromatCoefficient = culcDichromatCoefficient(whiteLMS, dichromatLMS)

    # deutan変換の場合はM軸に沿って投影させる
    deutanM = (DichromatCoefficient[0] * inputLMS[0] + DichromatCoefficient[2] * inputLMS[2]) / DichromatCoefficient[1] * -1
    deutanLMS = np.array([inputLMS[0], deutanM, inputLMS[2]])

    return deutanLMS


def LMS2XYZ(inputLMS):
    LMS2XYZ_conversion_factor = np.linalg.inv(np.array([[0.15516, 0.54307, -0.03701], [-0.15516, 0.45692, 0.02969], [0, 0, 0.00732]])) # XYZ表色系をLMS値に変換する係数の逆行列
    outputXYZ = np.dot(LMS2XYZ_conversion_factor, inputLMS)

    return outputXYZ


def XYZ4Lab(inputXYZ):
    whiteXYZd50 = np.array([96.42, 100.0, 82.49])  # D50における白色点のXYZ値(Xn, Yn, Zn)

    # LabのL成分の計算
    L = 0
    th = 0.008856
    normaliseX = inputXYZ[0] / whiteXYZd50[0]
    normaliseY = inputXYZ[1] / whiteXYZd50[1]
    normaliseZ = inputXYZ[2] / whiteXYZd50[2]
    if normaliseY > th:
        L = np.cbrt(normaliseY) * 116-16
    else:
        L = normaliseY * 903.29

    a = 500 * (np.cbrt(normaliseX) - np.cbrt(normaliseY)) # Labのa成分の計算
    b = 200 * (np.cbrt(normaliseY) - np.cbrt(normaliseZ)) # Labのa成分の計算

    outputLab = np.array([L, a, b])

    return outputLab


def RadianToDegree(radian):
    degree = radian * (180 / np.pi)

    return degree


def DegreeToRadian(degree):
    radian = degree * (np.pi / 180)
    
    return radian


def CIEDE2000(Lab1, Lab2, kL=1, kC=1, kH=1):
    L1, a1, b1, L2, a2, b2 = np.concatenate([Lab1, Lab2])
    deltaLp = L2 - L1
    L_ = (L1 + L2) / 2

    C1 = np.sqrt(np.power(a1, 2) + np.power(b1, 2))
    C2 = np.sqrt(np.power(a2, 2) + np.power(b2, 2))
    C_ = (C1 + C2) / 2

    ap1 = a1 + (a1 / 2) * (1 - np.sqrt(np.power(C_, 7) / (np.power(C_, 7) + np.power(25, 7))))
    ap2 = a2 + (a2 / 2) * (1 - np.sqrt(np.power(C_, 7) / (np.power(C_, 7) + np.power(25, 7))))

    Cp1 = np.sqrt(np.power(ap1, 2) + np.power(b1, 2))
    Cp2 = np.sqrt(np.power(ap2, 2) + np.power(b2, 2))
    Cp_ = (Cp1 + Cp2) / 2
    deltaCp = Cp2 - Cp1

    if (b1 == 0) and (ap1 == 0):
        hp1 = 0
    else:
        hp1 = RadianToDegree(np.arctan2(b1, ap1))
        if hp1 < 0:
            hp1 = hp1 + 360
        else:
            pass

    if (b2 == 0) and (ap2 == 0):
        hp2 = 0
    else:
        hp2 = RadianToDegree(np.arctan2(b2, ap2))
        if hp2 < 0:
            hp2 = hp2 + 360
        else:
            pass

    if (C1 == 0) or (C2 == 0):
        deltahp = 0
    elif np.abs(hp1 - hp2) <= 180:
        deltahp = hp2 - hp1
    elif hp2 <= hp1:
        deltahp = hp2 - hp1 + 360
    else:
        deltahp = hp2 - hp1 - 360

    deltaHp = 2 * np.sqrt(Cp1 * Cp2) * np.sin(DegreeToRadian(deltahp) / 2)

    if np.abs(hp1 - hp2) > 180:
        Hp_ = (hp1 + hp2 + 360) / 2
    else:
        Hp_ = (hp1 + hp2) / 2

    T = 1 - 0.17 * np.cos(DegreeToRadian(Hp_ - 30)) + 0.24 * np.cos(DegreeToRadian(2 * Hp_)) + 0.32 * np.cos(DegreeToRadian(3 * Hp_ + 6)) - 0.20 * np.cos(DegreeToRadian(4 * Hp_ - 63))
    
    SL = 1 + ((0.015 * np.power(L_ - 50, 2)) / np.sqrt(20 + np.power(L_ - 50, 2)))
    SC = 1 + 0.045 * Cp_
    SH = 1 + 0.015 * Cp_ * T

    RT = -2 * np.sqrt(np.power(Cp_, 7) / (np.power(Cp_, 7) + np.power(25, 7))) * np.sin(DegreeToRadian(60 * np.exp(-np.power((Hp_ - 275) / 25, 2))))

    color_diff = np.sqrt(np.power(deltaLp / (kL * SL), 2) + np.power(deltaCp / (kC * SC), 2) + np.power(deltaHp / (kH * SH), 2) + RT * (deltaCp / (kC * SC)) * (deltaHp / (kH * SH)))

    return color_diff


def judge_color_diff(Lab1, Lab2):
    # JISに基づいた色差の判定
    TH_NON_COLORIMETRY_AREA = 0.2  # 特別に調整された測色器械でも誤差の範囲にあり、人では識別不能
    TH_IDENTIFICATION_COLOR_DIFFERENCE = 0.3  # 十分に調整された測色器械の再現精度の範囲で、訓練を積んだ人が再現性を持って識別できる限界
    TH_AAA = 0.4  # 目視判定の再現性からみて、厳格な許容色差の規格を設定できる限界
    TH_AA = 0.8  # 色の隣接比較で、わずかに色差が感じられるレベル。一般の測色器械間の誤差を含む許容色差の範囲 
    TH_A = 1.6  # 色の離間比較では、ほとんど気付かれない色差レベル。一般的には同じ色だと思われているレベル
    TH_B = 3.2  # 印象レベルでは同じ色として扱える範囲。塗料業界やプラスチック業界では色違いでクレームになることがある
    TH_C = 6.5  # ＪＩＳ標準色票、マンセル色票等の１歩度に相当する色差
    TH_D = 13.0  # 細分化された系統色名で区別ができる程度の色の差で、この程度を超えると別の色名のイメージになる
    THRESHOLD_OTHER_COLOR = 25.0  # 完全に別の色

    color_diff = CIEDE2000(Lab1, Lab2)
    if color_diff <= TH_NON_COLORIMETRY_AREA:
        result_msg = "評価不能領域"
    elif color_diff <= TH_IDENTIFICATION_COLOR_DIFFERENCE:
        result_msg = "識別限界"
    elif color_diff <= TH_AAA:
        result_msg = "AAA級許容差"
    elif color_diff <= TH_AA:
        result_msg = "AA級許容差"
    elif color_diff <= TH_A:
        result_msg = "A級許容差"
    elif color_diff <= TH_B:
        result_msg = "B級許容差"
    elif color_diff <= TH_C:
        result_msg = "C級許容差"
    elif color_diff <= TH_D:
        result_msg = "D級許容差"
    else:
        result_msg = "別の色"

    return result_msg, color_diff


def calc_commonLab(inputRGB):
    XYZ = RGB2XYZ(inputRGB)
    LMS = XYZ2LMS(XYZ)
    commonLab = XYZ4Lab(XYZ)

    return commonLab


def calc_protanLab(inputRGB):
    XYZ = RGB2XYZ(inputRGB)
    LMS = XYZ2LMS(XYZ)
    protanLMS = LMS4protan(LMS)
    protanXYZ = LMS2XYZ(protanLMS)
    protanLab = XYZ4Lab(protanXYZ)

    return protanLab


def calc_deutanLab(inputRGB):
    XYZ = RGB2XYZ(inputRGB)
    LMS = XYZ2LMS(XYZ)
    deutanLMS = LMS4deutan(LMS)
    deutanXYZ = LMS2XYZ(deutanLMS)
    deutanLab = XYZ4Lab(deutanXYZ)

    return deutanLab


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='入力された２つのRGB値から色覚タイプごとの色差判定を行う')
    parser.add_argument('rgb1', help='比較するRGB1')
    parser.add_argument('rgb2', help='比較するRGB2')
    args = parser.parse_args()

    try:
        RGB1 = tuple(map(lambda x: int(x), args.rgb1.split("-")))
    except ValueError:
        print("\033[35m use \"-\" to split for RGB1 \033[0m")
        sys.exit()

    try:
        RGB2 = tuple(map(lambda x: int(x), args.rgb2.split("-")))
    except ValueError:
        print("\033[35m use \"-\" to split for RGB2\033[0m")
        sys.exit()


    commonLab1 = calc_commonLab(RGB1)
    protanLab1 = calc_protanLab(RGB1)
    deutanLab1 = calc_deutanLab(RGB1)

    commonLab2 = calc_commonLab(RGB2)
    protanLab2 = calc_protanLab(RGB2)
    deutanLab2 = calc_deutanLab(RGB2)

    result_common = judge_color_diff(commonLab1, commonLab2)
    result_protan = judge_color_diff(protanLab1, protanLab2)
    result_deutan = judge_color_diff(deutanLab1, deutanLab2)

    print("\n\033[4m RGB1: {} / RGB2: {} \033[0m".format(RGB1, RGB2))
    print("\033[34m C型の色差判定: {} / SCORE: {} \033[0m".format(result_common[0], result_common[1]))
    print("\033[31m P型の色差判定: {} / SCORE: {} \033[0m".format(result_protan[0], result_protan[1]))
    print("\033[32m D型の色差判定: {} / SCORE: {} \033[0m\n".format(result_deutan[0], result_deutan[1]))
