#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import io
import os
import sys
import time

import cv2
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify
from flask_httpauth import HTTPBasicAuth
import numpy as np

from colorDetector import Color
from cloud_firestore import ColorSchemeStorage

app = Flask(__name__)
auth = HTTPBasicAuth()

admin = {"admin": "admin"}
QUARITY = 90
ENCODE_PARAMS = [int(cv2.IMWRITE_JPEG_QUALITY), QUARITY]

print("Python Version is {}".format(sys.version))


@auth.get_password
def get_pw(username):
    """basic認証を呼ぶ関数 / app.maintenance()が呼ばれると認証を求める"""
    if username in admin:
        return admin.get(username)
    return None

  
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

  
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send', methods=['GET', 'POST'])
def send():
    org_img, dec_img = convertBeforeProcess(request)
    analyzed_img, detection_result = Color.analyse(dec_img)
    analyzed_img = convertAfterProcess(analyzed_img)

    return jsonify({
        "original_img": org_img,
        "analyzed_img": analyzed_img
    })

@app.route('/grayout', methods=['GET', 'POST'])
def grayout():    
    org_img, dec_img = convertBeforeProcess(request)
    analyzed_img = cv2.cvtColor(dec_img, cv2.COLOR_BGR2GRAY)
    analyzed_img = convertAfterProcess(analyzed_img)

    return jsonify({
        "original_img": org_img,
        "analyzed_img": analyzed_img
    })

@app.route('/binarization', methods=['GET', 'POST'])
def binarization():    
    org_img, dec_img = convertBeforeProcess(request)
    retval, analyzed_img = cv2.threshold(dec_img, 150, 255, cv2.THRESH_BINARY)
    analyzed_img = convertAfterProcess(analyzed_img)

    return jsonify({
        "original_img": org_img,
        "analyzed_img": analyzed_img
    })

@app.route('/canny', methods=['GET', 'POST'])
def canny():    
    org_img, dec_img = convertBeforeProcess(request)
    analyzed_img = cv2.Canny(dec_img,100,200)
    analyzed_img = convertAfterProcess(analyzed_img)

    return jsonify({
        "original_img": org_img,
        "analyzed_img": analyzed_img
    })

def convertBeforeProcess(request): 
    img_file = request.files['img_file']
    # Read image and adjust to OpenCV coverable data-type
    read_file = img_file.stream.read()
    bin_img = io.BytesIO(read_file)
    np_img = np.asarray(bytearray(bin_img.read()), dtype=np.uint8)
    dec_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
    # Resize original-image
    result, enc_img = cv2.imencode(".jpg", dec_img, ENCODE_PARAMS)
    org_img = base64.b64encode(enc_img).decode("utf-8")
    return org_img, dec_img

def convertAfterProcess(analyzed_img): 
    result, enc_img = cv2.imencode(".jpg", analyzed_img, ENCODE_PARAMS)
    analyzed_img = base64.b64encode(enc_img).decode("utf-8")
    return analyzed_img

  
@app.route('/maintenance')
@auth.login_required
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
    app.run(host='0.0.0.0', port=5000)
