#!/usr/bin/env python
# -*- coding: utf-8 -*-
from colorDetector import Color
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == "POST":
    inputImg = request.files["inputImg"]
    print(inputImg)
    Color.read_input_image(inputImg)
    return render_template('index.html')
  else:
    return render_template('index.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
