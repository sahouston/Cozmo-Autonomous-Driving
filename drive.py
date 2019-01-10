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
from keras.optimizers import SGD, Adam, RMSprop
import sklearn.metrics as metrics

from keras.callbacks import ModelCheckpoint

import cv2
import numpy as np
import json
import pygame
import cozmo
from PIL import Image


import math
import h5py
import glob
from tqdm import tqdm
import scipy
from scipy import misc

imgSize = (128, 128)
speed = 75.0
#speed = 30.0

def run(sdk_conn):
    # load the model:
    model = Sequential()
    with open('autopilot_basic_model.json') as model_file:
        model = models.model_from_json(model_file.read())

    # load weights
    model.load_weights("weights/model_basic_weight.hdf5")

    adam = Adam(lr=0.0001)
    model.compile(loss='mse',
                  optimizer=adam,
                  metrics=['mse','accuracy'])

    # Prime Keras by making a first prediction
    steer = model.predict(np.zeros((1,3,128,128), dtype=np.float16))

    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    robot.set_lift_height(1.0, in_parallel=True)
    robot.set_head_angle(cozmo.robot.MIN_HEAD_ANGLE, in_parallel=True)

    screen = pygame.display.set_mode((640,480))

    # -------- Main Program Loop -----------
    run = True
    while run:
        steer = 0.0
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.QUIT:
                robot.stop_all_motors()
                run = False

        latest_image = robot.world.latest_image
        if latest_image is not None:            
            raw = latest_image.raw_image
            # Convert to pygame image and display in window
            py_image = pygame.image.fromstring(raw.tobytes(), raw.size, raw.mode)
            screen.blit(py_image, (0,0))
            pygame.display.flip() # update the display
            # Scale image
            scaled_img = raw.resize(imgSize, Image.BICUBIC)
            steer = model.predict(np.array(scaled_img, dtype=np.float16, ndmin=4).transpose((0,3,1,2))/255.)

        #print(steer)
        l_wheel_speed = speed + (steer * 75.0 * 2) # TODO: shouldn't need to * 2
        r_wheel_speed = speed - (steer * 75.0 * 2)
        robot.drive_wheel_motors(l_wheel_speed, r_wheel_speed, l_wheel_acc=500, r_wheel_acc=500)
        pygame.time.wait(100) # sleep
        
    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    cozmo.setup_basic_logging()
    try:
        cozmo.connect(run)
    except KeyboardInterrupt as e:
        pass
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
