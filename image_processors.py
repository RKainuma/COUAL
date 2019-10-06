#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2


def rgb_to_hsv(img):
    """
    [Desc]Converting images from RGB to HSV
    [args]numpy decoded image
    """

    ret = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    return ret
