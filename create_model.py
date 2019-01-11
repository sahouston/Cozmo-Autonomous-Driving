from __future__ import absolute_import
from __future__ import print_function
import os


os.environ['KERAS_BACKEND'] = 'theano'
os.environ['THEANO_FLAGS']='mode=FAST_RUN,device=cuda0,floatX=float32,optimizer=None'


import keras
import keras.models as models

from keras.models import Sequential, Model
from keras.layers.core import Dense, Dropout, Activation, Flatten, Reshape
from keras.layers import BatchNormalization,Input
from keras.layers.recurrent import SimpleRNN, LSTM
from keras.layers.convolutional import Convolution2D
from keras.layers import Conv2D
from keras.optimizers import SGD, Adam, RMSprop
import sklearn.metrics as metrics

import cv2
import numpy as np
import json

import math
import h5py
import glob
from tqdm import tqdm
import scipy
from scipy import misc

imgSize = (66, 200, 3) # h, w, channels

# model start here
model = Sequential()

model.add(BatchNormalization(epsilon=0.001, axis=1, input_shape=imgSize))

model.add(Conv2D(24, (5,5), padding='valid', activation='relu', strides=(2,2)))
model.add(Conv2D(36, (5,5), padding='valid', activation='relu', strides=(2,2)))
model.add(Conv2D(48, (5,5), padding='valid', activation='relu', strides=(2,2)))
model.add(Conv2D(64, (3,3), padding='valid', activation='relu', strides=(1,1)))
model.add(Conv2D(64, (3,3), padding='valid', activation='relu', strides=(1,1)))
model.add(Flatten())
model.add(Dense(100, activation='relu'))
model.add(Dense(50, activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(1, activation='tanh'))

model.summary()
# Save model to JSON
with open('autopilot_basic_model.json', 'w') as outfile:
    outfile.write(json.dumps(json.loads(model.to_json()), indent=2))
