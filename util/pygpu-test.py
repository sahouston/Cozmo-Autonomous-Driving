import pygpu
import os

os.environ['DEVICE'] = 'cuda0'
pygpu.test()
