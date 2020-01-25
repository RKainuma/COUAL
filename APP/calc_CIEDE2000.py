import argparse
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import sRGBColor, LabColor, XYZColor
import numpy as np
import sys
from timeit import timeit, default_timer

np.set_printoptions(precision=30)  # 有効桁数を少数第20位までに指定


def RGB2XYZ(rgb):
    xyz = convert_color(sRGBColor(*(rgb / 255)), XYZColor, target_illuminant='d65')

    return xyz


def RGB2Lab(rgb):
    lab = convert_color(sRGBColor(*(rgb / 255)), LabColor, target_illuminant='d65')

    return lab

def XYZ2RGB(xyz):
    rgb = convert_color(sRGBColor(*(xyz)), sRGBColor, target_illuminant='d65')

    return rgb


def XYZ2Lab(xyz):
    obj = XYZColor(*(xyz))
    lab = convert_color(XYZColor(*(xyz)), LabColor, target_illuminant='d65')

    return lab


def XYZ2LMS(xyz):
    """XYZ表色系からLMS値に変換"""
    XYZ2LMS_conversion_factor = np.array([[0.4002, 0.7076, -0.0808], [-0.2263, 1.1653, 0.0457], [0, 0, 0.9182]])  # XYZ表色系からLMS値への変換係数
    lms = np.dot(XYZ2LMS_conversion_factor, xyz)

    return lms


def LMS2XYZ(lms):
    """LMS値をXYZ表色系に変換"""
    LMS2XYZ_conversion_factor = np.linalg.inv(np.array([[0.4002, 0.7076, -0.0808], [-0.2263, 1.1653, 0.0457], [0, 0, 0.9182]]))  # XYZ表色系をLMS値に変換する係数の逆行列
    xyz = np.dot(LMS2XYZ_conversion_factor, lms)

    return xyz


def culcDichromatCoefficient(whiteLMS,dichromatLMS):
    """二色型色覚が見ているMS平面,LS平面,LM平面に投影するための係数を算出"""
    elm1 = whiteLMS[1] * dichromatLMS[2] - whiteLMS[2] * dichromatLMS[1]
    elm2 = whiteLMS[2] * dichromatLMS[0] - whiteLMS[0] * dichromatLMS[2]
    elm3 = whiteLMS[0] * dichromatLMS[1] - whiteLMS[1] * dichromatLMS[0]
    ret = np.array([elm1, elm2, elm3])

    return ret


def LMS4protan(lms):
    """P型色覚のLMS値に変換"""
    whiteXYZ = np.array([0.333, 0.333, 0.333])  #XYZ表色系における白色エネルギー
    whiteLMS = XYZ2LMS(whiteXYZ)  # 白色のLMS値を光エネルギーの傾き判定の基準とする
    tangent_lms = lms[2]/lms[1]  # ProtanはL軸情報が喪失するのでMS平面に投影
    tangent_whiteLMS = whiteLMS[2]/whiteLMS[1]  # 入力LMSと白色LMS値の傾き

    XYZ575nm = np.array([0.8425, 0.9154, 0.0018])  # 波長575nmのXYZ表色系
    XYZ475nm = np.array([0.1421, 0.1126, 1.0419])  # 波長475nmのXYZ表色系
    if tangent_lms < tangent_whiteLMS:
        dichromatLMS = XYZ2LMS(XYZ575nm)  # 白色よりも波長が大きい
    else:
        dichromatLMS = XYZ2LMS(XYZ475nm)  # 白色よりも波長が小さい

    DichromatCoefficient = culcDichromatCoefficient(whiteLMS, dichromatLMS)

    # Protan変換の場合はL軸に沿って投影させる
    protan_l = (DichromatCoefficient[1] * lms[1] + DichromatCoefficient[2] * lms[2]) / DichromatCoefficient[0] * -1
    protan_lms = np.array([protan_l, lms[1], lms[2]])

    return protan_lms


def LMS4deutan(lms):
    """D型色覚のLMS値に変換"""
    whiteXYZ = np.array([0.333, 0.333, 0.333])  #XYZ表色系における白色エネルギー
    whiteLMS = XYZ2LMS(whiteXYZ)  # 白色のLMS値を光エネルギーの傾き判定の基準とする
    tangent_lms = lms[2]/lms[0]  # ProtanはLMS空間のM軸情報が喪失するのでLS平面に投影
    tangent_whiteLMS = whiteLMS[2]/whiteLMS[0]  # 入力LMSと白色LMS値の傾き

    XYZ575nm = np.array([0.8425, 0.9154, 0.0018])  # 波長575nmのXYZ表色系
    XYZ475nm = np.array([0.1421, 0.1126, 1.0419])  # 波長475nmのXYZ表色系
    if tangent_lms < tangent_whiteLMS:
        dichromatLMS = XYZ2LMS(XYZ575nm)  # 白色よりも波長が大きい
    else:
        dichromatLMS = XYZ2LMS(XYZ475nm)  # 白色よりも波長が小さい

    DichromatCoefficient = culcDichromatCoefficient(whiteLMS, dichromatLMS)

    # deutan変換の場合はM軸に沿って投影させる
    deutan_m = (DichromatCoefficient[0] * lms[0] + DichromatCoefficient[2] * lms[2]) / DichromatCoefficient[1] * -1
    deutan_lms = np.array([lms[0], deutan_m, lms[2]])

    return deutan_lms

