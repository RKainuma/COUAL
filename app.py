#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import io
import matplotlib.pyplot as plt
import os
import time
from werkzeug import secure_filename

import cv2
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import numpy as np

from colorDetector import Color
from cloud_firestore import ColorSchemeStorage

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'PNG', 'JPG'])
IMAGE_WIDTH = 500
QUARITY = 90
ENCODE_PARAMS = [int(cv2.IMWRITE_JPEG_QUALITY), QUARITY]


def starter_setups():
    ColorSchemeStorage.get_keys_to_analyze_color()

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        img_file = request.files['img_file']
        # 変なファイル弾き
        if img_file and allowed_file(img_file.filename): 
            filename = secure_filename(img_file.filename)
        elif img_file.filename is '':
            return ''' <p>ファイルを選択してください</p> ''' 
        else:
            return ''' <p>許可されていない拡張子です</p> '''

        # Read image and adjust to OpenCV coverable data-type
        read_file = img_file.stream.read()
        bin_img = io.BytesIO(read_file)
        np_img = np.asarray(bytearray(bin_img.read()), dtype=np.uint8)
        dec_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        # Resize original-image
        result, enc_img = cv2.imencode(".jpg", dec_img, ENCODE_PARAMS)
        org_img = base64.b64encode(enc_img).decode("utf-8")
        
        analyzed_img, detection_result = Color.analyse(dec_img)

        result, enc_img = cv2.imencode(".jpg", analyzed_img, ENCODE_PARAMS)
        analyzed_img = base64.b64encode(enc_img).decode("utf-8")
        
        return render_template('index.html', original_img=org_img, result_img=analyzed_img, detection_result=detection_result)

    else:
        return redirect(url_for('index.html'))


@app.route('/maintenance')
def maintenance(): 
    """管理画面のテンプレートをレンダリングする"""
    return render_template('maintenance.html')


@app.route('/post_colors', methods=['POST'])
def post_colors(): 
    """管理画面で配色パターンをPOSTする関数を呼び、管理画面のレンダリング関数にリダイレクトする"""
    results = request.form
    base_hsv = results["base-color"]
    base_color_name = results["base-color-name"]

    for i, result in enumerate(results):

        if len(result) < 6:
            if "neg" in result:
                pattern_stat = "negative"
                accent_hsv = results[result]
                accent_color = results[str(result + "-name")]
            elif "pos" in result:
                pattern_stat = "positive"
                accent_hsv = results[result]
                accent_color = results[str(result + "-name")]
            ColorSchemeStorage.post_color_scheme(base_hsv, base_color_name, pattern_stat, accent_hsv, accent_color)

        else:
            pass

    return redirect(url_for('maintenance'))


if __name__ == '__main__':
    starter_setups()
    app.run(host='0.0.0.0', port=5000, debug=True)
