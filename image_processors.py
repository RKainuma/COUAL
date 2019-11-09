#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np

def rgb_to_hsv(img):
    """
    [Desc]Converting images from RGB to HSV
    [args]numpy decoded image
    """

    ret = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    return ret

def hsv_to_bgr_tuple(h, s, v):
    bgr = cv2.cvtColor(np.array([[[h, s, v]]], dtype=np.uint8), cv2.COLOR_HSV2BGR)[0][0]
    return (int(bgr[0]), int(bgr[1]), int(bgr[2]))