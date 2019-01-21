import os

os.environ['KERAS_BACKEND'] = 'theano'
os.environ['THEANO_FLAGS']='mode=FAST_RUN,device=cuda0,floatX=float32,optimizer=None'

import keras.models as models
from keras.models import Sequential, Model
from keras.optimizers import SGD, Adam, RMSprop
from keras.callbacks import ModelCheckpoint

import autodrive_constants
import numpy as np
import glob

import matplotlib.pyplot as plt


imgSize = autodrive_constants.IMG_SIZE
imgs = np.zeros((0, imgSize[0], imgSize[1], imgSize[2]), dtype=np.float16)
targets = np.zeros(0, dtype=np.float32)

imgfiles = sorted(glob.glob('data_train/*-images.npz'))
steerfiles = sorted(glob.glob('data_train/*-steer.npz'))
for imgfile, steerfile in zip(imgfiles, steerfiles):
    imgs = np.append(imgs, np.load(imgfile)['img_arr'], axis=0)
    targets = np.append(targets, np.load(steerfile)['steer_arr'], axis=0)

print(f'Have {imgs.shape[0]} training images')

idx = 2000
imgplot = plt.imshow(imgs[idx,:].astype(np.float32))
print(f'steer: {targets[idx]}')
plt.show()

# Shuffle images and steering targets
idx = np.arange(0,imgs.shape[0])
idx = np.random.permutation(idx)
imgs = imgs[idx,:,:,:]
targets = targets[idx]

# load the model:
model = Sequential()
with open('autopilot_basic_model.json') as model_file:
    model = models.model_from_json(model_file.read())

# checkpoint
filepath="weights/weights.best.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
callbacks_list = [checkpoint]

adam = Adam(lr=0.0001)
model.compile(loss='mse',
              optimizer=adam,
              metrics=['mse','accuracy'])

epochs = 25
batch_size = 64

model.fit(imgs, targets, callbacks=callbacks_list,
	batch_size=batch_size, epochs=epochs, verbose=1,
	validation_split=0.1, shuffle=True)

model.save_weights('weights/model_basic_weight.hdf5')

