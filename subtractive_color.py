import cv2
import numpy as np

def execute(img):
    # 画像で使用されている色一覧。(W * H, 3) の numpy 配列。
    colors = img.reshape(-1, 3)
    # cv2.kmeans に渡すデータは float 型である必要があるため、キャストする。
    colors = colors.astype(np.float32)

    # クラスタ数
    K = 15

       # 最大反復回数: 10、移動量の閾値: 1.0
    criteria = cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 10, 1.0

    ret, label, center = cv2.kmeans(
        colors, K, None, criteria, attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS
    )

    # 各クラスタに属するサンプル数を計算する。
    _, counts = np.unique(label, axis=0, return_counts=True)

    # 各画素を k平均法の結果に置き換える。
    dst = center[label.ravel()].reshape(img.shape)
    dst = dst.astype(np.uint8)

    return dst
