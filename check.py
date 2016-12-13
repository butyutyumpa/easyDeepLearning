#i!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import cv2
import argparse
import os
import numpy as np

import argparse
import datetime
import json
import multiprocessing
import random
import sys
import threading
import time

import numpy as np
from PIL import Image

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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt

import pylab

parser = argparse.ArgumentParser(
    description='Image inspection using chainer')
parser.add_argument('source_dir', help='Path to inspection image file')
parser.add_argument('--model','-m',default='model', help='Path to model file')
parser.add_argument('--mean', default='mean.npy',
                    help='Path to the mean file (computed by compute_mean.py)')
args = parser.parse_args()

mean_image = np.load("mean.npy")

model = nin.NIN()
serializers.load_npz("model.model", model)

cuda.get_device(0).use()
model.to_gpu()

size = 256
ok=0
ng=0
cropwidth = 256 - model.insize
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

for source_dirpath in os.listdir(args.source_dir):
    for source_imgpath in os.listdir(args.source_dir+"/"+source_dirpath):
        #img = cv2.imread(args.source_dir+"/"+source_dirpath+"/"+source_imgpath)
        resize(cv2.imread(args.source_dir+"/"+source_dirpath+"/"+source_imgpath))
        img = read_image("cropped.jpg")
        x = np.ndarray((1, 3, model.insize, model.insize), dtype=np.float32)
        x[0]=img
        x=cuda.to_gpu(x)
        score = model.predict(x)
        score=cuda.to_cpu(score.data)
        categories = np.loadtxt("labels.txt", str, delimiter="\t")
        prediction = zip(score[0].tolist(), categories)
        prediction.sort(cmp=lambda x, y: cmp(x[0], y[0]), reverse=True)
        top_k=1
        ys_pass=0

        for rank, (score, name) in enumerate(prediction[:top_k], start=1):
            if name == source_dirpath:
                print (args.source_dir+"/"+source_dirpath+"/"+source_imgpath+" "+name+" True")
                ok+=1
            else:
                print (args.source_dir+"/"+source_dirpath+"/"+source_imgpath+" "+name+" False")
                ng+=1

print ("correct {}/{}".format(str(ok),str(ok+ng)),file=sys.stderr)
print ("not correct {}/{}".format(str(ng),str(ok+ng)),file=sys.stderr)
