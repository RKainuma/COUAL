#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import io
import time
import base64
from werkzeug import secure_filename

import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session

from colorDetector import Color

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'PNG', 'JPG'])
IMAGE_WIDTH = 640
QUARITY = 90
ENCODE_PARAMS = [int(cv2.IMWRITE_JPEG_QUALITY), QUARITY]


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

        # Read image and adjust to OpenCV coverable data-type
        read_file = img_file.stream.read()
        bin_img = io.BytesIO(read_file)
        np_img = np.asarray(bytearray(bin_img.read()), dtype=np.uint8)
        dec_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # Resize original-image
        org_img = cv2.resize(dec_img, (IMAGE_WIDTH, int(IMAGE_WIDTH*dec_img.shape[0]/dec_img.shape[1])))
        result, enc_img = cv2.imencode(".jpg", org_img, ENCODE_PARAMS)
        org_img = base64.b64encode(enc_img).decode("utf-8")

        #NOTE まだ緑しか見つけてないけど、ベースの仕組みはこれ
        out_img = Color.read_input_image(dec_img)
        result, enc_img = cv2.imencode(".jpg", out_img, ENCODE_PARAMS)
        result_img = base64.b64encode(enc_img).decode("utf-8")

        return render_template('index.html', original_img=org_img, result_img=result_img)

    else:
        return redirect(url_for('index.html'))


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