def judge_color_diff(color_diff):
    """JISに基づいた色差の判定"""
    # 以下、CIEDE2000の結果を判定するパラメーター
    TH_NON_COLORIMETRY_AREA = 0.2  # 特別に調整された測色器械でも誤差の範囲にあり、人では識別不能
    TH_IDENTIFICATION_COLOR_DIFFERENCE = 0.4  # 十分に調整された測色器械の再現精度の範囲で、訓練を積んだ人が再現性を持って識別できる限界
    TH_AAA = 0.8  # 目視判定の再現性からみて、厳格な許容色差の規格を設定できる限界
    TH_AA = 1.6  # 色の隣接比較で、わずかに色差が感じられるレベル。一般の測色器械間の誤差を含む許容色差の範囲 
    TH_A = 3.2  # 色の離間比較では、ほとんど気付かれない色差レベル。一般的には同じ色だと思われているレベル
    TH_B = 6.5  # 印象レベルでは同じ色として扱える範囲。塗料業界やプラスチック業界では色違いでクレームになることがある
    TH_C = 13.0  # ＪＩＳ標準色票、マンセル色票等の１歩度に相当する色差
    TH_D = 25.0  # 細分化された系統色名で区別ができる程度の色の差で、この程度を超えると別の色名のイメージになる

    if color_diff <= TH_NON_COLORIMETRY_AREA:  # 評価不能領域
        result_label = "UNEVALUABLE"
        result_msg = "評価不能領域"
    elif color_diff <= TH_IDENTIFICATION_COLOR_DIFFERENCE:  # 識別限界
        result_label = "LIMIT"
        result_msg = "識別限界"
    elif color_diff <= TH_AAA:  # AAA級許容差
        result_label = "AAA"
        result_msg = "AAA級許容差"
    elif color_diff <= TH_AA:  # AA級許容差
        result_label = "AA"
        result_msg = "AA級許容差"
    elif color_diff <= TH_A:  # A級許容差
        result_label = "A"
        result_msg = "A級許容差"
    elif color_diff <= TH_B:  # B級許容差
        result_label = "B"
        result_msg = "B級許容差"
    elif color_diff <= TH_C:  # C級許容差
        result_label = "C"
        result_msg = "C級許容差"
    elif color_diff <= TH_D:  # D級許容差
        result_label = "D"
        result_msg = "D級許容差"
    else:  # 別の色
        result_label = "FINE"
        result_msg = "別の色"

    return {"label":result_label, "msg":result_msg}


def proceed_color_diff(RGB1, RGB2, warning=False):
    RGB1, RGB2 = np.array(RGB1,np.uint8), np.array(RGB2,np.uint8)
    XYZ1, XYZ2 = RGB2XYZ(RGB1), RGB2XYZ(RGB2)
    XYZ1 = XYZ1.xyz_x, XYZ1.xyz_y, XYZ1.xyz_z
    XYZ2 = XYZ2.xyz_x, XYZ2.xyz_y, XYZ2.xyz_z
    LMS1, LMS2 = XYZ2LMS(XYZ1), XYZ2LMS(XYZ2)

    # C型の色差を求める処理
    common_Lab1, common_Lab2 = XYZ2Lab(XYZ1), XYZ2Lab(XYZ2)
    common_color_diff = delta_e_cie2000(common_Lab1, common_Lab2)
    common_judge_JIS = judge_color_diff(common_color_diff)
    if (common_judge_JIS['label'] == "FINE") or (common_judge_JIS['label'] == "D"):
        # P型の色差を求める処理
        protan_LMS1, protan_LMS2 = LMS4protan(LMS1), LMS4protan(LMS2)
        protan_XYZ1, protan_XYZ2 = LMS2XYZ(protan_LMS1), LMS2XYZ(protan_LMS2)
        protan_Lab1, protan_Lab2 = XYZ2Lab(protan_XYZ1), XYZ2Lab(protan_XYZ2)
        protan_color_diff = delta_e_cie2000(protan_Lab1, protan_Lab2)
        protan_judge_JIS = judge_color_diff(protan_color_diff)

        if (protan_judge_JIS['label'] == "FINE") or (protan_judge_JIS['label'] == "D"):
            # D型の色差を求める処理
            deutan_LMS1, deutan_LMS2 = LMS4deutan(LMS1), LMS4deutan(LMS2)
            deutan_XYZ1, deutan_XYZ2 = LMS2XYZ(deutan_LMS1), LMS2XYZ(deutan_LMS2)
            deutan_Lab1, deutan_Lab2 = XYZ2Lab(deutan_XYZ1), XYZ2Lab(deutan_XYZ2)
            deutan_color_diff = delta_e_cie2000(deutan_Lab1, deutan_Lab2)
            deutan_judge_JIS = judge_color_diff(deutan_color_diff)
            if (deutan_judge_JIS['label'] == "FINE") or (deutan_judge_JIS['label'] == "D"):
                pass
            else:
                warning = True
        else:
            warning = True
    else:
        pass

    return warning


