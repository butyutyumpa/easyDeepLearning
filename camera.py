#!/usr/bin/env python
"""Example code of learning a large scale convnet from ILSVRC2012 dataset.

Prerequisite: To run this example, crop the center of ILSVRC2012 training and
validation images and scale them to 256x256, and make two lists of space-
separated CSV whose first column is full path to image and second column is
zero-origin label (this format is same as that used by Caffe's ImageDataLayer).

"""
from __future__ import print_function
import argparse
import getopt
import datetime
import json
import multiprocessing
import random
import sys
import threading
import time

import numpy as np
from PIL import Image


import six
#import six.moves.cPickle as pickle
import cPickle as pickle
from six.moves import queue
from video import create_capture
from common import clock, draw_str
import chainer
import matplotlib.pyplot as plt
import numpy as np
import math
import chainer.functions as F
import chainer.links as L
from chainer.links import caffe
from matplotlib.ticker import * 
from chainer import serializers
import cv2
import nin

parser = argparse.ArgumentParser(
    description='Image inspection using chainer')
#parser.add_argument('image', help='Path to inspection image file')
parser.add_argument('--model','-m',default='model', help='Path to model file')
parser.add_argument('--mean', default='mean.npy',
                    help='Path to the mean file (computed by compute_mean.py)')
args = parser.parse_args()

def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color, pokemon):
    for x1, y1, x2, y2 in rects:
        cv2.putText(img, pokemon, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)



def read_image(path, center=False, flip=False):
  image = np.asarray(Image.open(path)).transpose(2, 0, 1)
  if center:
    top = left = cropwidth / 2
  else:
    top = random.randint(0, cropwidth - 1)
    left = random.randint(0, cropwidth - 1)
  bottom = model.insize + top
  right = model.insize + left
  image = image[:, top:bottom, left:right].astype(np.float32)
  image -= mean_image[:, top:bottom, left:right]
  image /= 255
  if flip and random.randint(0, 1) == 0:
    return image[:, :, ::-1]
  else:
    return image
def resize(img):
    
    target_shape = (256, 256)
    height, width, depth = img.shape
    #print "height:"+str(height) + "width:" + str(width)
    output_side_length=256
    new_height = output_side_length
    new_width = output_side_length
    if height > width:
        new_height = output_side_length * height / width
    else:
        new_width = output_side_length * width / height

    resized_img = cv2.resize(img, (new_width, new_height))
    height_offset = (new_height - output_side_length) / 2
    width_offset = (new_width - output_side_length) / 2
    cropped_img = resized_img[height_offset:height_offset + output_side_length,
    width_offset:width_offset + output_side_length]
    cv2.imwrite("cropped.jpg", cropped_img)
    
args2, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
args2 = dict(args2)
cascade_fn = args2.get('--cascade', "./total.xml")
cascade = cv2.CascadeClassifier(cascade_fn)
video_src = 0
cam = create_capture(video_src, fallback='synth:bg=../data/lena.jpg:noise=0.05')
mean_image = np.load("mean.npy")
model = nin.NIN()
serializers.load_npz("model.model", model)
cropwidth = 256 - model.insize
model.to_cpu()


def predict(net, x):
    h = F.max_pooling_2d(F.relu(net.mlpconv1(x)), 3, stride=2)
    h = F.max_pooling_2d(F.relu(net.mlpconv2(h)), 3, stride=2)
    h = F.max_pooling_2d(F.relu(net.mlpconv3(h)), 3, stride=2)
    h = net.mlpconv4(F.dropout(h, train=False))
    h = F.reshape(F.average_pooling_2d(h, 6), (1, 1000))
    return F.softmax(h)

#setattr(model, 'predict', predict)
#image = np.asarray(Image.open(args.image)).transpose(2, 0, 1)
#print (image)
#image = cv2.imread(args.image)
#image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#tmp = image[0]
#image[0] = image[2]
#image[2] = tmp
#print (image[:, :, ::-1].copy().T)
#resize(cv2.imread(args.image))
#img = read_image("cropped.jpg")

#img = resize(img)

#x = np.ndarray(
#        (1, 3, model.insize, model.insize), dtype=np.float32)
#x[0]=img
#x = chainer.Variable(np.asarray(x), volatile='on')
categories = np.loadtxt("labels.txt", str, delimiter="\t")
while True:
    ret, img = cam.read()
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.equalizeHist(gray)

    t = clock()
    vis = img.copy()
    rects = detect(vis, cascade)
    if len(rects) != 0:
        for rect in rects:
            x = rect[0]
            y = rect[1]
            w = rect[2]
            h = rect[3]
        resize(img[y:h,x:w])
        cropped_img = read_image("cropped.jpg")
        x = np.array(cropped_img).astype(np.float32).reshape(1, 3, model.insize, model.insize)
        label = np.argmax(model.predict(x).data[0])
        #label = model.predict(x).data
        #print label
        draw_rects(vis, rects, (0, 255, 0), categories[label])
    dt = clock() - t
    cv2.imshow('facedetect', vis)
    if 0xFF & cv2.waitKey(5) == 27:
        break



"""
score = model.predict(x)
categories = np.loadtxt("labels.txt", str, delimiter="\t")

top_k = 20
prediction = zip(score.data[0].tolist(), categories)
prediction.sort(cmp=lambda x, y: cmp(x[0], y[0]), reverse=True)
for rank, (score, name) in enumerate(prediction[:top_k], start=1):
    print('#%d | %s | %4.1f%%' % (rank, name, score * 100))
"""
