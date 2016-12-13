# -*- coding: utf-8 -*-
import cv2
import numpy as np
import math
import chainer
import chainer.functions as F
from chainer import cuda
from chainer import optimizers
from chainer import serializers
import random
import six
import six.moves.cPickle as pickle
from six.moves import queue

import nin


flag = False
# マウスイベント時に処理を行う
def mouse_event(event, x, y, flags, param):
    # 左クリックで赤い円形を生成
    global flag
    if event == cv2.EVENT_LBUTTONDOWN:
        flag = True
    if event == cv2.EVENT_LBUTTONUP:
        flag = False
    if event == cv2.EVENT_MOUSEMOVE and flag:
        cv2.circle(img, (x, y), 5, (255, 255, 255), -1)
    
    # 右クリック + Shiftキーで緑色のテキストを生成
    elif event == cv2.EVENT_RBUTTONUP and flags & cv2.EVENT_FLAG_SHIFTKEY:
        cv2.putText(img, "CLICK!!", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 3, cv2.CV_AA)
    
    # 右クリックのみで青い四角形を生成
    elif event == cv2.EVENT_RBUTTONUP:
        cv2.rectangle(img, (x-100, y-100), (x+100, y+100), (255, 0, 0), -1)


# 画像の読み込み
img = np.zeros((256,256,3), dtype="uint8")
# ウィンドウのサイズを変更可能にする
cv2.namedWindow("img", cv2.WINDOW_NORMAL)
# マウスイベント時に関数mouse_eventの処理を行う
cv2.setMouseCallback("img", mouse_event)
mean_image = pickle.load(open("mean.npy", 'rb'))
size = 256
model = nin.NIN()
serializers.load_npz("tegaki.model", model)
x = np.ndarray((1, 3, model.insize, model.insize), dtype=np.float32)
categories = np.loadtxt("labels.txt", str, delimiter="\t")

# 「Q」が押されるまで画像を表示する
while (True):
    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    if cv2.waitKey(1) & 0xFF == ord("e"):
        img = np.zeros((256,256,3), dtype="uint8")
    if cv2.waitKey(1) & 0xFF == ord("c"):
        resized_img = cv2.resize(img, (256,256))
        cropped_img = np.zeros((256,256,3))
        cropped_img[0:256,0:256] = resized_img
        top=left=(256-model.insize)/2
        bottom=model.insize+top
        right=model.insize+left
        cropped_img=cropped_img.astype(np.float32).swapaxes(0,2).swapaxes(1,2)
        cropped_img = cropped_img[:, top:bottom, left:right]
        cropped_img -= mean_image[:,top:bottom,left:right]
        cropped_img /= 255
        x[0] = cropped_img
        moji = model.predict(x)
        #print np.argmax(moji.data) 97053842
        a = np.argmax(moji.data)
        print categories[a]
