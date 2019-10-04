#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import io
import time
import cv2
import base64
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename
from colorDetector import Color
app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'PNG', 'JPG'])
IMAGE_WIDTH = 640
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)

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
        else:
            return ''' <p>許可されていない拡張子です</p> '''

        # Read image and adjust to data-type, OpenCV coveres
        f = img_file.stream.read()
        bin_data = io.BytesIO(f)
        file_bytes = np.asarray(bytearray(bin_data.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        # 元画像のリサイズ
        raw_img = cv2.resize(img, (IMAGE_WIDTH, int(IMAGE_WIDTH*img.shape[0]/img.shape[1])))
        result, encimg = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        orgImg = base64.b64encode(encimg).decode("utf-8")
        # cv2.imwrite("./in.jpg", raw_img)
        
        # なにがしかの加工
        out = Color.read_input_image(img)
        result, encimg = cv2.imencode(".jpg", out, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        outImg = base64.b64encode(encimg).decode("utf-8")
        return render_template('index.html', raw_img_url=orgImg, gray_img_url=outImg)
        # return redirect(url_for('index')) #NOTE base64エンコードしたデータを返す
    else:
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