# 検証用
def judge_color_valid(common_diff, protan_diff, deutan_diff, warning=False):
    """C型、P型、D型色覚の色差の結果をもとに配色パターンの正当性を判定"""
    if (common_diff["label"] == "FINE") or (common_diff["label"] == "D"):
        if (protan_diff["label"] != "UNEVALUABLE") and (protan_diff["label"] != "FINE") and (protan_diff["label"] != "D"):
            warning = True
        elif (deutan_diff["label"] != "UNEVALUABLE") and (deutan_diff["label"] != "FINE") and (deutan_diff["label"] != "D"):
            warning = True
        else:
            pass
    else:
        pass

    return warning

# 検証用
def proceed_color_diff_for_debug(RGB1, RGB2):
    RGB1, RGB2 = np.array(RGB1,np.uint8), np.array(RGB2,np.uint8)
    XYZ1, XYZ2 = RGB2XYZ(RGB1), RGB2XYZ(RGB2)
    XYZ1 = XYZ1.xyz_x, XYZ1.xyz_y, XYZ1.xyz_z
    XYZ2 = XYZ2.xyz_x, XYZ2.xyz_y, XYZ2.xyz_z
    LMS1, LMS2 = XYZ2LMS(XYZ1), XYZ2LMS(XYZ2)

    # C型の色差を求める処理
    common_Lab1, common_Lab2 = XYZ2Lab(XYZ1), XYZ2Lab(XYZ2)
    common_color_diff = delta_e_cie2000(common_Lab1, common_Lab2)
    common_judge_JIS = judge_color_diff(common_color_diff)
    common_diff = {"result": common_color_diff, "JIS": common_judge_JIS}

    # P型の色差を求める処理
    protan_LMS1, protan_LMS2 = LMS4protan(LMS1), LMS4protan(LMS2)
    protan_XYZ1, protan_XYZ2 = LMS2XYZ(protan_LMS1), LMS2XYZ(protan_LMS2)
    protan_Lab1, protan_Lab2 = XYZ2Lab(protan_XYZ1), XYZ2Lab(protan_XYZ2)
    protan_color_diff = delta_e_cie2000(protan_Lab1, protan_Lab2)
    protan_judge_JIS = judge_color_diff(protan_color_diff)
    protan_diff = {"result": protan_color_diff, "JIS": protan_judge_JIS}

    # D型の色差を求める処理
    deutan_LMS1, deutan_LMS2 = LMS4deutan(LMS1), LMS4deutan(LMS2)
    deutan_XYZ1, deutan_XYZ2 = LMS2XYZ(deutan_LMS1), LMS2XYZ(deutan_LMS2)
    deutan_Lab1, deutan_Lab2 = XYZ2Lab(deutan_XYZ1), XYZ2Lab(deutan_XYZ2)
    deutan_color_diff = delta_e_cie2000(deutan_Lab1, deutan_Lab2)
    deutan_judge_JIS = judge_color_diff(deutan_color_diff)
    deutan_diff = {"result": deutan_color_diff, "JIS": deutan_judge_JIS}

    warning = judge_color_valid(common_judge_JIS, protan_judge_JIS, deutan_judge_JIS)

    return warning, common_diff, protan_diff, deutan_diff

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='入力された２つのRGB値から色覚タイプごとの色差判定を行う')
    parser.add_argument('rgb1', help='比較するRGB1')
    parser.add_argument('rgb2', help='比較するRGB2')
    parser.add_argument("--verbose", action="store_true", default=False, help='This is verbose running.')
    parser.add_argument("--debug", action="store_true", default=False, help='This is debug running.')
    parser.add_argument("-i", "--iteration", type=int, default=1000, help='Input num as iteration times on debug mode.')

    args = parser.parse_args()
    is_diff_msg = False
    process_speed= None

    try:
        RGB1 = tuple(map(lambda x: int(x), args.rgb1.split("-")))
    except ValueError:
        print("\033[35m use \"-\" to split for RGB1 \033[0m")
        sys.exit()

    try:
        RGB2 = tuple(map(lambda x: int(x), args.rgb2.split("-")))
    except ValueError:
        print("\033[35m use \"-\" to split for RGB2 \033[0m")
        sys.exit()

    if args.verbose:
        runMode = "Run as verbose mode"
        is_diff_msg = True
        RGB1, RGB2 = np.array(RGB1,np.uint8), np.array(RGB2,np.uint8)
        XYZ1, XYZ2 = RGB2XYZ(RGB1), RGB2XYZ(RGB2)
        XYZ1 = XYZ1.xyz_x, XYZ1.xyz_y, XYZ1.xyz_z
        XYZ2 = XYZ2.xyz_x, XYZ2.xyz_y, XYZ2.xyz_z
        LMS1, LMS2 = XYZ2LMS(XYZ1), XYZ2LMS(XYZ2)

        # C型の色差を求める処理
        common_Lab1, common_Lab2 = XYZ2Lab(XYZ1), XYZ2Lab(XYZ2)
        common_color_diff = delta_e_cie2000(common_Lab1, common_Lab2)
        common_judge_JIS = judge_color_diff(common_color_diff)
        common_diff = {"result": common_color_diff, "JIS": common_judge_JIS}

        # P型の色差を求める処理
        protan_LMS1, protan_LMS2 = LMS4protan(LMS1), LMS4protan(LMS2)
        protan_XYZ1, protan_XYZ2 = LMS2XYZ(protan_LMS1), LMS2XYZ(protan_LMS2)
        protan_Lab1, protan_Lab2 = XYZ2Lab(protan_XYZ1), XYZ2Lab(protan_XYZ2)
        protan_color_diff = delta_e_cie2000(protan_Lab1, protan_Lab2)
        protan_judge_JIS = judge_color_diff(protan_color_diff)
        protan_diff = {"result": protan_color_diff, "JIS": protan_judge_JIS}

        # D型の色差を求める処理
        deutan_LMS1, deutan_LMS2 = LMS4deutan(LMS1), LMS4deutan(LMS2)
        deutan_XYZ1, deutan_XYZ2 = LMS2XYZ(deutan_LMS1), LMS2XYZ(deutan_LMS2)
        deutan_Lab1, deutan_Lab2 = XYZ2Lab(deutan_XYZ1), XYZ2Lab(deutan_XYZ2)
        deutan_color_diff = delta_e_cie2000(deutan_Lab1, deutan_Lab2)
        deutan_judge_JIS = judge_color_diff(deutan_color_diff)
        deutan_diff = {"result": deutan_color_diff, "JIS": deutan_judge_JIS}

        warning = judge_color_valid(common_judge_JIS, protan_judge_JIS, deutan_judge_JIS)

    elif args.debug:
        runMode = "Run as debug mode"
        is_diff_msg = True

        warning, common_diff, protan_diff, deutan_diff = proceed_color_diff_for_debug(RGB1, RGB2)
        process_speed = timeit('proceed_color_diff_for_debug(RGB1, RGB2)', globals=globals(), number=args.iteration)

    else:
        runMode = "Run as application mode"

        warning = proceed_color_diff(RGB1, RGB2)

    # 以下結果表示に関する処理
    if warning is True:
        result_msg = "色異常者では判断しづらい色が含まれています。"
    elif warning is False:
        result_msg = "全色覚にとって判別しやすい配色となっています。"
    else:
        raise ValueError("\033[35m An error occured \033[0m")

    print("\n\033[1m {} \033[0m".format(runMode))
    print("\n\033[4m RGB1: {} / RGB2: {}  ==> {} \033[0m \n".format(RGB1, RGB2, result_msg))

    if is_diff_msg:
        print("\033[34m C型の色差判定: {} / SCORE: {} \033[0m".format(common_diff["JIS"]["msg"], common_diff["result"]))
        print("\033[31m P型の色差判定: {} / SCORE: {} \033[0m".format( protan_diff["JIS"]["msg"], protan_diff["result"]))
        print("\033[32m D型の色差判定: {} / SCORE: {} \033[0m\n".format(deutan_diff["JIS"]["msg"], deutan_diff["result"]))
    else:
        print("\n")

    if process_speed is not None:
        print("\033[01m Process speed of {} times: {} \033[0m\n".format(args.iteration, process_speed))
    else:
        print("\033[01m Use debug mode to show {} times process speed. \033[0m\n".format(args.iteration))
